import { z } from 'zod'
import {
  StrategyGraphSchema,
  NodeDefinitionSchema,
} from './strategy'
import { MarketSchema } from './market'
import { IndicatorDefinitionSchema as IndicatorDefSchema } from './indicator'

// MCP Tool Definition
export const MCPToolSchema = z.object({
  name: z.string(),
  description: z.string(),
  inputSchema: z.record(z.unknown()),
})

export type MCPTool = z.infer<typeof MCPToolSchema>

// MCP Tool Call
export const MCPToolCallSchema = z.object({
  name: z.string(),
  arguments: z.record(z.unknown()),
})

export type MCPToolCall = z.infer<typeof MCPToolCallSchema>

// MCP Tool Result
export const MCPToolResultSchema = z.object({
  content: z.array(z.object({
    type: z.literal('text'),
    text: z.string(),
  })),
  isError: z.boolean().default(false),
})

export type MCPToolResult = z.infer<typeof MCPToolResultSchema>

// MCP Tool Names (Discovery)
export const DiscoveryTools = [
  'get_platform_capabilities',
  'list_markets',
  'describe_market',
  'list_indicators',
  'describe_indicator',
  'list_node_types',
  'describe_node_type',
] as const

export type DiscoveryToolName = typeof DiscoveryTools[number]

// MCP Tool Names (Strategies)
export const StrategyTools = [
  'list_strategies',
  'get_strategy',
  'create_strategy',
  'clone_strategy',
  'update_strategy',
  'validate_strategy',
  'get_strategy_versions',
  'get_strategy_diff',
] as const

export type StrategyToolName = typeof StrategyTools[number]

// MCP Tool Names (Backtesting)
export const BacktestTools = [
  'run_backtest',
  'get_backtest',
  'list_backtests',
  'get_backtest_trades',
  'get_backtest_metrics',
] as const

export type BacktestToolName = typeof BacktestTools[number]

// MCP Tool Names (Comparison)
export const ComparisonTools = [
  'compare_backtests',
  'compare_strategies',
  'compare_strategy_versions',
] as const

export type ComparisonToolName = typeof ComparisonTools[number]

// MCP Tool Names (Experiments - Future)
export const ExperimentTools = [
  'create_experiment',
  'get_experiment',
  'list_experiments',
  'promote_experiment',
  'discard_experiment',
] as const

export type ExperimentToolName = typeof ExperimentTools[number]

// MCP Tool Names (Optimization - Future)
export const OptimizationTools = [
  'run_optimization',
  'get_optimization',
  'get_optimization_results',
] as const

export type OptimizationToolName = typeof OptimizationTools[number]

// All MCP Tools
export const ALL_MCP_TOOLS = [
  ...DiscoveryTools,
  ...StrategyTools,
  ...BacktestTools,
  ...ComparisonTools,
  ...ExperimentTools,
  ...OptimizationTools,
] as const

export type MCPToolName = typeof ALL_MCP_TOOLS[number]

// MCP Server Info
export const MCPServerInfoSchema = z.object({
  name: z.string(),
  version: z.string(),
  protocol_version: z.string().default('2024-11-05'),
  capabilities: z.object({
    tools: z.boolean().default(true),
    resources: z.boolean().default(false),
    prompts: z.boolean().default(false),
  }),
})

export type MCPServerInfo = z.infer<typeof MCPServerInfoSchema>

// Platform Capabilities
export const PlatformCapabilitiesSchema = z.object({
  markets: z.array(MarketSchema),
  indicators: z.array(IndicatorDefSchema),
  node_types: z.array(NodeDefinitionSchema),
  max_strategy_nodes: z.number().default(100),
  max_strategy_edges: z.number().default(200),
  max_backtest_bars: z.number().default(100000),
  supported_timeframes: z.array(z.string()),
  features: z.object({
    versioning: z.boolean().default(true),
    experiments: z.boolean().default(false),
    optimization: z.boolean().default(false),
    walk_forward: z.boolean().default(false),
    monte_carlo: z.boolean().default(false),
  }),
})

export type PlatformCapabilities = z.infer<typeof PlatformCapabilitiesSchema>

// Tool Input/Output Schemas
export const GetPlatformCapabilitiesInput = z.object({})
export const GetPlatformCapabilitiesOutput = PlatformCapabilitiesSchema

export const ListMarketsInput = z.object({})
export const ListMarketsOutput = z.array(MarketSchema)

export const DescribeMarketInput = z.object({ symbol: z.string() })
export const DescribeMarketOutput = MarketSchema

export const ListIndicatorsInput = z.object({})
export const ListIndicatorsOutput = z.array(IndicatorDefSchema)

export const DescribeIndicatorInput = z.object({ indicator_id: z.string() })
export const DescribeIndicatorOutput = IndicatorDefSchema

export const ListNodeTypesInput = z.object({})
export const ListNodeTypesOutput = z.array(NodeDefinitionSchema)

export const DescribeNodeTypeInput = z.object({ node_type_id: z.string() })
export const DescribeNodeTypeOutput = NodeDefinitionSchema

export const ListStrategiesInput = z.object({
  page: z.number().int().positive().default(1),
  page_size: z.number().int().positive().max(100).default(20),
  market: z.string().optional(),
})
export const ListStrategiesOutput = z.object({
  items: z.array(z.object({
    id: z.string().uuid(),
    name: z.string(),
    market: z.string(),
    timeframe: z.string(),
    current_version: z.number(),
    created_at: z.string(),
    updated_at: z.string(),
  })),
  total: z.number(),
  page: z.number(),
  page_size: z.number(),
})

export const GetStrategyInput = z.object({ strategy_id: z.string().uuid() })
export const GetStrategyOutput = z.object({
  id: z.string().uuid(),
  name: z.string(),
  market: z.string(),
  timeframe: z.string(),
  graph: StrategyGraphSchema,
  current_version: z.number(),
})

// Rename to avoid conflicts with validation.ts
export const MCPCreateStrategyInput = z.object({
  name: z.string().min(1).max(255),
  description: z.string().optional(),
  market: z.string().min(1).max(50),
  timeframe: z.string().min(1).max(20),
  graph: StrategyGraphSchema,
})
export const MCPCreateStrategyOutput = z.object({
  id: z.string().uuid(),
  name: z.string(),
  market: z.string(),
  timeframe: z.string(),
  graph: StrategyGraphSchema,
  current_version: z.number(),
})

export const MCPCloneStrategyInput = z.object({
  strategy_id: z.string().uuid(),
  name: z.string().min(1).max(255),
})
export const MCPCloneStrategyOutput = MCPCreateStrategyOutput

export const MCPUpdateStrategyInput = z.object({
  strategy_id: z.string().uuid(),
  name: z.string().min(1).max(255).optional(),
  description: z.string().optional(),
  graph: StrategyGraphSchema.optional(),
})
export const MCPUpdateStrategyOutput = GetStrategyOutput

export const ValidateStrategyInput = z.object({ strategy_id: z.string().uuid() })
export const ValidateStrategyOutput = z.object({
  valid: z.boolean(),
  errors: z.array(z.string()),
  node_count: z.number(),
  edge_count: z.number(),
})

export const GetStrategyVersionsInput = z.object({ strategy_id: z.string().uuid() })
export const GetStrategyVersionsOutput = z.array(z.object({
  id: z.string().uuid(),
  version: z.number(),
  changelog: z.string().optional(),
  created_by: z.string().optional(),
  created_at: z.string(),
}))

export const GetStrategyDiffInput = z.object({
  strategy_id: z.string().uuid(),
  version_a: z.number().int().positive(),
  version_b: z.number().int().positive(),
})
export const GetStrategyDiffOutput = z.object({
  changes: z.array(z.object({
    path: z.string(),
    old_value: z.unknown(),
    new_value: z.unknown(),
  })),
  metrics_impact: z.record(z.number()).optional(),
})

// Define BacktestConfigSchema locally
const BacktestConfigSchema = z.object({
  strategy_id: z.string().uuid(),
  market: z.string().min(1).max(50),
  timeframe: z.string().min(1).max(20),
  start_date: z.string().datetime(),
  end_date: z.string().datetime(),
  initial_capital: z.number().positive().default(10000),
  commission: z.number().min(0).max(1).default(0.001),
  slippage: z.number().min(0).max(1).default(0.0005),
})

export const RunBacktestInput = z.object({
  strategy_version_id: z.string().uuid(),
  config: BacktestConfigSchema,
})
export const RunBacktestOutput = z.object({
  backtest_id: z.string().uuid(),
  status: z.string(),
})

export const GetBacktestInput = z.object({ backtest_id: z.string().uuid() })
// Define BacktestResultSchema locally
const BacktestResultSchema = z.object({
  id: z.string().uuid(),
  strategy_id: z.string().uuid(),
  strategy_version_id: z.string().uuid(),
  config: BacktestConfigSchema,
  status: z.string(),
  metrics: z.any().optional(),
  equity_curve: z.any().optional(),
  trades: z.any().optional(),
  error: z.string().optional(),
  started_at: z.string().datetime().optional(),
  completed_at: z.string().datetime().optional(),
  created_at: z.string().datetime(),
})
export const GetBacktestOutput = BacktestResultSchema

export const ListBacktestsInput = z.object({
  strategy_id: z.string().uuid().optional(),
  status: z.string().optional(),
  limit: z.number().int().positive().default(50),
})
export const ListBacktestsOutput = z.array(z.object({
  id: z.string().uuid(),
  strategy_id: z.string().uuid(),
  status: z.string(),
  metrics: BacktestResultSchema.shape.metrics,
  created_at: z.string(),
}))

export const GetBacktestTradesInput = z.object({ backtest_id: z.string().uuid() })
export const GetBacktestTradesOutput = z.array(z.object({
  id: z.number(),
  type: z.string(),
  entry_time: z.string(),
  exit_time: z.string(),
  entry_price: z.number(),
  exit_price: z.number(),
  return_pct: z.number(),
  pnl: z.number(),
  duration: z.string(),
}))

export const GetBacktestMetricsInput = z.object({ backtest_id: z.string().uuid() })
export const GetBacktestMetricsOutput = BacktestResultSchema.shape.metrics

export const CompareBacktestsInput = z.object({
  backtest_ids: z.array(z.string().uuid()).min(2).max(10),
})
export const CompareBacktestsOutput = z.object({
  comparison: z.array(z.object({
    backtest_id: z.string().uuid(),
    metrics: BacktestResultSchema.shape.metrics,
  })),
  best: z.object({
    return: z.string().uuid(),
    sharpe: z.string().uuid().optional(),
    drawdown: z.string().uuid().optional(),
  }),
})

export const CompareStrategiesInput = z.object({
  strategy_ids: z.array(z.string().uuid()).min(2).max(10),
})
export const CompareStrategiesOutput = CompareBacktestsOutput

export const CompareStrategyVersionsInput = z.object({
  strategy_id: z.string().uuid(),
  versions: z.array(z.number().int().positive()).min(2).max(10),
})
export const CompareStrategyVersionsOutput = CompareBacktestsOutput