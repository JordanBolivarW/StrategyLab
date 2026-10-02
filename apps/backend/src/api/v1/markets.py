from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db_session
from src.models import Dataset
from src.schemas import MarketResponse, Candle

router = APIRouter()


# Predefined markets for MVP
MARKETS = [
    MarketResponse(symbol="BTCUSDT", name="Bitcoin / USDT", type="crypto", timeframes=["5m", "15m", "1h", "4h", "1D"]),
    MarketResponse(symbol="ETHUSDT", name="Ethereum / USDT", type="crypto", timeframes=["5m", "15m", "1h", "4h", "1D"]),
    MarketResponse(symbol="SPY", name="SPDR S&P 500 ETF", type="stock", timeframes=["5m", "15m", "1h", "4h", "1D"]),
    MarketResponse(symbol="EURUSD", name="Euro / US Dollar", type="forex", timeframes=["5m", "15m", "1h", "4h", "1D"]),
]


@router.get("", response_model=list[MarketResponse])
async def list_markets():
    return MARKETS


@router.get("/{symbol}", response_model=MarketResponse)
async def get_market(symbol: str):
    market = next((m for m in MARKETS if m.symbol == symbol), None)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/{symbol}/data")
async def get_market_data(
    symbol: str,
    timeframe: str = Query("1h"),
    start_date: str | None = Query(None),
    end_date: str | None = Query(None),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db_session),
):
    # Verify market exists
    market = next((m for m in MARKETS if m.symbol == symbol), None)
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")

    # TODO: Implement actual data loading from Parquet/MinIO
    # For now, return mock data
    from src.services.market_data import load_market_data

    try:
        data = await load_market_data(symbol, timeframe, start_date, end_date, limit)
        return {"symbol": symbol, "timeframe": timeframe, "candles": data}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Market data not found")


@router.post("/{symbol}/import")
async def import_market_data(
    symbol: str,
    timeframe: str,
    # TODO: Accept file upload (CSV/Parquet)
):
    # TODO: Implement data import
    return {"message": "Import endpoint - to be implemented"}