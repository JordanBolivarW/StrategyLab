# Strategy Lab Backend

FastAPI + SQLAlchemy 2.x async + MCP Server

## Setup

```bash
# From monorepo root
cd apps/backend

# Install dependencies (using uv or pip)
pip install -e ".[dev]"

# Or with uv (faster)
uv pip install -e ".[dev]"
```

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload --port 8000

# Or from monorepo root
pnpm dev:backend
```

## Database

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"

# Reset database (dev only)
alembic downgrade base && alembic upgrade head
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_strategies.py -v
```

## Linting & Type Checking

```bash
# Lint with Ruff
ruff check src tests

# Format with Ruff
ruff format src tests

# Type check with MyPy
mypy src
```

## Project Structure

```
apps/backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Pydantic Settings
│   ├── database.py          # SQLAlchemy async engine/session
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas (API)
│   ├── api/                 # API routes
│   │   ├── v1/
│   │   │   ├── strategies.py
│   │   │   ├── backtests.py
│   │   │   ├── markets.py
│   │   │   └── mcp.py
│   └── services/            # Business logic
│       ├── strategy_engine.py
│       ├── indicator_engine.py
│       ├── backtest_engine.py
│       └── market_data.py
├── tests/                   # Pytest tests
├── migrations/              # Alembic migrations
├── pyproject.toml
└── alembic.ini
```

## Environment Variables

See `.env.example` in monorepo root.

Key variables:
- `DATABASE_URL` - PostgreSQL async connection string
- `REDIS_URL` - Redis connection string
- `MINIO_*` - MinIO/S3 configuration
- `SECRET_KEY` - JWT secret
- `DEBUG` - Enable debug mode

## API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## MCP Tools

Available at `/api/v1/mcp/tools`:
- Discovery: `get_platform_capabilities`, `list_markets`, `describe_market`, `list_indicators`, `describe_indicator`, `list_node_types`, `describe_node_type`
- Strategies: `list_strategies`, `get_strategy`, `create_strategy`, `clone_strategy`, `update_strategy`, `validate_strategy`, `get_strategy_versions`, `get_strategy_diff`
- Backtesting: `run_backtest`, `get_backtest`, `list_backtests`, `get_backtest_trades`, `get_backtest_metrics`
- Comparison: `compare_backtests`, `compare_strategies`, `compare_strategy_versions`

Execute tools via POST to `/api/v1/mcp/tools/call` with `{name, arguments}`.