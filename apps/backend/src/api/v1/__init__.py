from fastapi import APIRouter

from . import strategies, backtests, markets, mcp

v1_router = APIRouter()
v1_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
v1_router.include_router(backtests.router, prefix="/backtests", tags=["backtests"])
v1_router.include_router(markets.router, prefix="/markets", tags=["markets"])
v1_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])