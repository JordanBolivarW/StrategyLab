# Strategy Lab - Reporte de estado actual

**Fecha:** 2026-10-04
**Rama:** `main`
**Metodo:** smoke test real (instalacion de dependencias, arranque de servicios, pruebas de endpoints, ejecucion de suites de tests)

## 1. Resumen ejecutivo

El proyecto **si se puede correr** en local (Windows). En esta sesion se verifico:

- Backend (FastAPI) corriendo y sano en `http://localhost:8000`
- Frontend (Vite + React) corriendo en `http://localhost:5173`
- PostgreSQL 16 del sistema en `localhost:5432` con base `strategy_lab` y sus 6 tablas creadas
- Las unicas areas realmente implementadas son **Market Data (REST)** y **MCP de solo lectura**
- El resto (Strategies REST, Backtests REST, engines de indicadores/backtest, auth) sigue en estado **stub**

Estado de tests backend: **25 passed / 10 failed / 13 errors** (1.8s).

## 2. Entorno verificado

| Componente | Version / valor | Nota |
|---|---|---|
| OS | Windows (PowerShell 5.1) | `&&` no funciona en PS 5.1, usar `;` |
| Python | 3.13.1 | venv en `apps/backend/.venv` |
| pnpm | 9.0.0 | workspaces OK |
| Node | 24.19.0 | |
| PostgreSQL | 16.15 (servicio del sistema) | `localhost:5432`, usuario `postgres`/`postgres` |
| Docker | **no disponible** | `pnpm docker:up` no sirve en esta maquina; no bloquea el smoke test |
| Backend | `src/main:app` (no `app.main:app`) | la estructura real es `apps/backend/src/` |
| Frontend | `apps/frontend`, 3 rutas | `/`, `/strategy/:id?`, `/backtest/:id` |

### Credenciales locales creadas para el proyecto

- Usuario: `strategy_lab` / clave `strategy_lab`
- Base: `strategy_lab` (ambos creados con `psql -U postgres` durante el smoke test)
- No se necesita `.env`: los defaults de `src/config.py` ya apuntan a `postgresql+asyncpg://strategy_lab:strategy_lab@localhost:5432/strategy_lab`

## 3. Como arrancar (comandos verificados)

```powershell
# 1. Dependencias frontend/monorepo (desde la raiz)
pnpm install

# 2. Dependencias backend (una sola vez)
cd apps\backend
python -m venv .venv
.\.venv\Scripts\pip.exe install -e .
# OJO: ver seccion 4, el pyproject no instala las deps de runtime por si solo

# 3. Backend (puerto 8000)
cd apps\backend
.\.venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8000

# 4. Frontend (puerto 5173)
pnpm --filter @strategy-lab/frontend dev

# 5. Verificar
# http://localhost:8000/health  -> {"status":"ok","service":"strategy-lab-backend"}
# http://localhost:5173         -> HTTP 200
```

## 4. Problemas detectados y corregidos durante el smoke test

| # | Problema | Solucion aplicada |
|---|---|---|
| 1 | `pip install -e .` no instala las dependencias de runtime: en `apps/backend/pyproject.toml` las `dependencies` estan **anidadas dentro de `[tool.uv]`**, fuera del alcance de PEP 621 | Instaladas manualmente con pip (fix real pendiente: mover `dependencies` al nivel `[project]`) |
| 2 | `ImportError: SQLAlchemy asyncio requires greenlet` | `pip install "sqlalchemy[asyncio]"` |
| 3 | No existian el rol ni la base `strategy_lab` en Postgres | Creados con psql (server 16 local) |
| 4 | Tests fallaban con `ModuleNotFoundError: aiosqlite` | `pip install aiosqlite` |
| 5 | El módulo de entrada real es `src.main:app` corriendo desde `apps/backend` (los docs/AGENTS mencionan `app.main`) | Lanzar uvicorn con cwd=`apps/backend` y target `src.main:app` |

## 5. Features realmente implementadas (verificadas con peticiones reales)

### Funcionan

- **Market Data REST**
  - `GET /api/v1/markets` -> 4 simbolos (BTCUSDT, ETHUSDT, SPY, EURUSD)
  - `GET /api/v1/markets/{symbol}`, `GET /api/v1/markets/{symbol}/data`, `POST /api/v1/markets/{symbol}/import`
- **MCP sobre HTTP (lectura)** - el modulo mas completo del backend
  - `GET /api/v1/mcp/tools` -> lista de tools con `inputSchema`
  - `POST /api/v1/mcp/tools/call` probado: `get_platform_capabilities`, `list_markets`, `list_indicators` (devuelve sma, ema, rsi, macd, atr, bollinger_bands), `list_node_types`, `describe_*`
- **Esquema de datos** - 6 tablas creadas automaticamente en el arranque: `users`, `strategies`, `strategy_versions`, `backtests`, `datasets`, `experiments`
- **Frontend UI** - Vite sirve las 3 paginas (Dashboard, StrategyBuilder, BacktestResults)

### No funcionan (stubs confirmados)

- **`src/api/v1/strategies.py`** (513 bytes): solo imports y `router = APIRouter()` vacio. **Cero endpoints** (se esperan: list/create/get/update/delete/versions/clone/validate). Genera 10 tests fallidos.
- **`src/api/v1/backtests.py`** (595 bytes): mismo caso, router vacio.
- **MCP de escritura**: `list_strategies` devuelve `Tool 'list_strategies' not implemented yet`.
- **`src/services/indicator_engine.py`**: 13 errores de tests por incompatibilidad con la API de **Polars v1.x** instalada.
- **`src/services/backtest_engine.py`**: errores de validacion Pydantic en los tests.
- **Auth**: no existe router ni servicio de autenticacion (aunque si hay modelo `User`).

### Conteo por archivo (tamano como indicador de avance)

```
src/api/v1/strategies.py     513 bytes  -> stub
src/api/v1/backtests.py      595 bytes  -> stub
src/api/v1/markets.py      2388 bytes   -> implementado
src/api/v1/mcp.py         20777 bytes   -> implementado (lectura)
```

## 6. Veredicto sobre los specs

- Existe **un solo spec**: `SPECS/project-foundation.md` (bien definido, pero de alcance amplio: mezcla infraestructura y contrato de dominio).
- Los demas specs citados en `AGENTS.md` (`strategy-graph`, `backtesting-engine`, `mcp-server`, `ui-graph-editor`, `api-contracts`, `market-data`) **no existen todavia**.
- En la practica, los **tests de `apps/backend/tests/` funcionan como contrato de aceptacion** por feature.
- El foundation esta cumplido en estructura; lo pendiente es la implementacion de los endpoints/services.

## 7. Siguiente paso

Ver `docs/orden-ejecucion.md` para el orden de fases recomendado (Relleno de stubs por dependencias, siguiendo SPEC -> Plan -> Implement -> Verify).
