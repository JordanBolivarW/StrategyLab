# Spec: Project Foundation

## User Story
As a developer, I want to set up the complete project foundation (monorepo structure, backend, frontend, database, MCP server) so that the team can start implementing the Strategy Lab MCP features immediately.

## Acceptance Criteria
- [ ] Monorepo structure created with pnpm workspaces
- [ ] Backend (FastAPI + Python 3.13) with SQLAlchemy 2.x async, pytest + httpx
- [ ] Frontend (React 18 + TypeScript + Vite) with Lightweight Charts
- [ ] PostgreSQL database schema for core entities (Users, Strategies, StrategyVersions, Backtests, Trades, Metrics, Datasets)
- [ ] MCP Server structure integrated with FastAPI
- [ ] Shared types/package for Strategy Graph, Indicators, Market Data
- [ ] Development tooling: ESLint, Prettier, Ruff, MyPy, Husky
- [ ] Docker Compose for local development (PostgreSQL, Redis, MinIO)
- [ ] AGENTS.md created with project configuration
- [ ] CI/CD pipeline skeleton (GitHub Actions)
- [ ] All services run with `pnpm dev` or `docker-compose up`

## Technical Requirements
- **Monorepo**: pnpm workspaces with `apps/` and `packages/` structure
- **Backend**: FastAPI, Python 3.13, SQLAlchemy 2.x (async), Pydantic v2, Alembic
- **Frontend**: React 18, TypeScript 5.x, Vite, React Flow, Lightweight Charts, Tailwind CSS
- **Database**: PostgreSQL 16+, Parquet for market data
- **MCP**: FastMCP or native MCP implementation
- **Testing**: pytest + httpx (backend), Vitest + React Testing Library (frontend)
- **Linting**: Ruff (Python), ESLint + TypeScript ESLint (frontend)
- **Formatting**: Prettier (frontend), Ruff format (Python)

## API / Interface
```typescript
// Shared Strategy Graph types (packages/shared/src/types/strategy.ts)
interface StrategyGraph {
  nodes: StrategyNode[];
  edges: StrategyEdge[];
  metadata: StrategyMetadata;
}

interface StrategyNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: Record<string, unknown>;
}

interface StrategyEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
}

// Backtest types
interface BacktestConfig {
  strategyId: string;
  market: string;
  timeframe: string;
  startDate: string;
  endDate: string;
  initialCapital: number;
  commission: number;
  slippage: number;
}

interface BacktestResult {
  id: string;
  config: BacktestConfig;
  metrics: BacktestMetrics;
  equityCurve: EquityPoint[];
  trades: Trade[];
  createdAt: string;
}
```

## Data Model
```sql
-- Core tables (PostgreSQL)
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE strategies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  market VARCHAR(50) NOT NULL,
  timeframe VARCHAR(20) NOT NULL,
  graph JSONB NOT NULL,
  current_version INT DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE strategy_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id) ON DELETE CASCADE,
  version INT NOT NULL,
  graph JSONB NOT NULL,
  changelog TEXT,
  created_by VARCHAR(100), -- 'user' | 'agent'
  source VARCHAR(50), -- 'web' | 'mcp' | 'api'
  client VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(strategy_id, version)
);

CREATE TABLE backtests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_version_id UUID REFERENCES strategy_versions(id),
  config JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'pending', -- pending, running, completed, failed
  metrics JSONB,
  equity_curve JSONB,
  trades JSONB,
  error TEXT,
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE datasets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  market VARCHAR(50) NOT NULL,
  timeframe VARCHAR(20) NOT NULL,
  source VARCHAR(100), -- 'csv', 'binance', 'polygon', etc.
  start_date TIMESTAMPTZ NOT NULL,
  end_date TIMESTAMPTZ NOT NULL,
  row_count BIGINT,
  file_path VARCHAR(500), -- Parquet file path
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(market, timeframe, source, start_date, end_date)
);

CREATE TABLE experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  strategy_id UUID REFERENCES strategies(id),
  base_version INT NOT NULL,
  candidate_version INT NOT NULL,
  hypothesis TEXT,
  changes JSONB,
  dataset_id UUID REFERENCES datasets(id),
  backtest_id UUID REFERENCES backtests(id),
  results JSONB,
  conclusion TEXT,
  created_by VARCHAR(100),
  source VARCHAR(50),
  client VARCHAR(100),
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## UI / UX Requirements
- Monorepo root with clear README
- Backend: Auto-reload on file change (`uvicorn --reload`)
- Frontend: HMR with Vite
- Shared package: TypeScript types published internally
- Docker Compose: One command starts all infra

## Edge Cases
- Python 3.13 may have some dependency compatibility issues (monitor)
- Lightweight Charts requires Canvas API (works in all modern browsers)
- MCP server must share the same core services as the REST API
- Parquet files for market data should be stored outside the database (object storage or local files)

## Testing Strategy
- **Unit**: pytest for backend services, Vitest for frontend utils/hooks
- **Integration**: pytest + httpx for API endpoints, testcontainers for DB
- **E2E**: Playwright for critical user flows (create strategy → run backtest → view results)

## Rollout Plan
- [ ] Feature flag: `foundation`
- [ ] Gradual rollout: 100% (internal only)
- [ ] Rollback: Revert docker-compose and pnpm workspace config

## Dependencies
- Python 3.13, Node.js 20+, pnpm 9+, Docker, PostgreSQL 16+
- Key packages: fastapi, uvicorn, sqlalchemy, alembic, pydantic, pydantic-settings, python-multipart, python-jose, passlib, bcrypt, polars, numpy, pandas, fastmcp/mcp
- Frontend: react, react-dom, reactflow, lightweight-charts, tailwindcss, @tanstack/react-query, zustand, zod, react-hook-form

## Notes
This spec covers Phase 1 (Foundation) of the roadmap. Subsequent phases (Backtesting, MCP, Web, Experimentation) will have their own specs.