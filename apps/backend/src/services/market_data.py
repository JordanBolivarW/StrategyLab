from datetime import datetime
from pathlib import Path
from typing import Any
import polars as pl


class MarketDataService:
    """Service for loading and managing market data"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    async def load_parquet(
        self,
        market: str,
        timeframe: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> pl.DataFrame:
        """Load market data from Parquet file"""
        file_path = self.data_dir / f"{market}_{timeframe}.parquet"

        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        df = pl.read_parquet(file_path)

        # Filter by date range
        if start_date:
            df = df.filter(pl.col("timestamp") >= start_date)
        if end_date:
            df = df.filter(pl.col("timestamp") <= end_date)

        return df.sort("timestamp")

    async def load_csv(
        self,
        file_path: str,
        timestamp_col: str = "timestamp",
    ) -> pl.DataFrame:
        """Load market data from CSV file"""
        df = pl.read_csv(file_path)

        # Ensure timestamp is datetime
        if timestamp_col in df.columns:
            df = df.with_columns(pl.col(timestamp_col).str.to_datetime())
            df = df.rename({timestamp_col: "timestamp"})

        # Ensure required columns
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        return df.sort("timestamp")

    async def save_parquet(self, df: pl.DataFrame, market: str, timeframe: str) -> Path:
        """Save market data to Parquet"""
        file_path = self.data_dir / f"{market}_{timeframe}.parquet"
        df.write_parquet(file_path)
        return file_path

    def list_available_data(self) -> list[dict]:
        """List all available data files"""
        files = []
        for file_path in self.data_dir.glob("*.parquet"):
            parts = file_path.stem.split("_")
            if len(parts) >= 2:
                market = parts[0]
                timeframe = "_".join(parts[1:])
                files.append({
                    "market": market,
                    "timeframe": timeframe,
                    "file": str(file_path),
                    "size_mb": file_path.stat().st_size / (1024 * 1024),
                })
        return files


async def load_market_data(
    market: str,
    timeframe: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int | None = None,
) -> pl.DataFrame:
    """Convenience function to load market data"""
    service = MarketDataService()

    try:
        df = await service.load_parquet(market, timeframe, start_date, end_date)
    except FileNotFoundError:
        # Generate mock data for development
        df = generate_mock_data(market, timeframe, start_date, end_date)

    if limit:
        df = df.tail(limit)

    return df


def generate_mock_data(
    market: str,
    timeframe: str,
    start_date: str | None = None,
    end_date: str | None = None,
    num_bars: int = 1000,
) -> pl.DataFrame:
    """Generate mock OHLCV data for testing"""
    import numpy as np

    # Base price by market
    base_prices = {
        "BTCUSDT": 50000,
        "ETHUSDT": 3000,
        "SPY": 450,
        "EURUSD": 1.08,
    }
    base_price = base_prices.get(market, 100)

    # Timeframe to minutes
    tf_minutes = {
        "5m": 5,
        "15m": 15,
        "1h": 60,
        "4h": 240,
        "1D": 1440,
    }
    minutes = tf_minutes.get(timeframe, 60)

    # Generate timestamps
    start = datetime.fromisoformat(start_date) if start_date else datetime(2024, 1, 1)
    timestamps = [start]
    for i in range(1, num_bars):
        from datetime import timedelta
        timestamps.append(timestamps[-1] + timedelta(minutes=minutes))

    # Generate prices using random walk
    np.random.seed(42)
    returns = np.random.normal(0, 0.02, num_bars)
    prices = base_price * np.exp(np.cumsum(returns))

    # Generate OHLCV
    data = []
    for i, (ts, close) in enumerate(zip(timestamps, prices)):
        high = close * (1 + abs(np.random.normal(0, 0.01)))
        low = close * (1 - abs(np.random.normal(0, 0.01)))
        open_price = prices[i-1] if i > 0 else close
        volume = abs(np.random.normal(1000000, 500000))

        data.append({
            "timestamp": ts,
            "open": open_price,
            "high": max(open_price, high, close),
            "low": min(open_price, low, close),
            "close": close,
            "volume": volume,
        })

    df = pl.DataFrame(data)
    return df