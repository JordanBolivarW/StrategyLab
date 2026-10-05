"""Single source of truth for strategy node types.

SPECS/strategy-graph.md §5 (R1): this registry feeds StrategyEngine and
(all future) MCP discovery handlers. Do not duplicate node type definitions
elsewhere.
"""

from typing import Any

# Action types that open a position (strategy entry points)
ENTRY_NODE_TYPES: set[str] = {"action.buy", "action.sell", "action.long", "action.short"}

# Action/risk types that close or bound a position (strategy exit points)
EXIT_NODE_TYPES: set[str] = {"action.close", "risk.stop_loss", "risk.take_profit"}


def _params(*specs: dict[str, Any]) -> list[dict[str, Any]]:
    return list(specs)


def _p(
    name: str,
    type: str,
    default: Any = None,
    min: float | None = None,
    max: float | None = None,
) -> dict[str, Any]:
    return {"name": name, "type": type, "default": default, "min": min, "max": max}


def _data_node(id: str, name: str) -> dict[str, Any]:
    return {
        "id": id,
        "name": name,
        "category": "data",
        "description": f"{name} series from market data",
        "inputs": {},
        "outputs": {"value": {"type": "series"}},
        "parameters": [],
    }


NODE_TYPES: dict[str, dict[str, Any]] = {
    # Data nodes (no inputs, single series output)
    "data.open": _data_node("data.open", "Open Price"),
    "data.high": _data_node("data.high", "High Price"),
    "data.low": _data_node("data.low", "Low Price"),
    "data.close": _data_node("data.close", "Close Price"),
    "data.volume": _data_node("data.volume", "Volume"),
    "data.timestamp": _data_node("data.timestamp", "Timestamp"),
    # Indicator nodes
    "indicator.sma": {
        "id": "indicator.sma",
        "name": "SMA",
        "category": "indicator",
        "description": "Simple Moving Average",
        "inputs": {"source": {"type": "series", "required": True}},
        "outputs": {"value": {"type": "series"}},
        "parameters": _params(_p("period", "int", default=20, min=2, max=500)),
    },
    "indicator.ema": {
        "id": "indicator.ema",
        "name": "EMA",
        "category": "indicator",
        "description": "Exponential Moving Average",
        "inputs": {"source": {"type": "series", "required": True}},
        "outputs": {"value": {"type": "series"}},
        "parameters": _params(_p("period", "int", default=20, min=2, max=500)),
    },
    "indicator.rsi": {
        "id": "indicator.rsi",
        "name": "RSI",
        "category": "indicator",
        "description": "Relative Strength Index",
        "inputs": {"source": {"type": "series", "required": True}},
        "outputs": {"value": {"type": "series"}},
        "parameters": _params(_p("period", "int", default=14, min=2, max=100)),
    },
    "indicator.macd": {
        "id": "indicator.macd",
        "name": "MACD",
        "category": "indicator",
        "description": "Moving Average Convergence Divergence",
        "inputs": {"source": {"type": "series", "required": True}},
        "outputs": {
            "macd": {"type": "series"},
            "signal": {"type": "series"},
            "histogram": {"type": "series"},
        },
        "parameters": _params(
            _p("fast", "int", default=12, min=2, max=100),
            _p("slow", "int", default=26, min=2, max=200),
            _p("signal", "int", default=9, min=2, max=50),
        ),
    },
    "indicator.atr": {
        "id": "indicator.atr",
        "name": "ATR",
        "category": "indicator",
        "description": "Average True Range",
        "inputs": {
            "high": {"type": "series", "required": True},
            "low": {"type": "series", "required": True},
            "close": {"type": "series", "required": True},
        },
        "outputs": {"value": {"type": "series"}},
        "parameters": _params(_p("period", "int", default=14, min=2, max=100)),
    },
    "indicator.bollinger_bands": {
        "id": "indicator.bollinger_bands",
        "name": "Bollinger Bands",
        "category": "indicator",
        "description": "Bollinger Bands (upper / middle / lower)",
        "inputs": {"source": {"type": "series", "required": True}},
        "outputs": {
            "upper": {"type": "series"},
            "middle": {"type": "series"},
            "lower": {"type": "series"},
        },
        "parameters": _params(
            _p("period", "int", default=20, min=2, max=200),
            _p("std_dev", "float", default=2.0, min=0.5, max=5.0),
        ),
    },
    # Comparator nodes
    "logic.gt": {
        "id": "logic.gt",
        "name": "Greater Than",
        "category": "comparator",
        "description": "True when A > B",
        "inputs": {
            "a": {"type": "series", "required": True},
            "b": {"type": "series", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.lt": {
        "id": "logic.lt",
        "name": "Less Than",
        "category": "comparator",
        "description": "True when A < B",
        "inputs": {
            "a": {"type": "series", "required": True},
            "b": {"type": "series", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.gte": {
        "id": "logic.gte",
        "name": "Greater Than or Equal",
        "category": "comparator",
        "description": "True when A >= B",
        "inputs": {
            "a": {"type": "series", "required": True},
            "b": {"type": "series", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.lte": {
        "id": "logic.lte",
        "name": "Less Than or Equal",
        "category": "comparator",
        "description": "True when A <= B",
        "inputs": {
            "a": {"type": "series", "required": True},
            "b": {"type": "series", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.cross_above": {
        "id": "logic.cross_above",
        "name": "Cross Above",
        "category": "comparator",
        "description": "True when A crosses above B",
        "inputs": {
            "a": {"type": "series", "required": True},
            "b": {"type": "series", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.cross_below": {
        "id": "logic.cross_below",
        "name": "Cross Below",
        "category": "comparator",
        "description": "True when A crosses below B",
        "inputs": {
            "a": {"type": "series", "required": True},
            "b": {"type": "series", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    # Logic nodes
    "logic.and": {
        "id": "logic.and",
        "name": "AND",
        "category": "logic",
        "description": "Boolean AND of A and B",
        "inputs": {
            "a": {"type": "boolean", "required": True},
            "b": {"type": "boolean", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.or": {
        "id": "logic.or",
        "name": "OR",
        "category": "logic",
        "description": "Boolean OR of A and B",
        "inputs": {
            "a": {"type": "boolean", "required": True},
            "b": {"type": "boolean", "required": True},
        },
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    "logic.not": {
        "id": "logic.not",
        "name": "NOT",
        "category": "logic",
        "description": "Boolean NOT of A",
        "inputs": {"a": {"type": "boolean", "required": True}},
        "outputs": {"result": {"type": "boolean"}},
        "parameters": [],
    },
    # Action nodes
    "action.buy": {
        "id": "action.buy",
        "name": "Buy",
        "category": "action",
        "description": "Open a long position when condition is true (entry)",
        "inputs": {"condition": {"type": "boolean", "required": True}},
        "outputs": {"signal": {"type": "boolean"}},
        "parameters": [],
    },
    "action.sell": {
        "id": "action.sell",
        "name": "Sell",
        "category": "action",
        "description": "Open a short position when condition is true (entry)",
        "inputs": {"condition": {"type": "boolean", "required": True}},
        "outputs": {"signal": {"type": "boolean"}},
        "parameters": [],
    },
    "action.long": {
        "id": "action.long",
        "name": "Long",
        "category": "action",
        "description": "Open a long position when condition is true (entry)",
        "inputs": {"condition": {"type": "boolean", "required": True}},
        "outputs": {"signal": {"type": "boolean"}},
        "parameters": [],
    },
    "action.short": {
        "id": "action.short",
        "name": "Short",
        "category": "action",
        "description": "Open a short position when condition is true (entry)",
        "inputs": {"condition": {"type": "boolean", "required": True}},
        "outputs": {"signal": {"type": "boolean"}},
        "parameters": [],
    },
    "action.close": {
        "id": "action.close",
        "name": "Close Position",
        "category": "action",
        "description": "Close the open position when condition is true (exit)",
        "inputs": {"condition": {"type": "boolean", "required": True}},
        "outputs": {"signal": {"type": "boolean"}},
        "parameters": [],
    },
    # Risk nodes
    "risk.position_size": {
        "id": "risk.position_size",
        "name": "Position Size",
        "category": "risk",
        "description": "Position size from risk percentage and equity",
        "inputs": {
            "risk_pct": {"type": "float", "required": False},
            "equity": {"type": "float", "required": False},
        },
        "outputs": {"size": {"type": "float"}},
        "parameters": _params(_p("risk_pct", "float", default=None, min=0.0, max=100.0)),
    },
    "risk.stop_loss": {
        "id": "risk.stop_loss",
        "name": "Stop Loss",
        "category": "risk",
        "description": "Stop loss price from entry and percentage (exit)",
        "inputs": {
            "entry": {"type": "float", "required": False},
            "pct": {"type": "float", "required": False},
        },
        "outputs": {"price": {"type": "float"}},
        "parameters": _params(_p("pct", "float", default=None, min=0.0, max=100.0)),
    },
    "risk.take_profit": {
        "id": "risk.take_profit",
        "name": "Take Profit",
        "category": "risk",
        "description": "Take profit price from entry and percentage (exit)",
        "inputs": {
            "entry": {"type": "float", "required": False},
            "pct": {"type": "float", "required": False},
        },
        "outputs": {"price": {"type": "float"}},
        "parameters": _params(_p("pct", "float", default=None, min=0.0, max=100.0)),
    },
}


def get_legacy_node_types() -> dict[str, dict[str, list[str]]]:
    """Node types in the legacy {category, inputs, outputs} shape.

    Used by StrategyEngine until all consumers move to full definitions.
    """
    return {
        type_id: {
            "category": definition["category"],
            "inputs": list(definition["inputs"].keys()),
            "outputs": list(definition["outputs"].keys()),
        }
        for type_id, definition in NODE_TYPES.items()
    }
