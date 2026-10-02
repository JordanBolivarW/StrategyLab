# strategy-lab-shared

Shared Pydantic schemas for Strategy Lab MCP - matching TypeScript `@strategy-lab/shared` types.

## Installation

```bash
# From monorepo root
cd packages/python-shared
pip install -e .
```

## Usage

```python
from strategy_lab_shared.schemas import (
    StrategyGraph,
    StrategyNode,
    StrategyEdge,
    StrategyNodeType,
    BacktestConfig,
    BacktestMetrics,
    Market,
    MarketType,
    IndicatorDefinition,
    BUILT_IN_INDICATORS,
)
from strategy_lab_shared.indicators import (
    get_indicator_by_id,
    validate_indicator_params,
    get_default_params,
    merge_params,
)
```

## Exports

### Schemas (`schemas.py`)
- `StrategyNode`, `StrategyEdge`, `StrategyGraph`
- `StrategyNodeType` (enum), `StrategyCategory` (enum)
- `StrategyMetadata`, `StrategyVersion`
- `BacktestConfig`, `BacktestMetrics`, `EquityPoint`, `Trade`, `BacktestResult`, `BacktestStatus`
- `Market`, `MarketType`, `Timeframe`, `Candle`, `Dataset`
- `IndicatorDefinition`, `IndicatorParameter`, `IndicatorInput`, `IndicatorOutput`, `IndicatorCategory`
- `MCPTool`, `MCPToolCall`, `MCPToolResult`, `PlatformCapabilities`
- `BUILT_IN_INDICATORS` - 6 indicators (SMA, EMA, RSI, MACD, ATR, Bollinger Bands)

### Indicators (`indicators.py`)
- `get_indicator_by_id(id)` - Get indicator definition
- `get_indicators_by_category(category)` - Filter by category
- `list_indicator_ids()` - List all indicator IDs
- `validate_indicator_params(id, params)` - Validate parameters
- `get_default_params(id)` - Get default parameters
- `merge_params(id, user_params)` - Merge with defaults

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type check
mypy src

# Lint
ruff check src tests
ruff format src tests
```

## Schema Alignment

This package mirrors `@strategy-lab/shared` TypeScript types. When making changes:
1. Update TypeScript schemas in `packages/shared/src/types/`
2. Update Python schemas here
3. Run tests in both packages to ensure alignment