# Task: Project Foundation

## Spec Reference
[SPECS/project-foundation.md](SPECS/project-foundation.md)

## Approach
Set up a complete monorepo with pnpm workspaces containing:
- `apps/backend` — FastAPI + SQLAlchemy 2.x async + MCP Server
- `apps/frontend` — React 18 + TypeScript + Vite + React Flow + Lightweight Charts
- `packages/shared` — Shared TypeScript types (Strategy Graph, Indicators, Market Data, Backtest, MCP)
- `packages/python-shared` — Shared Pydantic schemas
- Docker Compose for local infrastructure (PostgreSQL, Redis, MinIO)

## Implementation Steps

### Phase 1: Monorepo Root Setup
- [ ] 1.1 Create `package.json` with pnpm workspace config and root scripts
- [ ] 1.2 Create `pnpm-workspace.yaml` with package patterns
- [ ] 1.3 Create `tsconfig.base.json` with base TypeScript config
- [ ] 1.4 Create `.eslintrc.cjs` root ESLint config
- [ ] 1.5 Create `.prettierrc` Prettier config
- [ ] 1.6 Create comprehensive `.gitignore`
- [ ] 1.7 Create `README.md` with project overview and setup instructions
- [ ] 1.8 Create `docker-compose.yml` with PostgreSQL, Redis, MinIO, pgAdmin
- [ ] 1.9 Create `.env.example` with all environment variables
- [ ] 1.10 Create `.github/workflows/ci.yml` CI pipeline skeleton

### Phase 2: Backend (apps/backend)
- [ ] 2.1 Create `pyproject.toml` with dependencies and tool config
- [ ] 2.2 Create `alembic.ini` migration config
- [ ] 2.3 Create `src/main.py` FastAPI app entry point
- [ ] 2.4 Create `src/config.py` Pydantic Settings config
- [ ] 2.5 Create `src/database.py` SQLAlchemy async engine and session
- [ ] 2.6 Create `src/models/__init__.py` SQLAlchemy models (User, Strategy, StrategyVersion, Backtest, Dataset, Experiment)
- [ ] 2.7 Create `src/schemas/__init__.py` Pydantic schemas for API
- [ ] 2.8 Create `src/api/__init__.py` API router
- [ ] 2.9 Create `src/api/v1/__init__.py` v1 router
- [ ] 2.10 Create `src/api/v1/strategies.py` Strategy CRUD endpoints
- [ ] 2.11 Create `src/api/v1/backtests.py` Backtest endpoints
- [ ] 2.12 Create `src/api/v1/markets.py` Market data endpoints
- [ ] 2.13 Create `src/api/v1/mcp.py` MCP server integration
- [ ] 2.14 Create `src/services/__init__.py` Service layer
- [ ] 2.15 Create `src/services/strategy_engine.py` Strategy graph validation/execution
- [ ] 2.16 Create `src/services/indicator_engine.py` Indicator calculations (Polars/NumPy)
- [ ] 2.17 Create `src/services/backtest_engine.py` Backtest engine skeleton
- [ ] 2.18 Create `src/services/market_data.py` Market data loading (Parquet/CSV)
- [ ] 2.19 Create `tests/conftest.py` Pytest fixtures with testcontainers
- [ ] 2.20 Create `tests/test_strategies.py` Strategy API tests
- [ ] 2.21 Create `tests/test_backtest.py` Backtest engine tests
- [ ] 2.22 Create `tests/test_indicators.py` Indicator calculation tests

### Phase 3: Frontend (apps/frontend)
- [ ] 3.1 Create `package.json` with dependencies and scripts
- [ ] 3.2 Create `tsconfig.json` TypeScript config
- [ ] 3.3 Create `vite.config.ts` Vite config with React, path aliases
- [ ] 3.4 Create `tailwind.config.js` Tailwind config
- [ ] 3.5 Create `postcss.config.js` PostCSS config
- [ ] 3.6 Create `index.html` entry HTML
- [ ] 3.7 Create `src/main.tsx` React entry point
- [ ] 3.8 Create `src/App.tsx` Root component with providers (QueryClient, Zustand)
- [ ] 3.9 Create `src/pages/Dashboard.tsx` Main dashboard layout
- [ ] 3.10 Create `src/pages/StrategyBuilder.tsx` Strategy graph editor (React Flow)
- [ ] 3.11 Create `src/pages/BacktestResults.tsx` Results visualization
- [ ] 3.12 Create `src/components/Chart/Chart.tsx` Lightweight Charts wrapper
- [ ] 3.13 Create `src/components/Chart/Indicators.tsx` Indicator overlays
- [ ] 3.14 Create `src/components/StrategyGraph/StrategyGraph.tsx` React Flow graph editor
- [ ] 3.15 Create `src/components/StrategyGraph/NodeTypes.tsx` Custom node types (Indicator, Logic, Action)
- [ ] 3.16 Create `src/hooks/useStrategies.ts` TanStack Query hooks
- [ ] 3.17 Create `src/hooks/useBacktest.ts` Backtest hooks
- [ ] 3.18 Create `src/api/client.ts` Axios/Fetch API client
- [ ] 3.19 Create `src/types/strategy.ts` Shared types (re-export from @strategy-lab/shared)
- [ ] 3.20 Create `tests/setup.ts` Vitest setup
- [ ] 3.21 Create `tests/components/Chart.test.tsx` Chart component tests
- [ ] 3.22 Create `tests/hooks/useStrategies.test.ts` Hook tests

### Phase 4: Shared TypeScript Package (packages/shared)
- [ ] 4.1 Create `package.json` with package config and exports
- [ ] 4.2 Create `tsconfig.json` TypeScript config
- [ ] 4.3 Create `src/types/strategy.ts` StrategyGraph, Node, Edge, NodeType types
- [ ] 4.4 Create `src/types/indicator.ts` Indicator definitions, parameters
- [ ] 4.5 Create `src/types/market.ts` Market, Timeframe, Candle types
- [ ] 4.6 Create `src/types/backtest.ts` BacktestConfig, BacktestResult, Metrics, Trade
- [ ] 4.7 Create `src/types/mcp.ts` MCP tool definitions
- [ ] 4.8 Create `src/utils/validation.ts` Zod schemas for validation

### Phase 5: Shared Python Package (packages/python-shared)
- [ ] 5.1 Create `pyproject.toml` package config
- [ ] 5.2 Create `src/strategy_lab_shared/__init__.py` package init
- [ ] 5.3 Create `src/strategy_lab_shared/schemas.py` Pydantic models matching TypeScript types
- [ ] 5.4 Create `src/strategy_lab_shared/indicators.py` Indicator parameter definitions

### Phase 6: Tooling & Configuration
- [ ] 6.1 Configure ESLint + TypeScript ESLint for frontend
- [ ] 6.2 Configure Prettier for frontend
- [ ] 6.3 Configure Ruff for Python (lint + format)
- [ ] 6.4 Configure MyPy for Python type checking
- [ ] 6.5 Configure Husky pre-commit hooks
- [ ] 6.6 Verify `pnpm lint`, `pnpm typecheck`, `pnpm test` work

### Phase 7: Verification
- [ ] 7.1 Run `pnpm docker:up` — verify PostgreSQL, Redis, MinIO start
- [ ] 7.2 Run `pnpm db:migrate` — verify Alembic migrations run
- [ ] 7.3 Run `pnpm dev:backend` — verify FastAPI starts on port 8000
- [ ] 7.4 Run `pnpm dev:frontend` — verify Vite starts on port 5173
- [ ] 7.5 Run `pnpm dev` — verify both start concurrently
- [ ] 7.6 Run `pnpm test` — verify all tests pass
- [ ] 7.7 Run `pnpm lint` — verify no lint errors
- [ ] 7.8 Run `pnpm typecheck` — verify no type errors

## Tests to Write (TDD)

### Backend (pytest + httpx)
- [ ] T1: Strategy CRUD API — create, get, list, update, delete
- [ ] T2: Indicator calculations — SMA, EMA, RSI, MACD, ATR, Bollinger Bands
- [ ] T3: Backtest engine skeleton — config validation, status transitions

### Frontend (Vitest + React Testing Library)
- [ ] T4: Chart component — renders candlesticks + indicator overlays
- [ ] T5: Strategy Graph editor — adds nodes, connects edges, validates
- [ ] T6: Dashboard — loads strategies, shows market selector

### Shared (Zod validation)
- [ ] T7: StrategyGraph schema — validates nodes, edges, metadata
- [ ] T8: BacktestConfig schema — validates required fields, ranges
- [ ] T9: Indicator params schema — validates period ranges, source types

### Integration
- [ ] T10: Full flow — create strategy → run backtest → get results → compare

## Acceptance Criteria (from Spec)
- [ ] AC1: Monorepo structure with pnpm workspaces
- [ ] AC2: Backend with FastAPI, SQLAlchemy 2.x async, pytest + httpx
- [ ] AC3: Frontend with React 18, TypeScript, Vite, Lightweight Charts
- [ ] AC4: PostgreSQL schema for all core entities
- [ ] AC5: MCP Server structure integrated with FastAPI
- [ ] AC6: Shared types for Strategy Graph, Indicators, Market Data
- [ ] AC7: Tooling: ESLint, Prettier, Ruff, MyPy, Husky
- [ ] AC8: Docker Compose for local dev (PostgreSQL, Redis, MinIO)
- [ ] AC9: AGENTS.md created (done)
- [ ] AC10: CI/CD pipeline skeleton (GitHub Actions)
- [ ] AC11: All services run with `pnpm dev` / `docker-compose up`

## Risks & Mitigations
- **Python 3.13 compatibility** → Pin to 3.12 if wheels missing; test early
- **Lightweight Charts + React Flow Canvas conflict** → Test rendering both on same page early
- **MCP service sharing** → Ensure MCP imports from `src/services`, not direct DB
- **Parquet performance** → Use Polars lazy evaluation; test with 1M+ rows
- **Monorepo path aliases** → Configure `paths` in tsconfig.base.json; verify imports work

## Rollback Plan
If critical issues: `git checkout main && docker-compose down -v && pnpm install`

## Notes
- Follow TDD: write failing test → implement → refactor
- Commit format: `feat(foundation): <description>`
- Push to `dev` branch only; PR to `dev` with spec link