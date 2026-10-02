# Strategy Lab MCP

Visual platform for creating, testing, iterating and improving trading strategies with backtesting and AI agents via MCP.

## Quick Start

```bash
# 1. Install dependencies
pnpm install

# 2. Start infrastructure (PostgreSQL, Redis, MinIO)
pnpm docker:up

# 3. Run database migrations
pnpm db:migrate

# 4. Start all services (frontend + backend)
pnpm dev
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050 (admin@strategy-lab.com / admin)
- MinIO Console: http://localhost:9001 (minioadmin / minioadmin)

## Project Structure

```
strategy-lab/
├── apps/
│   ├── backend/          # FastAPI + SQLAlchemy + MCP Server
│   └── frontend/         # React + TypeScript + Vite + React Flow
├── packages/
│   ├── shared/           # Shared TypeScript types
│   └── python-shared/    # Shared Pydantic schemas
├── docker/
│   └── docker-compose.yml
├── SPECS/                # Feature specifications
├── docs/                 # Documentation
└── AGENTS.md             # AI assistant configuration
```

## Development Commands

```bash
# Development
pnpm dev                    # Start all services
pnpm dev:frontend           # Frontend only (Vite HMR)
pnpm dev:backend            # Backend only (uvicorn --reload)

# Testing
pnpm test                   # All tests
pnpm test:backend           # Backend tests (pytest)
pnpm test:frontend          # Frontend tests (Vitest)
pnpm test:e2e               # E2E tests (Playwright)

# Linting
pnpm lint                   # All packages
pnpm lint:backend           # Ruff
pnpm lint:frontend          # ESLint

# Type Checking
pnpm typecheck              # All packages
pnpm typecheck:backend      # MyPy
pnpm typecheck:frontend     # tsc --noEmit

# Database
pnpm db:migrate             # Run Alembic migrations
pnpm db:revision            # Create new migration
pnpm db:reset               # Drop and recreate database

# Infrastructure
pnpm docker:up              # Start PostgreSQL, Redis, MinIO, pgAdmin
pnpm docker:down            # Stop infrastructure

# MCP
pnpm mcp:dev                # Start MCP server in dev mode
```

## Tech Stack

- **Backend**: FastAPI, Python 3.13, SQLAlchemy 2.x (async), Pydantic v2, Alembic
- **Frontend**: React 18, TypeScript 5.x, Vite, React Flow, Lightweight Charts, Tailwind CSS
- **Database**: PostgreSQL 16+, Parquet for market data
- **Testing**: pytest + httpx (backend), Vitest + React Testing Library (frontend), Playwright (E2E)
- **Linting**: Ruff (Python), ESLint + TypeScript ESLint (frontend)
- **Formatting**: Ruff format (Python), Prettier (frontend)

## Architecture

```
                    ┌─────────────────┐
                    │      WEB        │
                    │ React + TS      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    CORE API     │
                    │    FastAPI      │
                    └────────┬────────┘
                             │
        ┌────────────────────┼─────────────────────┐
        │                    │                     │
        ▼                    ▼                     ▼
 STRATEGY ENGINE       BACKTEST ENGINE       MARKET DATA
        │                    │                     │
        ▼                    ▼                     ▼
   VERSIONING            ANALYTICS           DATASETS
        │
        ▼
  OPTIMIZATION


                    ┌─────────────────┐
                    │   MCP SERVER    │
                    └────────┬────────┘
                             │
          ┌──────────────────┼─────────────────┐
          │                  │                 │
          ▼                  ▼                 ▼
       ChatGPT            OpenCode          Claude
```

## MCP Integration

Strategy Lab exposes its capabilities via MCP (Model Context Protocol). External AI agents can:

- Discover markets, indicators, and node types
- Create, clone, update, and validate strategies
- Run backtests and retrieve results
- Compare strategies and versions
- Create and manage experiments

See [SPECS/project-foundation.md](SPECS/project-foundation.md) for the full MCP tool specification.

## Contributing

1. Read [AGENTS.md](AGENTS.md) for coding standards and workflow
2. Follow Spec-Driven Development: write spec → get approval → implement
3. Use Conventional Commits: `feat(scope): description`
4. Run `pnpm lint && pnpm typecheck && pnpm test` before committing

## License

MIT