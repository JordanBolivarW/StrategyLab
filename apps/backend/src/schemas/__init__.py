from datetime import datetime
from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


# User
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Strategy
class StrategyGraphNode(BaseModel):
    id: str
    type: str
    position: dict[str, float]
    data: dict[str, Any]


class StrategyGraphEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None


class StrategyGraph(BaseModel):
    nodes: list[StrategyGraphNode]
    edges: list[StrategyGraphEdge]
    metadata: dict[str, Any] = Field(default_factory=dict)


class StrategyBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    market: str = Field(min_length=1, max_length=50)
    timeframe: str = Field(min_length=1, max_length=20)
    graph: StrategyGraph


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    graph: Optional[StrategyGraph] = None


class StrategyResponse(StrategyBase):
    id: UUID
    # Optional until auth exists (SPECS/strategy-graph.md §11 U3)
    user_id: Optional[UUID]
    current_version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StrategyListResponse(BaseModel):
    items: list[StrategyResponse]
    total: int
    page: int
    page_size: int


# Strategy Version
class StrategyVersionResponse(BaseModel):
    id: UUID
    strategy_id: UUID
    version: int
    graph: StrategyGraph
    changelog: Optional[str] = None
    created_by: Optional[str] = None
    source: Optional[str] = None
    client: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Backtest
class BacktestConfig(BaseModel):
    strategy_id: UUID
    market: str
    timeframe: str
    start_date: str  # ISO format
    end_date: str
    initial_capital: float = Field(gt=0, default=10000.0)
    commission: float = Field(ge=0, le=1, default=0.001)
    slippage: float = Field(ge=0, le=1, default=0.0005)


class BacktestCreate(BaseModel):
    strategy_version_id: UUID
    config: BacktestConfig


class BacktestMetrics(BaseModel):
    initial_capital: float
    final_capital: float
    return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float
    total_trades: int
    win_rate_pct: float
    profit_factor: float
    avg_trade_pct: float
    sharpe_ratio: Optional[float] = None
    sortino_ratio: Optional[float] = None
    calmar_ratio: Optional[float] = None


class EquityPoint(BaseModel):
    timestamp: str
    equity: float
    drawdown_pct: float


class Trade(BaseModel):
    id: int
    type: str  # LONG, SHORT
    entry_time: str
    exit_time: str
    entry_price: float
    exit_price: float
    quantity: float
    return_pct: float
    pnl: float
    reason_entry: str
    reason_exit: str
    duration: str


class BacktestResponse(BaseModel):
    id: UUID
    strategy_id: UUID
    strategy_version_id: UUID
    config: BacktestConfig
    status: str
    metrics: Optional[BacktestMetrics] = None
    equity_curve: Optional[list[EquityPoint]] = None
    trades: Optional[list[Trade]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Market
class MarketResponse(BaseModel):
    symbol: str
    name: str
    type: str  # crypto, stock, forex
    timeframes: list[str]


class Candle(BaseModel):
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float


# MCP
class MCPTool(BaseModel):
    name: str
    description: str
    inputSchema: dict


class MCPToolCall(BaseModel):
    name: str
    arguments: dict


class MCPToolResult(BaseModel):
    content: list[dict]
    isError: bool = False