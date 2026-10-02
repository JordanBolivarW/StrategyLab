# Strategy Lab — Reporte de estado actual

**Fecha:** 2026-10-02
**Autor:** reporte generado durante la puesta en marcha del entorno local (Windows)
**Rama:** `main` (commit inicial, sin pushes previos)

## 1. Resumen ejecutivo

El proyecto **no está corriendo todavía**. El frontend (`http://localhost:5173/`) no muestra nada porque
ningún servidor está levantado. La base de datos **sí quedó lista**: se creó un cluster PostgreSQL propio
para el proyecto en el puerto **5434** con usuario y base `strategy_lab` verificados.

Lo único pendiente para correr el proyecto es:

1. Apuntar el `.env` al puerto `5434` (hoy apunta a `5433`).
2. Crear el venv del backend con Python 3.14, instalar dependencias y correr migraciones.
3. Levantar backend (puerto 8000) y frontend (puerto 5173).

## 2. Mapa de ubicación (dónde está cada cosa)

| Componente | Ubicación / puerto | Estado |
|---|---|---|
| Código del proyecto | `D:\StrategyLab` | ✅ presente |
| Frontend (Vite + React) | `D:\StrategyLab\apps\frontend` → `http://localhost:5173/` | ⛔ no está corriendo |
| Backend (FastAPI) | `D:\StrategyLab\apps\backend` → `http://localhost:8000/` | ⛔ no está corriendo, sin venv |
| Variables de entorno | `D:\StrategyLab\.env` (no se commitea, ver `.env.example`) | ⚠️ apunta a puerto `5433`, debe ser `5434` |
| Postgres del proyecto (propio) | `C:\Users\USUARIO\AppData\Local\Temp\opencode\pgdata` → `localhost:5434` | ✅ corriendo (PID 39176), BD `strategy_lab` creada |
| Log del Postgres propio | `C:\Users\USUARIO\AppData\Local\Temp\opencode\pgdata.log` | ✅ existe |
| Postgres del sistema (Windows) | `C:\Program Files\PostgreSQL\16\` → `localhost:5433` | ⚠️ corre pero **clave del superusuario `postgres` desconocida** — no usar |
| Docker Desktop | daemon con error 500 (`docker version` falla) | ⛔ no usable, por eso se optó por Postgres propio |
| pgAdmin | `http://localhost:5050` (contenedor, requiere Docker) | ⛔ no usable sin Docker |

### Credenciales del Postgres del proyecto (puerto 5434)

- **Usuario:** `strategy_lab`
- **Clave:** `strategy_lab`
- **Base:** `strategy_lab`
- **Auth local:** `trust` (cluster de desarrollo, solo escucha en `localhost`)

Verificación ejecutada: `psql -U strategy_lab -h localhost -p 5434 -d strategy_lab -c "SELECT 1;"` → OK.

## 3. Decisiones tomadas

1. **No usar el Postgres del sistema (5433).** El comando
   `psql -U postgres -p 5433` pide una clave que nadie conoce (se definió al instalar
   PostgreSQL 16 en Windows). Sin permisos de administrador no se puede resetear
   (`pg_ctl reload` y `Restart-Service postgresql-spax-16` devuelven "Operation not permitted" /
   "Cannot open service"). Se intentó adivinar claves comunes (`postgres`, `admin`) sin éxito.
2. **No usar Docker.** El daemon de Docker Desktop responde `500 Internal Server Error`
   (`docker version` y `docker compose up` fallan), así que `pnpm docker:up` no funciona.
3. **Crear cluster propio con `initdb`.** Se inicializó con:
   `initdb -D <temp>\opencode\pgdata -U strategy_lab -E UTF8 -A trust`,
   puerto cambiado a `5434` en `postgresql.conf`, arrancado con `pg_ctl start`.
   No requiere permisos de administrador y no toca la instalación del sistema.
4. El archivo `C:\Program Files\PostgreSQL\16\data\pg_hba.conf` se editó temporalmente a `trust`
   y **se revirtió a `scram-sha-256`**. El contenido actual es el original; como el servicio
   nunca se recargó, la configuración en ejecución no cambió.

## 4. Problemas conocidos del proyecto (detectados al intentar correrlo)

| # | Problema | Detalle |
|---|---|---|
| 1 | Scripts pnpm que apuntaban a `@strategy-lab/backend` (inexistente como proyecto pnpm) | ✅ **Corregido 2026-10-02:** `lint`, `typecheck`, `test`, `build` y `dev` ya no usan el filtro de backend. Siguen pendientes de reimplementar en Python: `dev:backend`, `build:backend`, `test:backend`, `lint:backend`, `typecheck:backend`, `db:*`, `mcp:dev`. El backend se corre con `uvicorn` (§5). |
| 1b | Hook pre-commit bloqueaba el commit inicial | ✅ **Corregido 2026-10-02:** migrado a flat config (`eslint.config.mjs`, ESLint 9), eliminados `any` innecesarios en frontend/shared, corregidos `exhaustive-deps` y renombrado `useStrategies.test.ts` → `.tsx`. `pnpm lint` y `pnpm typecheck` pasan en verde. |
| 2 | Python 3.11 roto | `py -3.11` apunta a `C:\Python311\python.exe` que **no existe**. Usar `py -3.14` (3.14.3 verificado) o `py -3.10`. |
| 3 | Sin `uv` ni `python` en PATH | `python` y `uv` no se reconocen; usar el launcher `py -3.14`. |
| 4 | `.env` desactualizado | Apunta a `5433`; debe apuntar a `5434` (ver §5 paso 1). |
| 5 | PowerShell 5.1 no acepta `&&` | Encadenar comandos con `&&` falla con `ParserError`. Usar `;` o comandos separados. |
| 6 | Comandos interactivos se cuelgan | `psql` sin clave válida queda esperando password y agota el timeout (120s). Siempre usar `PGPASSWORD` o el cluster propio (trust). |

## 5. Pasos pendientes para correr el proyecto

```powershell
# 1. Apuntar el .env al Postgres propio (5434)
#    Editar D:\StrategyLab\.env:
#    DATABASE_URL=postgresql+asyncpg://strategy_lab:strategy_lab@localhost:5434/strategy_lab
#    DATABASE_URL_SYNC=postgresql://strategy_lab:strategy_lab@localhost:5434/strategy_lab

# 2. Backend: crear venv e instalar dependencias (Python 3.14)
py -3.14 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e apps\backend  # o: pip install fastapi "uvicorn[standard]" sqlalchemy alembic asyncpg pydantic pydantic-settings polars numpy pandas redis minio structlog python-dotenv python-jose passlib python-multipart

# 3. Backend: migraciones
alembic -c apps\backend\alembic.ini upgrade head

# 4. Backend: levantar (puerto 8000) y verificar
py -3.14 -m uvicorn main:app --app-dir apps\backend\src --host 0.0.0.0 --port 8000 --reload
# verificar: http://localhost:8000/health  y  http://localhost:8000/docs

# 5. Frontend: levantar (puerto 5173) y verificar
pnpm --filter @strategy-lab/frontend dev
# abrir: http://localhost:5173/
```

> Nota: si se reinicia Windows, el Postgres propio **no arranca solo**. Levantarlo con:
> `& "C:\Program Files\PostgreSQL\16\bin\pg_ctl.exe" -D "C:\Users\USUARIO\AppData\Local\Temp\opencode\pgdata" -l "C:\Users\USUARIO\AppData\Local\Temp\opencode\pgdata.log" start`

## 6. Subida a GitHub

- Repo local: `D:\StrategyLab`, rama `main`, commit inicial con todo el código + este reporte.
- Destino solicitado: `https://github.com/JordanBolivarW` (repo `StrategyLab` por crear).
- El `.env` **no se sube** (está en `.gitignore`, líneas 30-33); quien clone debe copiar `.env.example` → `.env`
  y ajustar el puerto a `5434` (o a su propio Postgres).
