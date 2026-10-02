import { z } from 'zod'

// Backtest Config
export const BacktestConfigSchema = z.object({
  strategy_id: z.string().uuid(),
  market: z.string().min(1).max(50),
  timeframe: z.string().min(1).max(20),
  start_date: z.string().datetime(),
  end_date: z.string().datetime(),
  initial_capital: z.number().positive().default(10000),
  commission: z.number().min(0).max(1).default(0.001),
  slippage: z.number().min(0).max(1).default(0.0005),
  position_sizing: z.object({
    type: z.enum(['fixed', 'percent', 'risk']),
    value: z.number().positive(),
  }).optional(),
  stop_loss: z.number().min(0).max(1).optional(),
  take_profit: z.number().min(0).max(1).optional(),
})

export type BacktestConfig = z.infer<typeof BacktestConfigSchema>

// Backtest Status
export const BacktestStatusSchema = z.enum(['pending', 'running', 'completed', 'failed'])

export type BacktestStatus = z.infer<typeof BacktestStatusSchema>

// Backtest Metrics
export const BacktestMetricsSchema = z.object({
  initial_capital: z.number(),
  final_capital: z.number(),
  return_pct: z.number(),
  buy_hold_return_pct: z.number(),
  max_drawdown_pct: z.number(),
  total_trades: z.number().int().nonnegative(),
  win_rate_pct: z.number(),
  profit_factor: z.number(),
  avg_trade_pct: z.number(),
  avg_win_pct: z.number().optional(),
  avg_loss_pct: z.number().optional(),
  max_consecutive_wins: z.number().int().nonnegative().optional(),
  max_consecutive_losses: z.number().int().nonnegative().optional(),
  sharpe_ratio: z.number().optional(),
  sortino_ratio: z.number().optional(),
  calmar_ratio: z.number().optional(),
  expectancy: z.number().optional(),
  recovery_factor: z.number().optional(),
})

export type BacktestMetrics = z.infer<typeof BacktestMetricsSchema>

// Equity Point
export const EquityPointSchema = z.object({
  timestamp: z.string().datetime(),
  equity: z.number(),
  drawdown_pct: z.number(),
})

export type EquityPoint = z.infer<typeof EquityPointSchema>

// Trade
export const TradeSchema = z.object({
  id: z.number().int().positive(),
  type: z.enum(['LONG', 'SHORT']),
  entry_time: z.string().datetime(),
  exit_time: z.string().datetime(),
  entry_price: z.number(),
  exit_price: z.number(),
  quantity: z.number(),
  return_pct: z.number(),
  pnl: z.number(),
  reason_entry: z.string(),
  reason_exit: z.string(),
  duration: z.string(),
  fees: z.number().optional(),
  slippage: z.number().optional(),
})

export type Trade = z.infer<typeof TradeSchema>

// Backtest Result
export const BacktestResultSchema = z.object({
  id: z.string().uuid(),
  strategy_id: z.string().uuid(),
  strategy_version_id: z.string().uuid(),
  config: BacktestConfigSchema,
  status: BacktestStatusSchema,
  metrics: BacktestMetricsSchema.optional(),
  equity_curve: z.array(EquityPointSchema).optional(),
  trades: z.array(TradeSchema).optional(),
  error: z.string().optional(),
  started_at: z.string().datetime().optional(),
  completed_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
})

export type BacktestResult = z.infer<typeof BacktestResultSchema>

// Comparison
export const ComparisonResultSchema = z.object({
  strategies: z.array(z.object({
    strategy_id: z.string().uuid(),
    name: z.string(),
    version: z.number().int().positive(),
    metrics: BacktestMetricsSchema,
  })),
  best_by_return: z.string().uuid(),
  best_by_sharpe: z.string().uuid().optional(),
  best_by_drawdown: z.string().uuid().optional(),
})

export type ComparisonResult = z.infer<typeof ComparisonResultSchema>