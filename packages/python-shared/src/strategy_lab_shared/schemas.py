"""Pydantic schemas for Strategy Lab MCP - matching TypeScript shared types"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator


# Enums
class StrategyNodeType(str, Enum):
    # Data
    DATA_OPEN = "data.open"
    DATA_HIGH = "data.high"
    DATA_LOW = "data.low"
    DATA_CLOSE = "data.close"
    DATA_VOLUME = "data.volume"
    DATA_TIMESTAMP = "data.timestamp"
    # Indicators
    INDICATOR_SMA = "indicator.sma"
    INDICATOR_EMA = "indicator.ema"
    INDICATOR_RSI = "indicator.rsi"
    INDICATOR_MACD = "indicator.macd"
    INDICATOR_ATR = "indicator.atr"
    INDICATOR_BOLLINGER_BANDS = "indicator.bollinger_bands"
    # Comparators
    LOGIC_GT = "logic.gt"
    LOGIC_LT = "logic.lt"
    LOGIC_GTE = "logic.gte"
    LOGIC_LTE = "logic.lte"
    LOGIC_CROSS_ABOVE = "logic.cross_above"
    LOGIC_CROSS_BELOW = "logic.cross_below"
    # Logic
    LOGIC_AND = "logic.and"
    LOGIC_OR = "logic.or"
    LOGIC_NOT = "logic.not"
    # Actions
    ACTION_BUY = "action.buy"
    ACTION_SELL = "action.sell"
    ACTION_LONG = "action.long"
    ACTION_SHORT = "action.short"
    ACTION_CLOSE = "action.close"
    # Risk
    RISK_POSITION_SIZE = "risk.position_size"
    RISK_STOP_LOSS = "risk.stop_loss"
    RISK_TAKE_PROFIT = "risk.take_profit"


class StrategyCategory(str, Enum):
    DATA = "data"
    INDICATOR = "indicator"
    COMPARATOR = "comparator"
    LOGIC = "logic"
    ACTION = "action"
    RISK = "risk"
    TIME = "time"
    MATH = "math"


class IndicatorCategory(str, Enum):
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    OTHER = "other"


class MarketType(str, Enum):
    CRYPTO = "crypto"
    STOCK = "stock"
    FOREX = "forex"
    COMMODITY = "commodity"
    INDEX = "index"
    ETF = "etf"
    FUTURE = "future"
    OPTION = "option"


class Timeframe(str, Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    H6 = "6h"
    H8 = "8h"
    H12 = "12h"
    D1 = "1D"
    W1 = "1W"
    M1_MONTH = "1M"


class BacktestStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Base Models
class Position(BaseModel):
    x: float
    y: float


class StrategyNode(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    type: StrategyNodeType
    position: Position
    data: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)


class StrategyEdge(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    source: UUID
    target: UUID
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)


class StrategyGraph(BaseModel):
    nodes: list[StrategyNode] = Field(min_length=1)
    edges: list[StrategyEdge] = Field(min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(use_enum_values=True)


class StrategyMetadata(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    market: str = Field(min_length=1, max_length=50)
    timeframe: str = Field(min_length=1, max_length=20)
    created_by: str = Field(default="user")
    source: str = Field(default="web")
    client: Optional[str] = None


class StrategyVersion(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    strategy_id: UUID
    version: int = Field(gt=0)
    graph: StrategyGraph
    changelog: Optional[str] = None
    created_by: Optional[str] = None
    source: Optional[str] = None
    client: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)


# Backtest Models
class BacktestConfig(BaseModel):
    strategy_id: UUID
    market: str = Field(min_length=1, max_length=50)
    timeframe: str = Field(min_length=1, max_length=20)
    start_date: datetime
    end_date: datetime
    initial_capital: float = Field(default=10000.0, gt=0)
    commission: float = Field(default=0.001, ge=0, le=1)
    slippage: float = Field(default=0.0005, ge=0, le=1)

    @field_validator("end_date")
    @classmethod
    def end_after_start(cls, v: datetime, info) -> datetime:
        if info.data.get("start_date") and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class BacktestMetrics(BaseModel):
    initial_capital: float
    final_capital: float
    return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float
    total_trades: int = Field(ge=0)
    win_rate_pct: float
    profit_factor: float
    avg_trade_pct: float
    avg_win_pct: Optional[float] = None
    avg_loss_pct: Optional[float] = None
    max_consecutive_wins: Optional[int] = Field(default=None, ge=0)
    max_consecutive_losses: Optional[int] = Field(default=None, ge=0)
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None
    expectancy: Optional[float] = None
    recovery_factor: Optional[float] = None


class EquityPoint(BaseModel):
    timestamp: datetime
    equity: float
    drawdown_pct: float


class Trade(BaseModel):
    id: int = Field(gt=0)
    type: str = Field(pattern="^(LONG|SHORT)$")
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    quantity: float
    return_pct: float
    pnl: float
    reason_entry: str
    reason_exit: str
    duration: str
    fees: Optional[float] = None
    slippage: Optional[float] = None


class BacktestResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    strategy_id: UUID
    strategy_version_id: UUID
    config: BacktestConfig
    status: BacktestStatus = BacktestStatus.PENDING
    metrics: Optional[BacktestMetrics] = None
    equity_curve: Optional[list[EquityPoint]] = None
    trades: Optional[list[Trade]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(use_enum_values=True)


# Market Models
class Market(BaseModel):
    symbol: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    type: MarketType
    exchange: Optional[str] = None
    base_currency: Optional[str] = None
    quote_currency: Optional[str] = None
    timeframes: list[str] = Field(default=["5m", "15m", "1h", "4h", "1D"])
    min_tick: Optional[float] = None
    lot_size: Optional[float] = None

    model_config = ConfigDict(use_enum_values=True)


class Candle(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class Dataset(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    market: str
    timeframe: str
    source: Optional[str] = None
    start_date: datetime
    end_date: datetime
    row_count: Optional[int] = Field(default=None, gt=0)
    file_path: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Indicator Models
class IndicatorParameter(BaseModel):
    name: str
    type: str = Field(pattern="^(integer|number|string|boolean|select)$")
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None
    min: Optional[float] = None
    max: Optional[float] = None
    options: Optional[list[str]] = None


class IndicatorInput(BaseModel):
    name: str
    type: str = Field(pattern="^(series|value)$")
    description: Optional[str] = None
    default: Optional[str] = None


class IndicatorOutput(BaseModel):
    name: str
    type: str = Field(pattern="^(series|value)$")
    description: Optional[str] = None


class IndicatorDefinition(BaseModel):
    id: str
    name: str
    category: IndicatorCategory
    description: str
    inputs: list[IndicatorInput] = Field(default_factory=list)
    parameters: list[IndicatorParameter] = Field(default_factory=list)
    outputs: list[IndicatorOutput] = Field(default_factory=list)

    model_config = ConfigDict(use_enum_values=True)


# Built-in Indicators
BUILT_IN_INDICATORS: list[IndicatorDefinition] = [
    IndicatorDefinition(
        id="sma",
        name="Simple Moving Average",
        category=IndicatorCategory.TREND,
        description="Simple moving average of a price series",
        inputs=[IndicatorInput(name="source", type="series", default="close", description="Price series to average")],
        parameters=[IndicatorParameter(name="period", type="integer", min=2, max=500, default=20, description="Number of periods")],
        outputs=[IndicatorOutput(name="value", type="series", description="SMA values")],
    ),
    IndicatorDefinition(
        id="ema",
        name="Exponential Moving Average",
        category=IndicatorCategory.TREND,
        description="Exponential moving average of a price series",
        inputs=[IndicatorInput(name="source", type="series", default="close", description="Price series to average")],
        parameters=[IndicatorParameter(name="period", type="integer", min=2, max=500, default=20, description="Number of periods")],
        outputs=[IndicatorOutput(name="value", type="series", description="EMA values")],
    ),
    IndicatorDefinition(
        id="rsi",
        name="Relative Strength Index",
        category=IndicatorCategory.MOMENTUM,
        description="Momentum oscillator measuring speed and change of price movements",
        inputs=[IndicatorInput(name="source", type="series", default="close", description="Price series")],
        parameters=[IndicatorParameter(name="period", type="integer", min=2, max=100, default=14, description="Number of periods")],
        outputs=[IndicatorOutput(name="value", type="series", description="RSI values (0-100)")],
    ),
    IndicatorDefinition(
        id="macd",
        name="Moving Average Convergence Divergence",
        category=IndicatorCategory.MOMENTUM,
        description="Trend-following momentum indicator showing relationship between two EMAs",
        inputs=[IndicatorInput(name="source", type="series", default="close", description="Price series")],
        parameters=[
            IndicatorParameter(name="fast_period", type="integer", min=2, max=50, default=12, description="Fast EMA period"),
            IndicatorParameter(name="slow_period", type="integer", min=2, max=100, default=26, description="Slow EMA period"),
            IndicatorParameter(name="signal_period", type="integer", min=2, max=50, default=9, description="Signal line period"),
        ],
        outputs=[
            IndicatorOutput(name="macd", type="series", description="MACD line"),
            IndicatorOutput(name="signal", type="series", description="Signal line"),
            IndicatorOutput(name="histogram", type="series", description="MACD histogram"),
        ],
    ),
    IndicatorDefinition(
        id="atr",
        name="Average True Range",
        category=IndicatorCategory.VOLATILITY,
        description="Measures market volatility by decomposing the entire range of an asset price",
        inputs=[
            IndicatorInput(name="high", type="series", description="High prices"),
            IndicatorInput(name="low", type="series", description="Low prices"),
            IndicatorInput(name="close", type="series", description="Close prices"),
        ],
        parameters=[IndicatorParameter(name="period", type="integer", min=2, max=100, default=14, description="Number of periods")],
        outputs=[IndicatorOutput(name="value", type="series", description="ATR values")],
    ),
    IndicatorDefinition(
        id="bollinger_bands",
        name="Bollinger Bands",
        category=IndicatorCategory.VOLATILITY,
        description="Volatility bands placed above and below a moving average",
        inputs=[IndicatorInput(name="source", type="series", default="close", description="Price series")],
        parameters=[
            IndicatorParameter(name="period", type="integer", min=2, max=100, default=20, description="Moving average period"),
            IndicatorParameter(name="std_dev", type="number", min=0.5, max=5, default=2, description="Standard deviation multiplier"),
        ],
        outputs=[
            IndicatorOutput(name="upper", type="series", description="Upper band"),
            IndicatorOutput(name="middle", type="series", description="Middle band (SMA)"),
            IndicatorOutput(name="lower", type="series", description="Lower band"),
        ],
    ),
]


# MCP Models
class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: dict[str, Any]


class MCPToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]


class MCPToolResult(BaseModel):
    content: list[dict[str, str]]
    isError: bool = False


class PlatformCapabilities(BaseModel):
    markets: list[Market]
    indicators: list[IndicatorDefinition]
    max_strategy_nodes: int = 100
    max_strategy_edges: int = 200
    max_backtest_bars: int = 100000
    supported_timeframes: list[str] = Field(default=["5m", "15m", "1h", "4h", "1D"])
    features: dict[str, bool] = Field(default_factory=lambda: {
        "versioning": True,
        "experiments": False,
        "optimization": False,
        "walk_forward": False,
        "monte_carlo": False,
    })

    model_config = ConfigDict(use_enum_values=True)