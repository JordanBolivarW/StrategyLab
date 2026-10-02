// Re-export shared types from @strategy-lab/shared
export * from '@strategy-lab/shared'

// Additional frontend-specific types
export interface StrategyResponse {
  id: string
  user_id: string
  name: string
  description: string | null
  market: string
  timeframe: string
  graph: StrategyGraph
  current_version: number
  created_at: string
  updated_at: string
}

export interface StrategyListResponse {
  items: StrategyResponse[]
  total: number
  page: number
  page_size: number
}

export interface StrategyCreate {
  name: string
  description?: string
  market: string
  timeframe: string
  graph: StrategyGraph
}

export interface StrategyUpdate {
  name?: string
  description?: string
  graph?: StrategyGraph
}

export interface StrategyGraph {
  nodes: StrategyNode[]
  edges: StrategyEdge[]
  metadata: Record<string, unknown>
}

export interface StrategyNode {
  id: string
  type: string
  position: { x: number; y: number }
  data: Record<string, unknown>
}

export interface StrategyEdge {
  id: string
  source: string
  target: string
  sourceHandle?: string
  targetHandle?: string
  animated?: boolean
}

export interface StrategyVersionResponse {
  id: string
  strategy_id: string
  version: number
  graph: StrategyGraph
  changelog: string | null
  created_by: string | null
  source: string | null
  client: string | null
  created_at: string
}

export interface BacktestConfig {
  strategy_id: string
  market: string
  timeframe: string
  start_date: string
  end_date: string
  initial_capital: number
  commission: number
  slippage: number
}

export interface BacktestCreate {
  strategy_version_id: string
  config: BacktestConfig
}

export interface BacktestResponse {
  id: string
  strategy_id: string
  strategy_version_id: string
  config: BacktestConfig
  status: string
  metrics: BacktestMetrics | null
  equity_curve: { points: EquityPoint[] } | null
  trades: { trades: Trade[] } | null
  error: string | null
  started_at: string | null
  completed_at: string | null
  created_at: string
}

export interface BacktestMetrics {
  initial_capital: number
  final_capital: number
  return_pct: number
  buy_hold_return_pct: number
  max_drawdown_pct: number
  total_trades: number
  win_rate_pct: number
  profit_factor: number
  avg_trade_pct: number
  sharpe_ratio: number | null
  sortino_ratio: number | null
  calmar_ratio: number | null
}

export interface EquityPoint {
  timestamp: string
  equity: number
  drawdown_pct: number
}

export interface Trade {
  id: number
  type: string
  entry_time: string
  exit_time: string
  entry_price: number
  exit_price: number
  quantity: number
  return_pct: number
  pnl: number
  reason_entry: string
  reason_exit: string
  duration: string
}

export interface MarketResponse {
  symbol: string
  name: string
  type: string
  timeframes: string[]
}

export interface Candle {
  timestamp: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface MCPTool {
  name: string
  description: string
  inputSchema: Record<string, unknown>
}

export interface MCPToolCall {
  name: string
  arguments: Record<string, unknown>
}

export interface MCPToolResult {
  content: Array<{ type: string; text: string }>
  isError: boolean
}