from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db_session
from src.models import Backtest
from src.schemas import BacktestCreate, BacktestResponse
from src.services import backtest_service

router = APIRouter()


def _to_response(run: Backtest) -> BacktestResponse:
    return BacktestResponse.model_validate(run)


@router.post("", response_model=BacktestResponse, status_code=status.HTTP_201_CREATED)
async def create_backtest(
    payload: BacktestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session),
):
    run = await backtest_service.create_backtest(db, payload)
    if run is None:
        raise HTTPException(status_code=404, detail="Strategy version not found")
    background_tasks.add_task(backtest_service.execute_backtest, db, run.id)
    return _to_response(run)


@router.get("", response_model=dict)
async def list_backtests(
    strategy_id: UUID | None = None,
    run_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db_session),
):
    if run_status is not None and run_status not in backtest_service.VALID_STATUSES:
        raise HTTPException(status_code=422, detail="Invalid status filter")
    items, total = await backtest_service.list_backtests(
        db, strategy_id=strategy_id, status=run_status, limit=limit, offset=offset
    )
    return {"items": [_to_response(r) for r in items], "total": total}


@router.get("/{backtest_id}", response_model=BacktestResponse)
async def get_backtest(backtest_id: UUID, db: AsyncSession = Depends(get_db_session)):
    run = await backtest_service.get_backtest(db, backtest_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return _to_response(run)


@router.delete("/{backtest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backtest(backtest_id: UUID, db: AsyncSession = Depends(get_db_session)):
    deleted = await backtest_service.delete_backtest(db, backtest_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
