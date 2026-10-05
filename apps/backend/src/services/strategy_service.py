"""Strategy CRUD + versioning service.

Service layer shared by the REST API and MCP (AGENTS.md: no direct DB
access from routes). Graph semantics: SPECS/strategy-graph.md §§8-11.
"""

from copy import deepcopy
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Strategy, StrategyVersion
from ..schemas import StrategyCreate, StrategyGraph, StrategyUpdate
from .strategy_engine import StrategyEngine


async def list_strategies(
    session: AsyncSession, page: int = 1, page_size: int = 20
) -> tuple[list[Strategy], int]:
    """List strategies newest-first with total count."""
    total = (await session.execute(select(func.count()).select_from(Strategy))).scalar_one()
    result = await session.execute(
        select(Strategy)
        .order_by(Strategy.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    return list(result.scalars().all()), total


async def get_strategy(session: AsyncSession, strategy_id: UUID) -> Strategy | None:
    """Get a strategy by id, or None."""
    return await session.get(Strategy, strategy_id)


async def _snapshot(
    session: AsyncSession,
    strategy: Strategy,
    changelog: str,
    created_by: str = "user",
    source: str = "api",
) -> StrategyVersion:
    """Append a version row for the strategy's current graph (V1, V2)."""
    version = StrategyVersion(
        strategy_id=strategy.id,
        version=strategy.current_version,
        graph=deepcopy(strategy.graph),
        changelog=changelog,
        created_by=created_by,
        source=source,
    )
    session.add(version)
    await session.flush()
    return version


async def create_strategy(session: AsyncSession, payload: StrategyCreate) -> Strategy:
    """Create a strategy with its version-1 snapshot (V4).

    Semantic graph validity is NOT required: drafts are storable
    (SPECS/strategy-graph.md §10). Owner is NULL until auth exists (U2).
    """
    strategy = Strategy(
        user_id=None,
        name=payload.name,
        description=payload.description,
        market=payload.market,
        timeframe=payload.timeframe,
        graph=payload.graph.model_dump(mode="json"),
        current_version=1,
    )
    session.add(strategy)
    await session.flush()
    await _snapshot(session, strategy, changelog="Initial version")
    await session.commit()
    await session.refresh(strategy)
    return strategy


async def update_strategy(
    session: AsyncSession, strategy: Strategy, payload: StrategyUpdate
) -> Strategy:
    """Apply a patch; any change appends a new version (V2, decision A)."""
    changed: list[str] = []
    if payload.name is not None and payload.name != strategy.name:
        strategy.name = payload.name
        changed.append("name")
    if payload.description is not None and payload.description != strategy.description:
        strategy.description = payload.description
        changed.append("description")
    if payload.graph is not None:
        strategy.graph = payload.graph.model_dump(mode="json")
        changed.append("graph")

    if not changed:
        return strategy

    strategy.current_version += 1
    if "graph" in changed:
        changelog = "graph updated"
    else:
        changelog = f"metadata updated: {', '.join(changed)}"
    await session.flush()
    await _snapshot(session, strategy, changelog=changelog)
    await session.commit()
    await session.refresh(strategy)
    return strategy


async def delete_strategy(session: AsyncSession, strategy: Strategy) -> None:
    """Delete a strategy; versions cascade (V6)."""
    await session.delete(strategy)
    await session.commit()


async def clone_strategy(
    session: AsyncSession, strategy: Strategy, name: str | None = None
) -> Strategy:
    """Deep-copy a strategy into a new one at version 1 (V5)."""
    clone = Strategy(
        user_id=strategy.user_id,
        name=name or f"{strategy.name} (copy)",
        description=strategy.description,
        market=strategy.market,
        timeframe=strategy.timeframe,
        graph=deepcopy(strategy.graph),
        current_version=1,
    )
    session.add(clone)
    await session.flush()
    await _snapshot(session, clone, changelog=f"Cloned from '{strategy.name}'")
    await session.commit()
    await session.refresh(clone)
    return clone


async def list_versions(session: AsyncSession, strategy_id: UUID) -> list[StrategyVersion]:
    """List version rows oldest-first."""
    result = await session.execute(
        select(StrategyVersion)
        .where(StrategyVersion.strategy_id == strategy_id)
        .order_by(StrategyVersion.version.asc())
    )
    return list(result.scalars().all())


def validate_strategy(strategy: Strategy) -> dict:
    """Validate the stored graph without persisting anything (§10)."""
    graph = StrategyGraph.model_validate(strategy.graph)
    engine = StrategyEngine()
    valid, errors = engine.validate_graph(graph)
    return {
        "valid": valid,
        "errors": errors,
        "node_count": len(graph.nodes),
        "edge_count": len(graph.edges),
    }
