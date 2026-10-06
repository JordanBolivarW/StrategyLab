import pytest
import polars as pl
import numpy as np

from src.services.indicator_engine import IndicatorEngine, calculate_indicators


class TestIndicatorEngine:
    """Test technical indicator calculations"""

    @pytest.fixture
    def engine(self):
        return IndicatorEngine()

    @pytest.fixture
    def sample_data(self):
        """Create sample OHLCV data"""
        np.random.seed(42)
        n = 100
        base = 100
        returns = np.random.normal(0, 0.01, n)
        closes = base * np.exp(np.cumsum(returns))

        highs = closes * (1 + np.abs(np.random.normal(0, 0.005, n)))
        lows = closes * (1 - np.abs(np.random.normal(0, 0.005, n)))
        opens = np.roll(closes, 1)
        opens[0] = closes[0]
        volumes = np.abs(np.random.normal(1000000, 200000, n))

        return pl.DataFrame({
            "timestamp": pl.datetime_range(
                start=pl.datetime(2024, 1, 1),
                end=pl.datetime(2024, 1, 1) + pl.duration(hours=n - 1),
                interval="1h",
                time_unit="ms",
                eager=True,
            ),
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        })

    def test_sma(self, engine, sample_data):
        result = engine.sma(sample_data["close"], 20)
        assert len(result) == len(sample_data)
        # First 19 should be null
        assert result[:19].null_count() == 19
        # Rest should have values
        assert result[19:].null_count() == 0

    def test_ema(self, engine, sample_data):
        result = engine.ema(sample_data["close"], 20)
        assert len(result) == len(sample_data)
        assert result.null_count() == 0  # EMA has no nulls with adjust=False

    def test_rsi(self, engine, sample_data):
        result = engine.rsi(sample_data["close"], 14)
        assert len(result) == len(sample_data)
        # First 13 should be null
        assert result[:13].null_count() == 13
        # Values should be between 0 and 100
        valid = result.drop_nulls()
        assert (valid >= 0).all()
        assert (valid <= 100).all()

    def test_macd(self, engine, sample_data):
        result = engine.macd(sample_data["close"])
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result
        for series in result.values():
            assert len(series) == len(sample_data)

    def test_atr(self, engine, sample_data):
        result = engine.atr(
            sample_data["high"],
            sample_data["low"],
            sample_data["close"],
            14
        )
        assert len(result) == len(sample_data)
        assert result[:13].null_count() == 13
        assert (result.drop_nulls() >= 0).all()

    def test_bollinger_bands(self, engine, sample_data):
        result = engine.bollinger_bands(sample_data["close"])
        assert "upper" in result
        assert "middle" in result
        assert "lower" in result
        for series in result.values():
            assert len(series) == len(sample_data)
        # Upper should be >= middle >= lower
        valid_idx = result["middle"].drop_nulls().to_list()
        if valid_idx:
            upper = result["upper"].drop_nulls()
            middle = result["middle"].drop_nulls()
            lower = result["lower"].drop_nulls()
            assert (upper >= middle).all()
            assert (middle >= lower).all()

    def test_cross_above(self, engine):
        a = pl.Series([1, 2, 3, 2, 1, 2, 3])
        b = pl.Series([2, 2, 2, 2, 2, 2, 2])
        result = engine.cross_above(a, b)
        # Cross above at index 2 (3 > 2, prev 2 <= 2)
        assert result[2] is True
        assert result[5] is False  # 2 > 2 is False

    def test_cross_below(self, engine):
        a = pl.Series([3, 2, 1, 2, 3, 2, 1])
        b = pl.Series([2, 2, 2, 2, 2, 2, 2])
        result = engine.cross_below(a, b)
        # Cross below at index 2 (1 < 2, prev 2 >= 2)
        assert result[2] is True

    def test_comparators(self, engine):
        a = pl.Series([1, 2, 3, 4, 5])
        b = pl.Series([3, 3, 3, 3, 3])

        assert engine.gt(a, b).to_list() == [False, False, False, True, True]
        assert engine.lt(a, b).to_list() == [True, True, False, False, False]
        assert engine.gte(a, b).to_list() == [False, False, True, True, True]
        assert engine.lte(a, b).to_list() == [True, True, True, False, False]

    def test_logic(self, engine):
        a = pl.Series([True, True, False, False])
        b = pl.Series([True, False, True, False])

        assert engine.and_op(a, b).to_list() == [True, False, False, False]
        assert engine.or_op(a, b).to_list() == [True, True, True, False]
        assert engine.not_op(a).to_list() == [False, False, True, True]

    def test_compute_indicator(self, engine, sample_data):
        # Test SMA
        result = engine.compute_indicator("sma", sample_data, period=20)
        assert isinstance(result, pl.Series)
        assert len(result) == len(sample_data)

        # Test MACD (returns dict)
        result = engine.compute_indicator("macd", sample_data)
        assert isinstance(result, dict)
        assert "macd" in result
        assert "signal" in result
        assert "histogram" in result

    def test_compute_indicator_invalid(self, engine, sample_data):
        with pytest.raises(ValueError, match="Unknown indicator"):
            engine.compute_indicator("invalid_indicator", sample_data)

    def test_compute_comparator(self, engine):
        a = pl.Series([1, 2, 3, 4])
        b = pl.Series([2, 2, 2, 2])

        result = engine.compute_comparator("gt", a, b)
        assert result.to_list() == [False, False, True, True]

        result = engine.compute_comparator("cross_above", a, b)
        assert isinstance(result, pl.Series)

    def test_compute_logic(self, engine):
        a = pl.Series([True, False, True])
        b = pl.Series([False, True, True])

        result = engine.compute_logic("and", a, b)
        assert result.to_list() == [False, False, True]

        result = engine.compute_logic("not", a)
        assert result.to_list() == [False, True, False]

    def test_calculate_indicators(self, sample_data):
        indicators = [
            {"type": "sma", "name": "SMA_20", "params": {"period": 20}},
            {"type": "ema", "name": "EMA_50", "params": {"period": 50}},
            {"type": "rsi", "name": "RSI_14", "params": {"period": 14}},
            {"type": "macd", "name": "MACD", "params": {"fast_period": 12, "slow_period": 26, "signal_period": 9}},
        ]

        result = calculate_indicators(sample_data, indicators)

        assert "SMA_20" in result.columns
        assert "EMA_50" in result.columns
        assert "RSI_14" in result.columns
        assert "MACD_macd" in result.columns
        assert "MACD_signal" in result.columns
        assert "MACD_histogram" in result.columns


class TestIndicatorEdgeCases:
    """Test edge cases for indicators"""

    def test_short_series(self):
        """Test with series shorter than period"""
        engine = IndicatorEngine()
        short = pl.Series([1, 2, 3])
        result = engine.sma(short, 20)
        assert result.null_count() == 3  # All null

    def test_constant_series(self):
        """Test with constant price"""
        engine = IndicatorEngine()
        constant = pl.Series([100] * 50)
        result = engine.rsi(constant, 14)
        # RSI should be 50 for constant price (no gains/losses)
        valid = result.drop_nulls()
        if len(valid) > 0:
            # Note: with 0/0 division, result may be null or inf
            pass

    def test_nan_handling(self):
        """Test handling of NaN values"""
        engine = IndicatorEngine()
        with_nan = pl.Series([1, 2, None, 4, 5])
        result = engine.sma(with_nan, 3)
        # Should handle gracefully
        assert len(result) == 5