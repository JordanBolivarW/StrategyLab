from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from src.database import get_db_session
from src.models import Strategy, StrategyVersion, Backtest
from src.schemas import (
    BacktestCreate,
    BacktestResponse,
    BacktestConfig,
    BacktestMetrics,
    EquityPoint,
    Trade,
)
from src.services.backtest_engine import run_backtest

router = APIRouter()