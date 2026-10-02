import polars as pl
import numpy as np
from typing import Any


class IndicatorEngine:
    """Technical indicator calculations using Polars and NumPy"""

    @staticmethod
    def sma(series: pl.Series, period: int) -> pl.Series:
        """Simple Moving Average"""
        return series.rolling_mean(window_size=period, min_periods=period)

    @staticmethod
    def ema(series: pl.Series, period: int) -> pl.Series:
        """Exponential Moving Average"""
        return series.ewm_mean(span=period, min_periods=period)

    @staticmethod
    def rsi(series: pl.Series, period: int = 14) -> pl.Series:
        """Relative Strength Index"""
        delta = series.diff()
        gain = delta.clip(lower_bound=0)
        loss = -delta.clip(upper_bound=0)

        avg_gain = gain.rolling_mean(window_size=period, min_periods=period)
        avg_loss = loss.rolling_mean(window_size=period, min_periods=period)

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def macd(
        series: pl.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ) -> dict[str, pl.Series]:
        """Moving Average Convergence Divergence"""
        ema_fast = IndicatorEngine.ema(series, fast_period)
        ema_slow = IndicatorEngine.ema(series, slow_period)

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm_mean(span=signal_period, min_periods=signal_period)
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram,
        }

    @staticmethod
    def atr(high: pl.Series, low: pl.Series, close: pl.Series, period: int = 14) -> pl.Series:
        """Average True Range"""
        prev_close = close.shift(1)

        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()

        true_range = pl.max_horizontal(tr1, tr2, tr3)
        atr = true_range.rolling_mean(window_size=period, min_periods=period)

        return atr

    @staticmethod
    def bollinger_bands(
        series: pl.Series,
        period: int = 20,
        std_dev: float = 2.0,
    ) -> dict[str, pl.Series]:
        """Bollinger Bands"""
        middle = series.rolling_mean(window_size=period, min_periods=period)
        std = series.rolling_std(window_size=period, min_periods=period, ddof=0)

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        return {
            "upper": upper,
            "middle": middle,
            "lower": lower,
        }

    @staticmethod
    def cross_above(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Returns True when A crosses above B"""
        prev_a = series_a.shift(1)
        prev_b = series_b.shift(1)
        return (prev_a <= prev_b) & (series_a > series_b)

    @staticmethod
    def cross_below(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Returns True when A crosses below B"""
        prev_a = series_a.shift(1)
        prev_b = series_b.shift(1)
        return (prev_a >= prev_b) & (series_a < series_b)

    @staticmethod
    def gt(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Greater than"""
        return series_a > series_b

    @staticmethod
    def lt(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Less than"""
        return series_a < series_b

    @staticmethod
    def gte(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Greater than or equal"""
        return series_a >= series_b

    @staticmethod
    def lte(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Less than or equal"""
        return series_a <= series_b

    @staticmethod
    def and_op(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Logical AND"""
        return series_a & series_b

    @staticmethod
    def or_op(series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Logical OR"""
        return series_a | series_b

    @staticmethod
    def not_op(series: pl.Series) -> pl.Series:
        """Logical NOT"""
        return ~series

    def compute_indicator(self, indicator_type: str, df: pl.DataFrame, **params) -> pl.Series | dict[str, pl.Series]:
        """Compute indicator by type"""
        close = df["close"]
        high = df["high"]
        low = df["low"]

        match indicator_type:
            case "sma":
                period = params.get("period", 20)
                return self.sma(close, period)
            case "ema":
                period = params.get("period", 20)
                return self.ema(close, period)
            case "rsi":
                period = params.get("period", 14)
                return self.rsi(close, period)
            case "macd":
                fast = params.get("fast_period", 12)
                slow = params.get("slow_period", 26)
                signal = params.get("signal_period", 9)
                return self.macd(close, fast, slow, signal)
            case "atr":
                period = params.get("period", 14)
                return self.atr(high, low, close, period)
            case "bollinger_bands":
                period = params.get("period", 20)
                std = params.get("std_dev", 2.0)
                return self.bollinger_bands(close, period, std)
            case _:
                raise ValueError(f"Unknown indicator: {indicator_type}")

    def compute_comparator(self, comparator_type: str, series_a: pl.Series, series_b: pl.Series) -> pl.Series:
        """Compute comparator by type"""
        match comparator_type:
            case "cross_above":
                return self.cross_above(series_a, series_b)
            case "cross_below":
                return self.cross_below(series_a, series_b)
            case "gt":
                return self.gt(series_a, series_b)
            case "lt":
                return self.lt(series_a, series_b)
            case "gte":
                return self.gte(series_a, series_b)
            case "lte":
                return self.lte(series_a, series_b)
            case _:
                raise ValueError(f"Unknown comparator: {comparator_type}")

    def compute_logic(self, logic_type: str, series_a: pl.Series, series_b: pl.Series | None = None) -> pl.Series:
        """Compute logic operation by type"""
        match logic_type:
            case "and":
                if series_b is None:
                    raise ValueError("AND requires two series")
                return self.and_op(series_a, series_b)
            case "or":
                if series_b is None:
                    raise ValueError("OR requires two series")
                return self.or_op(series_a, series_b)
            case "not":
                return self.not_op(series_a)
            case _:
                raise ValueError(f"Unknown logic: {logic_type}")


def calculate_indicators(df: pl.DataFrame, indicators_config: list[dict]) -> pl.DataFrame:
    """Calculate multiple indicators and add as columns"""
    engine = IndicatorEngine()
    result = df.clone()

    for config in indicators_config:
        ind_type = config["type"]
        name = config.get("name", ind_type)
        params = config.get("params", {})

        try:
            output = engine.compute_indicator(ind_type, result, **params)

            if isinstance(output, dict):
                for key, series in output.items():
                    col_name = f"{name}_{key}" if len(output) > 1 else name
                    result = result.with_columns(series.alias(col_name))
            else:
                result = result.with_columns(output.alias(name))

        except Exception as e:
            # Add null column on error
            result = result.with_columns(pl.lit(None).alias(name))

    return result