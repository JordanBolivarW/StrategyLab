# @strategy-lab/shared

Shared TypeScript types, Zod schemas, and utilities for Strategy Lab MCP.

## Installation

```bash
# From monorepo root
pnpm install
```

## Usage

```typescript
import {
  StrategyGraph,
  StrategyNode,
  StrategyEdge,
  BacktestConfig,
  BacktestResult,
  Market,
  IndicatorDefinition,
  validateStrategyGraph,
  validateBacktestConfig,
  symbol,
  timeframe,
  uuid,
} from '@strategy-lab/shared'
```

## Exports

### Types
- `strategy` - StrategyGraph, StrategyNode, StrategyEdge, StrategyVersion, NodeType, NodeCategory
- `indicator` - IndicatorDefinition, IndicatorParameter, IndicatorInput, IndicatorOutput, IndicatorId
- `market` - Market, MarketType, Timeframe, Candle, Dataset, MarketDataQuery
- `backtest` - BacktestConfig, BacktestResult, BacktestMetrics, EquityPoint, Trade, BacktestStatus
- `mcp` - MCPTool, MCPToolCall, MCPToolResult, PlatformCapabilities, all tool schemas

### Validation
- `validateStrategyGraph()` - Validate strategy graph structure
- `validateStrategyNode()` - Validate single node
- `validateStrategyEdge()` - Validate single edge
- `validateBacktestConfig()` - Validate backtest configuration
- `validateMarket()` - Validate market definition
- `validateIndicatorDefinition()` - Validate indicator definition

### Validators
- `symbol` - Trading symbol (e.g., BTCUSDT, SPY)
- `timeframe` - Timeframe enum (5m, 15m, 1h, 4h, 1D, etc.)
- `uuid` - UUID v4
- `dateRange` - Start/end date with validation
- `percentage` - 0-100
- `probability` - 0-1
- `positiveNumber` - > 0
- `nonNegativeNumber` - >= 0

### Built-in Data
- `BUILT_IN_INDICATORS` - Array of 6 indicator definitions (SMA, EMA, RSI, MACD, ATR, BB)
- `MVP_MARKETS` - Array of 4 market definitions (BTCUSDT, ETHUSDT, SPY, EURUSD)

## Development

```bash
# Build
pnpm build

# Watch mode
pnpm dev

# Type check
pnpm typecheck

# Lint
pnpm lint

# Test
pnpm test
```