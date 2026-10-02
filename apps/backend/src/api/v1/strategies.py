from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload

from src.database import get_db_session
from src.models import Strategy, StrategyVersion
from src.schemas import (
    StrategyCreate,
    StrategyUpdate,
    StrategyResponse,
    StrategyListResponse,
    StrategyGraph,
    StrategyVersionResponse,
)

router = APIRouter()