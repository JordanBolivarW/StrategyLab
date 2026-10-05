"""Strategy CRUD endpoints.

Thin routes over src.services.strategy_service (AGENTS.md: no direct DB
access from routes). Graph semantics: SPECS/strategy-graph.md §§8-11.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.schemas import (
    StrategyCreate,
    StrategyListResponse,
    StrategyResponse,
    StrategyUpdate,
    StrategyVersionResponse,
)
from src.services import strategy_service

router = APIRouter()


async def _get_or_404(session: AsyncSession, strategy_id: UUID):
    strategy = await strategy_service.get_strategy(session, strategy_id)
    if strategy is None:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.get("", response_model=StrategyListResponse)
async def list_strategies(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session),
):
    items, total = await strategy_service.list_strategies(db, page=page, page_size=page_size)
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("", response_model=StrategyResponse, status_code=status.HTTP_201_CREATED)
async def create_strategy(
    payload: StrategyCreate,
    db: AsyncSession = Depends(get_db_session),
):
    return await strategy_service.create_strategy(db, payload)


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    return await _get_or_404(db, strategy_id)


@router.patch("/{strategy_id}", response_model=StrategyResponse)
async def update_strategy(
    strategy_id: UUID,
    payload: StrategyUpdate,
    db: AsyncSession = Depends(get_db_session),
):
    strategy = await _get_or_404(db, strategy_id)
    return await strategy_service.update_strategy(db, strategy, payload)


@router.delete("/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_strategy(
    strategy_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    strategy = await _get_or_404(db, strategy_id)
    await strategy_service.delete_strategy(db, strategy)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{strategy_id}/versions", response_model=list[StrategyVersionResponse])
async def get_strategy_versions(
    strategy_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    await _get_or_404(db, strategy_id)
    return await strategy_service.list_versions(db, strategy_id)


@router.post(
    "/{strategy_id}/clone",
    response_model=StrategyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def clone_strategy(
    strategy_id: UUID,
    name: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
):
    strategy = await _get_or_404(db, strategy_id)
    return await strategy_service.clone_strategy(db, strategy, name=name)


@router.post("/{strategy_id}/validate")
async def validate_strategy(
    strategy_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    strategy = await _get_or_404(db, strategy_id)
    return strategy_service.validate_strategy(strategy)
