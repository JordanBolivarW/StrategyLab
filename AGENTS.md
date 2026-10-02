# Project Agents Configuration

## Project Overview
**Name:** Strategy Lab MCP
**Description:** Visual platform for creating, testing, iterating and improving trading strategies with backtesting and AI agents via MCP
**Type:** Monorepo (Quantitative Research Platform)

## Tech Stack
- **Language:** Python (3.13), TypeScript (5.x)
- **Framework:** FastAPI (0.115+), React (18+), Vite (5+)
- **Database:** PostgreSQL (16+), Parquet for market data
- **Testing:** pytest + httpx (backend), Vitest + React Testing Library (frontend)
- **Linting:** Ruff (Python), ESLint + TypeScript ESLint (frontend)
- **Formatting:** Ruff format (Python), Prettier (frontend)

## Architecture
- **Pattern:** Modular monorepo with shared packages
- **Key Directories:**
  - `apps/backend` — FastAPI + SQLAlchemy 2.x async + MCP Server
  - `apps/frontend` — React + TypeScript + Vite + React Flow + Lightweight Charts
  - `packages/shared` — Shared TypeScript types (Strategy Graph, Indicators, Market Data, Backtest, MCP)
  - `packages/python-shared` — Shared Pydantic schemas
  - `docker/` — Docker Compose for local infrastructure

## Development Commands
```bash
# Development (from root)
pnpm dev                    # Start all services (frontend + backend)
pnpm dev:frontend           # Frontend only (Vite HMR)
pnpm dev:backend            # Backend only (uvicorn --reload)
pnpm docker:up              # Start PostgreSQL, Redis, MinIO, pgAdmin
pnpm docker:down            # Stop infrastructure

# Testing
pnpm test                   # Run all tests
pnpm test:backend           # pytest backend tests
pnpm test:frontend          # Vitest frontend tests
pnpm test:e2e               # Playwright E2E tests

# Linting
pnpm lint                   # Lint all packages
pnpm lint:backend           # Ruff check
pnpm lint:frontend          # ESLint check

# Type Checking
pnpm typecheck              # Type check all packages
pnpm typecheck:backend      # MyPy
pnpm typecheck:frontend     # tsc --noEmit

# Build
pnpm build                  # Build all packages
pnpm build:frontend         # Vite build
pnpm build:backend          # Python package build (if needed)

# Database
pnpm db:migrate             # Run Alembic migrations
pnpm db:revision            # Create new migration
pnpm db:reset               # Drop and recreate database

# MCP
pnpm mcp:dev                # Start MCP server in dev mode
```

## Coding Standards
- **Naming:** snake_case (Python), camelCase (TypeScript), PascalCase (components/classes)
- **Imports:** Absolute imports with path aliases (`@/`, `@strategy-lab/shared`)
- **TypeScript:** Strict mode true, no `any`, no `unknown` without narrowing
- **Components:** Functional components with hooks, no classes
- **State:** TanStack Query (server), Zustand (client UI state)
- **Python:** Type hints everywhere, Pydantic for validation, async/await for I/O

## Testing
- **Unit:** pytest (backend services/engines), Vitest (frontend utils/hooks/components)
- **Integration:** pytest + httpx + testcontainers (API endpoints), Vitest + MSW (frontend API)
- **E2E:** Playwright (critical flows: create strategy → run backtest → view results)
- **Coverage Target:** 80% backend, 70% frontend

## Git Workflow
- **Main Branch:** main
- **Develop Branch:** dev
- **Feature Prefix:** feat/
- **Commit Format:** Conventional Commits (`feat(scope): description`, `fix(scope): description`)

## AI Assistant Instructions
This is a **Spec-Driven Development (SDD)** project. Never implement without an approved spec.
- Always read the spec in `SPECS/` before implementing
- Follow TDD: Red → Green → Refactor
- Write tests for all acceptance criteria
- Run lint/typecheck/test before committing
- The MCP server shares the same core services as the REST API — never bypass the service layer

## Forbidden Patterns
- [ ] Direct database access from MCP or API routes (must use service layer)
- [ ] `any` type in TypeScript without justification
- [ ] Sync database calls in async FastAPI routes
- [ ] Hardcoded configuration (use Pydantic Settings)
- [ ] Business logic in API routes (delegate to services)
- [ ] Mutable global state
- [ ] Skipping tests for new features

## Preferred Patterns
- [ ] Dependency injection via FastAPI `Depends()`
- [ ] Pydantic models for all API request/response
- [ ] SQLAlchemy async sessions with `async with`
- [ ] Polars for data processing, NumPy for calculations
- [ ] React Flow for Strategy Graph, Lightweight Charts for financial charts
- [ ] Zod schemas for runtime validation (shared with backend Pydantic)
- [ ] Feature flags for gradual rollouts
- [ ] Structured logging with structlog

## Environment Variables
```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/strategy_lab
DATABASE_URL_SYNC=postgresql://user:pass@localhost:5432/strategy_lab

# Redis
REDIS_URL=redis://localhost:6379/0

# MinIO (S3-compatible for Parquet files)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=market-data

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000

# MCP
MCP_SERVER_NAME=strategy-lab
MCP_SERVER_VERSION=0.1.0

# Security
SECRET_KEY=change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Development
DEBUG=true
LOG_LEVEL=INFO
```

## Useful References
- [Architecture Docs](docs/architecture.md)
- [API Docs](http://localhost:8000/docs) (when running)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [Lightweight Charts](https://tradingview.github.io/lightweight-charts/)
- [React Flow](https://reactflow.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)
- [Polars](https://pola.rs/)