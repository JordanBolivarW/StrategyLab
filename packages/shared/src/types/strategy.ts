import { z } from 'zod'

// Node Types
export const NodeTypeSchema = z.enum([
  // Data
  'data.open',
  'data.high',
  'data.low',
  'data.close',
  'data.volume',
  'data.timestamp',
  // Indicators
  'indicator.sma',
  'indicator.ema',
  'indicator.rsi',
  'indicator.macd',
  'indicator.atr',
  'indicator.bollinger_bands',
  // Comparators
  'logic.gt',
  'logic.lt',
  'logic.gte',
  'logic.lte',
  'logic.cross_above',
  'logic.cross_below',
  // Logic
  'logic.and',
  'logic.or',
  'logic.not',
  // Actions
  'action.buy',
  'action.sell',
  'action.long',
  'action.short',
  'action.close',
  // Risk
  'risk.position_size',
  'risk.stop_loss',
  'risk.take_profit',
])

export type NodeType = z.infer<typeof NodeTypeSchema>

// Node Categories
export const NodeCategorySchema = z.enum([
  'data',
  'indicator',
  'comparator',
  'logic',
  'action',
  'risk',
  'time',
  'math',
])

export type NodeCategory = z.infer<typeof NodeCategorySchema>

// Strategy Graph
export const PositionSchema = z.object({
  x: z.number(),
  y: z.number(),
})

export const StrategyNodeSchema = z.object({
  id: z.string().uuid(),
  type: NodeTypeSchema,
  position: PositionSchema,
  data: z.record(z.unknown()),
})

export type StrategyNode = z.infer<typeof StrategyNodeSchema>

export const StrategyEdgeSchema = z.object({
  id: z.string().uuid(),
  source: z.string().uuid(),
  target: z.string().uuid(),
  sourceHandle: z.string().optional(),
  targetHandle: z.string().optional(),
})

export type StrategyEdge = z.infer<typeof StrategyEdgeSchema>

export const StrategyGraphSchema = z.object({
  nodes: z.array(StrategyNodeSchema).min(1),
  edges: z.array(StrategyEdgeSchema).min(1),
  metadata: z.record(z.unknown()).default({}),
})

export type StrategyGraph = z.infer<typeof StrategyGraphSchema>

// Strategy Metadata
export const StrategyMetadataSchema = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  market: z.string().min(1).max(50),
  timeframe: z.string().min(1).max(20),
  created_by: z.enum(['user', 'agent']).default('user'),
  source: z.enum(['web', 'mcp', 'api']).default('web'),
  client: z.string().optional(),
})

export type StrategyMetadata = z.infer<typeof StrategyMetadataSchema>

// Strategy Version
export const StrategyVersionSchema = z.object({
  id: z.string().uuid(),
  strategy_id: z.string().uuid(),
  version: z.number().int().positive(),
  graph: StrategyGraphSchema,
  changelog: z.string().optional(),
  created_by: z.string().optional(),
  source: z.string().optional(),
  client: z.string().optional(),
  created_at: z.string().datetime(),
})

export type StrategyVersion = z.infer<typeof StrategyVersionSchema>

// Node Definition (for discovery)
export const NodeDefinitionSchema = z.object({
  id: NodeTypeSchema,
  name: z.string(),
  category: NodeCategorySchema,
  description: z.string(),
  inputs: z.record(z.object({
    type: z.string(),
    description: z.string().optional(),
    required: z.boolean().default(true),
  })),
  outputs: z.record(z.object({
    type: z.string(),
    description: z.string().optional(),
  })),
  parameters: z.array(z.object({
    name: z.string(),
    type: z.enum(['string', 'number', 'integer', 'boolean', 'select']),
    description: z.string().optional(),
    required: z.boolean().default(false),
    default: z.unknown().optional(),
    min: z.number().optional(),
    max: z.number().optional(),
    options: z.array(z.string()).optional(),
  })).default([]),
})

export type NodeDefinition = z.infer<typeof NodeDefinitionSchema>