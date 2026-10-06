"""Backtest runs: persistence + execution (service layer).

Routes in api/v1/backtests.py stay thin; MCP (phase 6) reuses this module.
Spec: SPECS/backtesting-engine.md
"""

from datetime import datetime, timezone
from uuid import UUID

import structlog
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Backtest, StrategyVersion
from ..schemas import BacktestConfig, BacktestCreate
from .backtest_engine import BacktestEngine
from .market_data import load_market_data

log = structlog.get_logger()

VALID_STATUSES = ("pending", "running", "completed", "failed")

TERMINAL_STATUSES = ("completed", "failed")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def create_backtest(db: AsyncSession, payload: BacktestCreate) -> Backtest | None:
    """Persist a run as pending. Returns None when the version does not exist.

    config.strategy_id is canonicalized from the version (§3.5 of the spec).
    """
    version = await db.get(StrategyVersion, payload.strategy_version_id)
    if version is None:
        return None

    config = payload.config.model_copy(update={"strategy_id": version.strategy_id})
    run = Backtest(
        strategy_id=version.strategy_id,
        strategy_version_id=version.id,
        config=config.model_dump(mode="json"),
        status="pending",
    )
    db.add(run)
    await db.commit()
    await db.refresh(run)
    log.info("backtest_created", backtest_id=str(run.id))
    return run


async def get_backtest(db: AsyncSession, backtest_id: UUID) -> Backtest | None:
    return await db.get(Backtest, backtest_id)


async def list_backtests(
    db: AsyncSession,
    strategy_id: UUID | None = None,
    status: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Backtest], int]:
    stmt = select(Backtest).order_by(desc(Backtest.created_at))
    count_stmt = select(func.count()).select_from(Backtest)
    if strategy_id is not None:
        stmt = stmt.where(Backtest.strategy_id == strategy_id)
        count_stmt = count_stmt.where(Backtest.strategy_id == strategy_id)
    if status is not None:
        stmt = stmt.where(Backtest.status == status)
        count_stmt = count_stmt.where(Backtest.status == status)
    total = (await db.execute(count_stmt)).scalar_one()
    items = (await db.execute(stmt.limit(limit).offset(offset))).scalars().all()
    return list(items), total


async def delete_backtest(db: AsyncSession, backtest_id: UUID) -> bool:
    run = await db.get(Backtest, backtest_id)
    if run is None:
        return False
    await db.delete(run)
    await db.commit()
    return True


async def execute_backtest(db: AsyncSession, backtest_id: UUID) -> Backtest | None:
    """Run the engine for a stored run; never raises (failed stored instead)."""
    run = await db.get(Backtest, backtest_id)
    if run is None:
        return None
    if run.status in TERMINAL_STATUSES:
        return run

    run.status = "running"
    run.started_at = _utcnow()
    await db.commit()

    try:
        version = await db.get(StrategyVersion, run.strategy_version_id)
        if version is None:
            raise ValueError("Strategy version no longer exists")
        config = BacktestConfig(**run.config)
        market_data = await load_market_data(
            config.market, config.timeframe, config.start_date, config.end_date
        )
        result = BacktestEngine().run(version.graph, config, market_data)

        run.metrics = result["metrics"].model_dump(mode="json")
        run.equity_curve = [p.model_dump(mode="json") for p in result["equity_curve"]]
        run.trades = [t.model_dump(mode="json") for t in result["trades"]]
        run.status = "completed"
        run.completed_at = _utcnow()
        await db.commit()
        log.info("backtest_completed", backtest_id=str(run.id))
    except Exception as exc:  # noqa: BLE001 — stored, never raised (spec §6.7)
        await db.rollback()
        run = await db.get(Backtest, backtest_id)
        if run is None:
            return None
        run.status = "failed"
        run.error = str(exc)[:2000]
        run.completed_at = _utcnow()
        await db.commit()
        log.exception("backtest_failed", backtest_id=str(backtest_id))

    await db.refresh(run)
    return run
