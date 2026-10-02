from fastapi import APIRouter

from .v1 import strategies, backtests, markets, mcp

api_router = APIRouter()
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(backtests.router, prefix="/backtests", tags=["backtests"])
api_router.include_router(markets.router, prefix="/markets", tags=["markets"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])