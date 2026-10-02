import { z } from 'zod'

// Market Types
export const MarketTypeSchema = z.enum(['crypto', 'stock', 'forex', 'commodity', 'index', 'etf', 'future', 'option'])

export type MarketType = z.infer<typeof MarketTypeSchema>

// Market Definition
export const MarketSchema = z.object({
  symbol: z.string().min(1).max(50),
  name: z.string().min(1).max(255),
  type: MarketTypeSchema,
  exchange: z.string().optional(),
  base_currency: z.string().optional(),
  quote_currency: z.string().optional(),
  timeframes: z.array(z.string()).default(['5m', '15m', '1h', '4h', '1D']),
  min_tick: z.number().optional(),
  lot_size: z.number().optional(),
  trading_hours: z.object({
    timezone: z.string(),
    open: z.string(),
    close: z.string(),
    days: z.array(z.enum(['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'])),
  }).optional(),
})

export type Market = z.infer<typeof MarketSchema>

// Timeframe
export const TimeframeSchema = z.enum(['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1D', '1W', '1M'])

export type Timeframe = z.infer<typeof TimeframeSchema>

// OHLCV Candle
export const CandleSchema = z.object({
  timestamp: z.string().datetime(),
  open: z.number(),
  high: z.number(),
  low: z.number(),
  close: z.number(),
  volume: z.number(),
})

export type Candle = z.infer<typeof CandleSchema>

// Market Data Query
export const MarketDataQuerySchema = z.object({
  market: z.string(),
  timeframe: TimeframeSchema,
  start_date: z.string().datetime().optional(),
  end_date: z.string().datetime().optional(),
  limit: z.number().int().positive().max(10000).default(1000),
})

export type MarketDataQuery = z.infer<typeof MarketDataQuerySchema>

// Market Data Response
export const MarketDataResponseSchema = z.object({
  market: z.string(),
  timeframe: z.string(),
  candles: z.array(CandleSchema),
  next_cursor: z.string().optional(),
})

export type MarketDataResponse = z.infer<typeof MarketDataResponseSchema>

// Predefined Markets for MVP
export const MVP_MARKETS: Market[] = [
  {
    symbol: 'BTCUSDT',
    name: 'Bitcoin / USDT',
    type: 'crypto',
    exchange: 'Binance',
    base_currency: 'BTC',
    quote_currency: 'USDT',
    timeframes: ['5m', '15m', '1h', '4h', '1D'],
  },
  {
    symbol: 'ETHUSDT',
    name: 'Ethereum / USDT',
    type: 'crypto',
    exchange: 'Binance',
    base_currency: 'ETH',
    quote_currency: 'USDT',
    timeframes: ['5m', '15m', '1h', '4h', '1D'],
  },
  {
    symbol: 'SPY',
    name: 'SPDR S&P 500 ETF',
    type: 'etf',
    exchange: 'NYSE',
    base_currency: 'SPY',
    quote_currency: 'USD',
    timeframes: ['5m', '15m', '1h', '4h', '1D'],
  },
  {
    symbol: 'EURUSD',
    name: 'Euro / US Dollar',
    type: 'forex',
    exchange: 'OANDA',
    base_currency: 'EUR',
    quote_currency: 'USD',
    timeframes: ['5m', '15m', '1h', '4h', '1D'],
  },
]

// Dataset
export const DatasetSchema = z.object({
  id: z.string().uuid(),
  market: z.string(),
  timeframe: z.string(),
  source: z.string().optional(),
  start_date: z.string().datetime(),
  end_date: z.string().datetime(),
  row_count: z.number().int().positive().optional(),
  file_path: z.string().optional(),
  metadata: z.record(z.unknown()).optional(),
  created_at: z.string().datetime(),
})

export type Dataset = z.infer<typeof DatasetSchema>