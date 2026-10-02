import { z } from 'zod'
import {
  StrategyGraphSchema,
  StrategyNodeSchema,
  StrategyEdgeSchema,
  NodeDefinitionSchema,
} from '../types/strategy'
import { MarketSchema } from '../types/market'
import { IndicatorDefinitionSchema } from '../types/indicator'

// Validation helpers
export function validateStrategyGraph(data: unknown) {
  return StrategyGraphSchema.safeParse(data)
}

export function validateStrategyNode(data: unknown) {
  return StrategyNodeSchema.safeParse(data)
}

export function validateStrategyEdge(data: unknown) {
  return StrategyEdgeSchema.safeParse(data)
}

export function validateMarket(data: unknown) {
  return MarketSchema.safeParse(data)
}

export function validateIndicatorDefinition(data: unknown) {
  return IndicatorDefinitionSchema.safeParse(data)
}

export function validateNodeDefinition(data: unknown) {
  return NodeDefinitionSchema.safeParse(data)
}

// Custom validators
export const positiveNumber = z.number().positive()
export const nonNegativeNumber = z.number().nonnegative()
export const percentage = z.number().min(0).max(100)
export const basisPoints = z.number().min(0).max(10000)
export const probability = z.number().min(0).max(1)

// Date range validator
export const dateRange = z.object({
  start: z.string().datetime(),
  end: z.string().datetime(),
}).refine((data) => new Date(data.start) < new Date(data.end), {
  message: 'Start date must be before end date',
  path: ['end'],
})

// UUID validator
export const uuid = z.string().uuid()

// Symbol validator (e.g., BTCUSDT, SPY, EURUSD)
export const symbol = z.string().min(1).max(50).regex(/^[A-Z0-9/.-]+$/)

export const timeframe = z.enum(['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1D', '1W', '1M'])

// Composite validators
export const createStrategyInput = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  market: symbol,
  timeframe: timeframe,
  graph: StrategyGraphSchema,
})

export const updateStrategyInput = z.object({
  name: z.string().min(1).max(255).optional(),
  description: z.string().optional(),
  graph: StrategyGraphSchema.optional(),
}).refine((data) => data.name !== undefined || data.description !== undefined || data.graph !== undefined, {
  message: 'At least one field must be provided',
})

export const backtestConfigInput = z.object({
  strategy_id: uuid,
  market: symbol,
  timeframe: timeframe,
  start_date: z.string().datetime(),
  end_date: z.string().datetime(),
  initial_capital: positiveNumber.default(10000),
  commission: probability.default(0.001),
  slippage: probability.default(0.0005),
}).refine((data) => new Date(data.start_date) < new Date(data.end_date), {
  message: 'Start date must be before end date',
  path: ['end_date'],
})

// Type exports
export type CreateStrategyInput = z.infer<typeof createStrategyInput>
export type UpdateStrategyInput = z.infer<typeof updateStrategyInput>
export type BacktestConfigInput = z.infer<typeof backtestConfigInput>
export type DateRange = z.infer<typeof dateRange>