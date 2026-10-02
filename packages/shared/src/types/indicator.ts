import { z } from 'zod'

// Indicator Categories
export const IndicatorCategorySchema = z.enum([
  'trend',
  'momentum',
  'volatility',
  'volume',
  'other',
])

export type IndicatorCategory = z.infer<typeof IndicatorCategorySchema>

// Indicator Parameter
export const IndicatorParameterSchema = z.object({
  name: z.string(),
  type: z.enum(['integer', 'number', 'string', 'boolean', 'select']),
  description: z.string().optional(),
  required: z.boolean().default(false),
  default: z.unknown().optional(),
  min: z.number().optional(),
  max: z.number().optional(),
  options: z.array(z.string()).optional(),
})

export type IndicatorParameter = z.infer<typeof IndicatorParameterSchema>

// Indicator Input
export const IndicatorInputSchema = z.object({
  name: z.string(),
  type: z.enum(['series', 'value']),
  description: z.string().optional(),
  default: z.string().optional(),
})

export type IndicatorInput = z.infer<typeof IndicatorInputSchema>

// Indicator Output
export const IndicatorOutputSchema = z.object({
  name: z.string(),
  type: z.enum(['series', 'value']),
  description: z.string().optional(),
})

export type IndicatorOutput = z.infer<typeof IndicatorOutputSchema>

// Indicator Definition
export const IndicatorDefinitionSchema = z.object({
  id: z.string(),
  name: z.string(),
  category: IndicatorCategorySchema,
  description: z.string(),
  inputs: z.array(IndicatorInputSchema).default([]),
  parameters: z.array(IndicatorParameterSchema).default([]),
  outputs: z.array(IndicatorOutputSchema).default([]),
})

export type IndicatorDefinition = z.infer<typeof IndicatorDefinitionSchema>

// Built-in Indicators
export const BUILT_IN_INDICATORS: IndicatorDefinition[] = [
  {
    id: 'sma',
    name: 'Simple Moving Average',
    category: 'trend',
    description: 'Simple moving average of a price series',
    inputs: [{ name: 'source', type: 'series', default: 'close', description: 'Price series to average' }],
    parameters: [{ name: 'period', type: 'integer', min: 2, max: 500, default: 20, description: 'Number of periods', required: true }],
    outputs: [{ name: 'value', type: 'series', description: 'SMA values' }],
  },
  {
    id: 'ema',
    name: 'Exponential Moving Average',
    category: 'trend',
    description: 'Exponential moving average of a price series',
    inputs: [{ name: 'source', type: 'series', default: 'close', description: 'Price series to average' }],
    parameters: [{ name: 'period', type: 'integer', min: 2, max: 500, default: 20, description: 'Number of periods', required: true }],
    outputs: [{ name: 'value', type: 'series', description: 'EMA values' }],
  },
  {
    id: 'rsi',
    name: 'Relative Strength Index',
    category: 'momentum',
    description: 'Momentum oscillator measuring speed and change of price movements',
    inputs: [{ name: 'source', type: 'series', default: 'close', description: 'Price series' }],
    parameters: [{ name: 'period', type: 'integer', min: 2, max: 100, default: 14, description: 'Number of periods', required: true }],
    outputs: [{ name: 'value', type: 'series', description: 'RSI values (0-100)' }],
  },
  {
    id: 'macd',
    name: 'Moving Average Convergence Divergence',
    category: 'momentum',
    description: 'Trend-following momentum indicator showing relationship between two EMAs',
    inputs: [{ name: 'source', type: 'series', default: 'close', description: 'Price series' }],
    parameters: [
      { name: 'fast_period', type: 'integer', min: 2, max: 50, default: 12, description: 'Fast EMA period', required: true },
      { name: 'slow_period', type: 'integer', min: 2, max: 100, default: 26, description: 'Slow EMA period', required: true },
      { name: 'signal_period', type: 'integer', min: 2, max: 50, default: 9, description: 'Signal line period', required: true },
    ],
    outputs: [
      { name: 'macd', type: 'series', description: 'MACD line' },
      { name: 'signal', type: 'series', description: 'Signal line' },
      { name: 'histogram', type: 'series', description: 'MACD histogram' },
    ],
  },
  {
    id: 'atr',
    name: 'Average True Range',
    category: 'volatility',
    description: 'Measures market volatility by decomposing the entire range of an asset price',
    inputs: [
      { name: 'high', type: 'series', description: 'High prices' },
      { name: 'low', type: 'series', description: 'Low prices' },
      { name: 'close', type: 'series', description: 'Close prices' },
    ],
    parameters: [{ name: 'period', type: 'integer', min: 2, max: 100, default: 14, description: 'Number of periods', required: true }],
    outputs: [{ name: 'value', type: 'series', description: 'ATR values' }],
  },
  {
    id: 'bollinger_bands',
    name: 'Bollinger Bands',
    category: 'volatility',
    description: 'Volatility bands placed above and below a moving average',
    inputs: [{ name: 'source', type: 'series', default: 'close', description: 'Price series' }],
    parameters: [
      { name: 'period', type: 'integer', min: 2, max: 100, default: 20, description: 'Moving average period', required: true },
      { name: 'std_dev', type: 'number', min: 0.5, max: 5, default: 2, description: 'Standard deviation multiplier', required: true },
    ],
    outputs: [
      { name: 'upper', type: 'series', description: 'Upper band' },
      { name: 'middle', type: 'series', description: 'Middle band (SMA)' },
      { name: 'lower', type: 'series', description: 'Lower band' },
    ],
  },
]

// Indicator IDs
export const IndicatorIdSchema = z.enum(BUILT_IN_INDICATORS.map(i => i.id) as [string, ...string[]])

export type IndicatorId = z.infer<typeof IndicatorIdSchema>