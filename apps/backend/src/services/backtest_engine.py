from datetime import datetime
from typing import Any
import polars as pl
import numpy as np

from ..schemas import (
    BacktestConfig,
    BacktestMetrics,
    EquityPoint,
    Trade,
)
from .indicator_engine import IndicatorEngine, calculate_indicators
from .strategy_engine import StrategyEngine


class BacktestEngine:
    """Backtest execution engine"""

    def __init__(self):
        self.indicator_engine = IndicatorEngine()
        self.strategy_engine = StrategyEngine()

    async def run(
        self,
        strategy_graph: dict[str, Any],
        config: BacktestConfig,
        market_data: pl.DataFrame,
    ) -> dict[str, Any]:
        """Run backtest on market data"""
        # Validate strategy
        valid, errors = self.strategy_engine.validate_graph(
            self._dict_to_strategy_graph(strategy_graph)
        )
        if not valid:
            raise ValueError(f"Invalid strategy: {errors}")

        # Calculate indicators needed by strategy
        indicators_config = self._extract_indicators(strategy_graph)
        df = calculate_indicators(market_data, indicators_config)

        # Execute strategy
        signals = self._execute_strategy(df, strategy_graph)

        # Simulate trades
        trades, equity_curve = self._simulate_trades(
            df, signals, config
        )

        # Calculate metrics
        metrics = self._calculate_metrics(
            config.initial_capital,
            equity_curve,
            trades,
            market_data["close"].to_list(),
        )

        return {
            "metrics": metrics,
            "equity_curve": equity_curve,
            "trades": trades,
        }

    def _dict_to_strategy_graph(self, graph_dict: dict) -> Any:
        from ..schemas import StrategyGraph
        return StrategyGraph.model_validate(graph_dict)

    def _extract_indicators(self, graph: dict) -> list[dict]:
        """Extract indicator configurations from strategy graph"""
        indicators = []
        for node in graph.get("nodes", []):
            if node.get("type", "").startswith("indicator."):
                ind_type = node["type"].replace("indicator.", "")
                params = node.get("data", {})
                indicators.append({
                    "type": ind_type,
                    "name": f"{ind_type}_{node['id'][:8]}",
                    "params": params,
                })
        return indicators

    def _execute_strategy(self, df: pl.DataFrame, graph: dict) -> pl.Series:
        """Execute strategy graph on data to generate entry/exit signals"""
        node_map = {n["id"]: n for n in graph.get("nodes", [])}
        edges = graph.get("edges", [])

        # Build adjacency for execution order
        engine = StrategyEngine()
        strategy_graph = self._dict_to_strategy_graph(graph)
        try:
            exec_order = engine.get_execution_order(strategy_graph)
        except ValueError:
            exec_order = list(node_map.keys())

        # Store computed values for each node
        node_values = {}

        # Data series
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                node_values[col] = df[col]

        # Execute nodes in order
        for node_id in exec_order:
            node = node_map.get(node_id)
            if not node:
                continue

            node_type = node.get("type", "")
            data = node.get("data", {})

            try:
                if node_type.startswith("indicator."):
                    ind_type = node_type.replace("indicator.", "")
                    output = self.indicator_engine.compute_indicator(ind_type, df, **data)
                    if isinstance(output, dict):
                        for k, v in output.items():
                            node_values[f"{node_id}.{k}"] = v
                    else:
                        node_values[node_id] = output

                elif node_type.startswith("logic."):
                    logic_type = node_type.replace("logic.", "")
                    # Find input edges
                    in_edges = [e for e in edges if e["target"] == node_id]
                    if len(in_edges) >= 1:
                        a = node_values.get(in_edges[0]["source"])
                    if len(in_edges) >= 2:
                        b = node_values.get(in_edges[1]["source"])
                    else:
                        b = None

                    if a is not None:
                        result = self.indicator_engine.compute_logic(logic_type, a, b)
                        node_values[node_id] = result

                elif node_type in ("data.open", "data.high", "data.low", "data.close", "data.volume"):
                    col = node_type.replace("data.", "")
                    node_values[node_id] = df[col]

            except Exception:
                # On error, store null series
                node_values[node_id] = pl.Series([None] * len(df))

        # Find entry/exit signals
        entry_nodes = [n for n in graph.get("nodes", []) if n["type"] in ("action.buy", "action.long")]
        exit_nodes = [n for n in graph.get("nodes", []) if n["type"] in ("action.sell", "action.short", "action.close")]

        # For simplicity, use first entry node's output as signal
        entry_signal = pl.Series([False] * len(df))
        for node in entry_nodes:
            signal = node_values.get(node["id"])
            if signal is not None:
                entry_signal = entry_signal | signal.fill_null(False)

        exit_signal = pl.Series([False] * len(df))
        for node in exit_nodes:
            signal = node_values.get(node["id"])
            if signal is not None:
                exit_signal = exit_signal | signal.fill_null(False)

        # Combine: 1 = entry, -1 = exit, 0 = hold
        signals = pl.Series([0] * len(df))
        for i in range(len(df)):
            if entry_signal[i]:
                signals = signals[:i] + pl.Series([1]) + signals[i+1:]
            elif exit_signal[i]:
                signals = signals[:i] + pl.Series([-1]) + signals[i+1:]

        return signals

    def _simulate_trades(
        self,
        df: pl.DataFrame,
        signals: pl.Series,
        config: BacktestConfig,
    ) -> tuple[list[Trade], list[EquityPoint]]:
        """Simulate trade execution"""
        trades = []
        equity_curve = []

        capital = config.initial_capital
        position = 0
        entry_price = 0
        entry_time = None
        entry_idx = 0
        trade_id = 0

        close_prices = df["close"].to_list()
        timestamps = df["timestamp"].to_list() if "timestamp" in df.columns else list(range(len(df)))

        for i, signal in enumerate(signals):
            price = close_prices[i]
            timestamp = timestamps[i]

            # Update equity
            if position != 0:
                unrealized_pnl = position * (price - entry_price)
                current_equity = capital + unrealized_pnl
            else:
                current_equity = capital

            drawdown = 0
            if equity_curve:
                peak = max(e.equity for e in equity_curve)
                if peak > 0:
                    drawdown = (peak - current_equity) / peak * 100

            equity_curve.append(EquityPoint(
                timestamp=str(timestamp),
                equity=current_equity,
                drawdown_pct=drawdown,
            ))

            # Check exit conditions
            if position != 0 and signal == -1:
                # Exit position
                pnl = position * (price - entry_price)
                commission_cost = abs(position) * price * config.commission
                slippage_cost = abs(position) * price * config.slippage
                net_pnl = pnl - commission_cost - slippage_cost

                capital += net_pnl
                return_pct = (price - entry_price) / entry_price * 100 * (1 if position > 0 else -1)

                duration = i - entry_idx
                duration_str = f"{duration} bars"

                trades.append(Trade(
                    id=trade_id,
                    type="LONG" if position > 0 else "SHORT",
                    entry_time=str(entry_time),
                    exit_time=str(timestamp),
                    entry_price=entry_price,
                    exit_price=price,
                    quantity=abs(position),
                    return_pct=return_pct,
                    pnl=net_pnl,
                    reason_entry="Strategy signal",
                    reason_exit="Strategy signal",
                    duration=duration_str,
                ))

                trade_id += 1
                position = 0

            # Check entry conditions
            if position == 0 and signal == 1:
                # Enter position
                position_size = capital * 0.1  # 10% position size (simplified)
                quantity = position_size / price

                # Apply commission and slippage
                entry_price = price * (1 + config.slippage)
                commission_cost = quantity * price * config.commission
                capital -= commission_cost

                position = quantity
                entry_time = timestamp
                entry_idx = i

        return trades, equity_curve

    def _calculate_metrics(
        self,
        initial_capital: float,
        equity_curve: list[EquityPoint],
        trades: list[Trade],
        buy_hold_prices: list[float],
    ) -> BacktestMetrics:
        """Calculate performance metrics"""
        if not equity_curve:
            return BacktestMetrics(
                initial_capital=initial_capital,
                final_capital=initial_capital,
                return_pct=0,
                buy_hold_return_pct=0,
                max_drawdown_pct=0,
                total_trades=0,
                win_rate_pct=0,
                profit_factor=0,
                avg_trade_pct=0,
            )

        final_capital = equity_curve[-1].equity
        return_pct = (final_capital - initial_capital) / initial_capital * 100

        # Buy & hold
        if len(buy_hold_prices) > 1:
            buy_hold_return = (buy_hold_prices[-1] - buy_hold_prices[0]) / buy_hold_prices[0] * 100
        else:
            buy_hold_return = 0

        # Max drawdown
        max_dd = max(e.drawdown_pct for e in equity_curve) if equity_curve else 0

        # Trade metrics
        total_trades = len(trades)
        if total_trades > 0:
            wins = [t for t in trades if t.pnl > 0]
            losses = [t for t in trades if t.pnl <= 0]
            win_rate = len(wins) / total_trades * 100
            gross_profit = sum(t.pnl for t in wins)
            gross_loss = abs(sum(t.pnl for t in losses))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float("inf")
            avg_trade = sum(t.return_pct for t in trades) / total_trades
        else:
            win_rate = 0
            profit_factor = 0
            avg_trade = 0

        return BacktestMetrics(
            initial_capital=initial_capital,
            final_capital=final_capital,
            return_pct=return_pct,
            buy_hold_return_pct=buy_hold_return,
            max_drawdown_pct=max_dd,
            total_trades=total_trades,
            win_rate_pct=win_rate,
            profit_factor=profit_factor,
            avg_trade_pct=avg_trade,
        )


async def run_backtest(
    strategy_graph: dict[str, Any],
    config: BacktestConfig,
) -> dict[str, Any]:
    """Convenience function to run backtest"""
    # Load market data
    from .market_data import load_market_data
    market_data = await load_market_data(
        config.market,
        config.timeframe,
        config.start_date,
        config.end_date,
    )

    engine = BacktestEngine()
    return await engine.run(strategy_graph, config, market_data)