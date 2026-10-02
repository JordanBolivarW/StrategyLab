import pytest
import polars as pl
from datetime import timedelta

from src.services.backtest_engine import BacktestEngine
from src.services.strategy_engine import StrategyEngine
from src.schemas import BacktestConfig


class TestBacktestEngine:
    """Test backtest engine"""

    @pytest.fixture
    def engine(self):
        return BacktestEngine()

    @pytest.fixture
    def sample_strategy(self):
        """Simple EMA crossover strategy"""
        return {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "indicator.ema", "position": {"x": 200, "y": 0}, "data": {"period": 20}},
                {"id": "3", "type": "indicator.ema", "position": {"x": 200, "y": 100}, "data": {"period": 50}},
                {"id": "4", "type": "logic.cross_above", "position": {"x": 400, "y": 50}, "data": {}},
                {"id": "5", "type": "action.buy", "position": {"x": 600, "y": 50}, "data": {}},
                {"id": "6", "type": "action.close", "position": {"x": 600, "y": 150}, "data": {}},
            ],
            "edges": [
                {"id": "e1", "source": "1", "target": "2"},
                {"id": "e2", "source": "1", "target": "3"},
                {"id": "e3", "source": "2", "target": "4", "sourceHandle": "value", "targetHandle": "a"},
                {"id": "e4", "source": "3", "target": "4", "sourceHandle": "value", "targetHandle": "b"},
                {"id": "e5", "source": "4", "target": "5", "sourceHandle": "result", "targetHandle": "condition"},
                {"id": "e6", "source": "4", "target": "6", "sourceHandle": "result", "targetHandle": "condition"},
            ],
            "metadata": {},
        }

    @pytest.fixture
    def market_data(self):
        """Generate trending market data"""
        import numpy as np
        np.random.seed(42)
        n = 500
        # Create uptrend
        trend = np.linspace(100, 150, n)
        noise = np.random.normal(0, 2, n)
        closes = trend + noise

        highs = closes + np.abs(np.random.normal(0, 1, n))
        lows = closes - np.abs(np.random.normal(0, 1, n))
        opens = np.roll(closes, 1)
        opens[0] = closes[0]
        volumes = np.abs(np.random.normal(1000000, 200000, n))

        return pl.DataFrame({
            "timestamp": pl.datetime_range(
                start=pl.datetime(2024, 1, 1),
                end=pl.datetime(2024, 1, 1) + pl.duration(hours=n-1),
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

    @pytest.fixture
    def config(self):
        return BacktestConfig(
            strategy_id="test",
            market="BTCUSDT",
            timeframe="1h",
            start_date="2024-01-01",
            end_date="2024-06-01",
            initial_capital=10000,
            commission=0.001,
            slippage=0.0005,
        )

    def test_run_backtest(self, engine, sample_strategy, market_data, config):
        result = engine.run(sample_strategy, config, market_data)

        assert "metrics" in result
        assert "equity_curve" in result
        assert "trades" in result

        metrics = result["metrics"]
        assert isinstance(metrics.initial_capital, float)
        assert isinstance(metrics.final_capital, float)
        assert isinstance(metrics.return_pct, float)
        assert isinstance(metrics.max_drawdown_pct, float)
        assert isinstance(metrics.total_trades, int)
        assert isinstance(metrics.win_rate_pct, float)
        assert isinstance(metrics.profit_factor, float)

        equity_curve = result["equity_curve"]
        assert isinstance(equity_curve, list)
        assert len(equity_curve) == len(market_data)

        trades = result["trades"]
        assert isinstance(trades, list)

    def test_run_backtest_invalid_strategy(self, engine, market_data, config):
        invalid_strategy = {
            "nodes": [],
            "edges": [],
            "metadata": {},
        }

        with pytest.raises(ValueError, match="Invalid strategy"):
            engine.run(invalid_strategy, config, market_data)

    def test_equity_curve_properties(self, engine, sample_strategy, market_data, config):
        result = engine.run(sample_strategy, config, market_data)
        equity_curve = result["equity_curve"]

        # First equity should be initial capital
        assert equity_curve[0].equity == config.initial_capital
        # All equity values should be positive
        assert all(e.equity > 0 for e in equity_curve)
        # Drawdown should be >= 0
        assert all(e.drawdown_pct >= 0 for e in equity_curve)

    def test_trade_properties(self, engine, sample_strategy, market_data, config):
        result = engine.run(sample_strategy, config, market_data)
        trades = result["trades"]

        for trade in trades:
            assert trade.id >= 0
            assert trade.type in ("LONG", "SHORT")
            assert trade.entry_price > 0
            assert trade.exit_price > 0
            assert trade.quantity > 0
            assert isinstance(trade.return_pct, float)
            assert isinstance(trade.pnl, float)


class TestStrategyEngineIntegration:
    """Test strategy engine with backtest"""

    def test_strategy_validation(self):
        engine = StrategyEngine()

        # Valid strategy
        valid_graph = {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "indicator.sma", "position": {"x": 200, "y": 0}, "data": {"period": 20}},
                {"id": "3", "type": "action.buy", "position": {"x": 400, "y": 0}, "data": {}},
            ],
            "edges": [
                {"id": "e1", "source": "1", "target": "2"},
                {"id": "e2", "source": "2", "target": "3"},
            ],
            "metadata": {},
        }

        valid, errors = engine.validate_graph(engine._dict_to_strategy_graph(valid_graph))
        assert valid
        assert len(errors) == 0

    def test_strategy_validation_no_nodes(self):
        engine = StrategyEngine()
        invalid_graph = {"nodes": [], "edges": [], "metadata": {}}
        valid, errors = engine.validate_graph(engine._dict_to_strategy_graph(invalid_graph))
        assert not valid
        assert "at least one node" in errors[0]

    def test_strategy_validation_no_entry(self):
        engine = StrategyEngine()
        # Has exit but no entry
        invalid_graph = {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "action.close", "position": {"x": 200, "y": 0}, "data": {}},
            ],
            "edges": [{"id": "e1", "source": "1", "target": "2"}],
            "metadata": {},
        }
        valid, errors = engine.validate_graph(engine._dict_to_strategy_graph(invalid_graph))
        assert not valid
        assert any("entry node" in e for e in errors)

    def test_strategy_validation_no_exit(self):
        engine = StrategyEngine()
        # Has entry but no exit
        invalid_graph = {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "action.buy", "position": {"x": 200, "y": 0}, "data": {}},
            ],
            "edges": [{"id": "e1", "source": "1", "target": "2"}],
            "metadata": {},
        }
        valid, errors = engine.validate_graph(engine._dict_to_strategy_graph(invalid_graph))
        assert not valid
        assert any("exit node" in e for e in errors)

    def test_execution_order(self):
        engine = StrategyEngine()
        graph = {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "indicator.sma", "position": {"x": 200, "y": 0}, "data": {"period": 20}},
                {"id": "3", "type": "action.buy", "position": {"x": 400, "y": 0}, "data": {}},
            ],
            "edges": [
                {"id": "e1", "source": "1", "target": "2"},
                {"id": "e2", "source": "2", "target": "3"},
            ],
            "metadata": {},
        }

        strategy_graph = engine._dict_to_strategy_graph(graph)
        order = engine.get_execution_order(strategy_graph)

        # Data node should come first, then indicator, then action
        assert order.index("1") < order.index("2")
        assert order.index("2") < order.index("3")

    def test_cycle_detection(self):
        engine = StrategyEngine()
        cyclic_graph = {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "indicator.sma", "position": {"x": 200, "y": 0}, "data": {"period": 20}},
            ],
            "edges": [
                {"id": "e1", "source": "1", "target": "2"},
                {"id": "e2", "source": "2", "target": "1"},  # Cycle!
            ],
            "metadata": {},
        }

        strategy_graph = engine._dict_to_strategy_graph(cyclic_graph)
        valid, errors = engine.validate_graph(strategy_graph)
        assert not valid
        assert any("cycle" in e.lower() for e in errors)

    def test_explain_strategy(self):
        engine = StrategyEngine()
        graph = {
            "nodes": [
                {"id": "1", "type": "data.close", "position": {"x": 0, "y": 0}, "data": {}},
                {"id": "2", "type": "indicator.ema", "position": {"x": 200, "y": 0}, "data": {"period": 20}},
                {"id": "3", "type": "indicator.ema", "position": {"x": 200, "y": 100}, "data": {"period": 50}},
                {"id": "4", "type": "logic.cross_above", "position": {"x": 400, "y": 50}, "data": {}},
                {"id": "5", "type": "action.buy", "position": {"x": 600, "y": 50}, "data": {}},
                {"id": "6", "type": "risk.position_size", "position": {"x": 600, "y": 150}, "data": {"risk_pct": 1}},
                {"id": "7", "type": "risk.stop_loss", "position": {"x": 600, "y": 200}, "data": {"pct": 2}},
            ],
            "edges": [
                {"id": "e1", "source": "1", "target": "2"},
                {"id": "e2", "source": "1", "target": "3"},
                {"id": "e3", "source": "2", "target": "4", "sourceHandle": "value", "targetHandle": "a"},
                {"id": "e4", "source": "3", "target": "4", "sourceHandle": "value", "targetHandle": "b"},
                {"id": "e5", "source": "4", "target": "5", "sourceHandle": "result", "targetHandle": "condition"},
                {"id": "e6", "source": "5", "target": "6"},
                {"id": "e7", "source": "5", "target": "7"},
            ],
            "metadata": {},
        }

        explanation = engine.explain_strategy(engine._dict_to_strategy_graph(graph))
        assert "ENTRY" in explanation
        assert "POSITION MANAGEMENT" in explanation
        assert "BUY" in explanation
        assert "EMA" in explanation