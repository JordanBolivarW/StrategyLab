import pytest
from datetime import datetime
from uuid import uuid4

from strategy_lab_shared.schemas import (
    StrategyNode,
    StrategyEdge,
    StrategyGraph,
    StrategyNodeType,
    StrategyCategory,
    BacktestConfig,
    BacktestMetrics,
    BacktestStatus,
    Market,
    MarketType,
    Timeframe,
    Candle,
    IndicatorDefinition,
    IndicatorParameter,
    BUILT_IN_INDICATORS,
    get_indicator_by_id,
    validate_indicator_params,
    get_default_params,
    merge_params,
)


class TestStrategySchemas:
    """Test Strategy-related schemas"""

    def test_strategy_node_creation(self):
        node = StrategyNode(
            id=uuid4(),
            type=StrategyNodeType.DATA_CLOSE,
            position={"x": 100, "y": 200},
            data={"source": "close"},
        )
        assert node.type == StrategyNodeType.DATA_CLOSE
        assert node.position.x == 100
        assert node.position.y == 200

    def test_strategy_edge_creation(self):
        source_id = uuid4()
        target_id = uuid4()
        edge = StrategyEdge(
            id=uuid4(),
            source=source_id,
            target=target_id,
            sourceHandle="output",
            targetHandle="input",
        )
        assert edge.source == source_id
        assert edge.target == target_id

    def test_strategy_graph_validation(self):
        # Valid graph
        graph = StrategyGraph(
            nodes=[
                StrategyNode(type=StrategyNodeType.DATA_CLOSE, position={"x": 0, "y": 0}),
                StrategyNode(type=StrategyNodeType.INDICATOR_EMA, position={"x": 200, "y": 0}, data={"period": 20}),
                StrategyNode(type=StrategyNodeType.ACTION_BUY, position={"x": 400, "y": 0}),
            ],
            edges=[
                StrategyEdge(source=uuid4(), target=uuid4()),
                StrategyEdge(source=uuid4(), target=uuid4()),
            ],
        )
        assert len(graph.nodes) == 3
        assert len(graph.edges) == 2

    def test_strategy_graph_rejects_empty(self):
        with pytest.raises(ValueError):
            StrategyGraph(nodes=[], edges=[])

        with pytest.raises(ValueError):
            StrategyGraph(nodes=[StrategyNode(type=StrategyNodeType.DATA_CLOSE, position={"x": 0, "y": 0})], edges=[])


class TestBacktestSchemas:
    """Test Backtest-related schemas"""

    def test_backtest_config_valid(self):
        config = BacktestConfig(
            strategy_id=uuid4(),
            market="BTCUSDT",
            timeframe="1h",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 12, 31),
            initial_capital=10000,
            commission=0.001,
            slippage=0.0005,
        )
        assert config.market == "BTCUSDT"
        assert config.initial_capital == 10000

    def test_backtest_config_invalid_dates(self):
        with pytest.raises(ValueError):
            BacktestConfig(
                strategy_id=uuid4(),
                market="BTCUSDT",
                timeframe="1h",
                start_date=datetime(2024, 12, 31),
                end_date=datetime(2024, 1, 1),
            )

    def test_backtest_config_invalid_commission(self):
        with pytest.raises(ValueError):
            BacktestConfig(
                strategy_id=uuid4(),
                market="BTCUSDT",
                timeframe="1h",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 12, 31),
                commission=1.5,
            )

    def test_backtest_metrics(self):
        metrics = BacktestMetrics(
            initial_capital=10000,
            final_capital=13800,
            return_pct=38.0,
            buy_hold_return_pct=45.0,
            max_drawdown_pct=11.3,
            total_trades=143,
            win_rate_pct=54.2,
            profit_factor=1.72,
            avg_trade_pct=0.87,
            sharpe_ratio=1.45,
        )
        assert metrics.return_pct == 38.0
        assert metrics.total_trades == 143


class TestMarketSchemas:
    """Test Market-related schemas"""

    def test_market_creation(self):
        market = Market(
            symbol="BTCUSDT",
            name="Bitcoin / USDT",
            type=MarketType.CRYPTO,
            exchange="Binance",
            base_currency="BTC",
            quote_currency="USDT",
        )
        assert market.symbol == "BTCUSDT"
        assert market.type == MarketType.CRYPTO

    def test_candle_creation(self):
        candle = Candle(
            timestamp=datetime(2024, 1, 1, 12, 0),
            open=50000,
            high=51000,
            low=49500,
            close=50500,
            volume=1000000,
        )
        assert candle.close == 50500
        assert candle.high > candle.low


class TestIndicatorSchemas:
    """Test Indicator-related schemas"""

    def test_builtin_indicators(self):
        assert len(BUILT_IN_INDICATORS) == 6
        ids = [i.id for i in BUILT_IN_INDICATORS]
        assert "sma" in ids
        assert "ema" in ids
        assert "rsi" in ids
        assert "macd" in ids
        assert "atr" in ids
        assert "bollinger_bands" in ids

    def test_indicator_definition(self):
        sma = get_indicator_by_id("sma")
        assert sma is not None
        assert sma.id == "sma"
        assert sma.name == "Simple Moving Average"
        assert sma.category == IndicatorCategory.TREND
        assert len(sma.parameters) == 1
        assert sma.parameters[0].name == "period"
        assert sma.parameters[0].default == 20

    def test_get_indicators_by_category(self):
        trend_indicators = get_indicators_by_category(IndicatorCategory.TREND)
        assert len(trend_indicators) == 2  # SMA, EMA
        assert all(i.category == IndicatorCategory.TREND for i in trend_indicators)

    def test_validate_indicator_params_valid(self):
        valid, errors = validate_indicator_params("sma", {"period": 20})
        assert valid
        assert len(errors) == 0

        valid, errors = validate_indicator_params("macd", {"fast_period": 12, "slow_period": 26, "signal_period": 9})
        assert valid

    def test_validate_indicator_params_invalid(self):
        valid, errors = validate_indicator_params("sma", {"period": "invalid"})
        assert not valid
        assert any("integer" in e for e in errors)

        valid, errors = validate_indicator_params("sma", {"period": 1})  # below min
        assert not valid

        valid, errors = validate_indicator_params("sma", {"period": 1000})  # above max
        assert not valid

    def test_get_default_params(self):
        sma_params = get_default_params("sma")
        assert sma_params == {"period": 20}

        macd_params = get_default_params("macd")
        assert macd_params == {"fast_period": 12, "slow_period": 26, "signal_period": 9}

    def test_merge_params(self):
        merged = merge_params("sma", {"period": 50})
        assert merged == {"period": 50}

        merged = merge_params("macd", {"fast_period": 8})
        assert merged == {"fast_period": 8, "slow_period": 26, "signal_period": 9}