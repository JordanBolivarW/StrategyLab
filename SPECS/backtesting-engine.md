# Spec: Backtesting Engine + Backtests API

**Status:** draft (pending review / approval)
**Gates:** phases 4 (Backtest Engine fixes) and 5 (Backtests API) of `docs/orden-ejecucion.md`
**Supersedes:** nothing. Complements `SPECS/strategy-graph.md` (§14 deferred items) for everything backtest-related. `project-foundation.md` remains valid for infra, stack, and roadmap.

## 1. User Story

As a trader (or an external AI agent via MCP), I want to launch a backtest of a stored strategy version over market data and read back its metrics, equity curve, and trades, so that I can evaluate the strategy before trading it.

## 2. Acceptance Criteria

- [ ] `POST /api/v1/backtests` with a valid `strategy_version_id` + config returns `201` with `status: "pending"`, then executes and reaches a terminal status (`completed` | `failed`)
- [ ] `GET /api/v1/backtests/{id}` returns metrics + equity curve + trades for completed runs
- [ ] `GET /api/v1/backtests` lists runs with pagination (`items`, `total`) and filters (`strategy_id`, `status`)
- [ ] `DELETE /api/v1/backtests/{id}` removes a run (`204`); unknown id → `404`
- [ ] Creating with an unknown `strategy_version_id` → `404`; malformed body → `422`
- [ ] Failed runs store `status: "failed"` + `error` message instead of raising to the client
- [ ] `tests/test_backtests.py` (new) passes: create → completed flow, get, list, delete, 404/422 cases
- [ ] Manual flow in `/docs` works: create strategy → launch backtest → read results (phase-5 exit criterion in `docs/orden-ejecucion.md`)
- [ ] Suite stays green: 48 existing tests keep passing

## 3. Source-of-Truth Decisions (proposed)

1. **Pydantic (`apps/backend/src/schemas`) is canonical** for `BacktestConfig`, `BacktestCreate`, `BacktestMetrics`, `EquityPoint`, `Trade`, `BacktestResponse` — same rule as `strategy-graph.md` §3.
2. **Service layer owns execution** (`apps/backend/src/services/backtest_service.py`, new). Routes in `apps/backend/src/api/v1/backtests.py` stay thin (no direct DB access — AGENTS.md forbidden pattern). MCP will reuse the same service in phase 6.
3. **`BacktestEngine.run` stays synchronous** (phase-4 decision). Execution from the API uses FastAPI `BackgroundTasks` (which runs sync callables in a threadpool via `anyio.to_thread`), so the event loop is never blocked. No Celery/RQ in this phase.
4. **Market data source: `load_market_data` with mock fallback** (`src/services/market_data.py`). If no Parquet file exists for `(market, timeframe)`, `generate_mock_data` supplies 1000 bars. Real data ingestion is out of scope (later `market-data` spec).
5. **`config.strategy_id` is canonicalized from the version.** `BacktestCreate` carries `strategy_version_id` (authoritative) plus `config` (which contains its own `strategy_id`). If they disagree, the service **overwrites** `config.strategy_id` with the version's `strategy_id` instead of failing — the version row is the source of truth, the config copy is just a snapshot for reproducibility.

## 4. Status Lifecycle

```
pending → running → completed
                ↘ failed (error stored, never raised to client)
```

- `pending`: row created, execution enqueued.
- `running`: execution started (`started_at` set).
- `completed`: metrics + equity_curve + trades stored (`completed_at` set).
- `failed`: `error` message stored (`completed_at` set), result columns stay `NULL`.
- No other transitions. No rerun endpoint in this phase (create a new run instead).

## 5. API Contract

### POST /api/v1/backtests → 201

Request (`BacktestCreate`):
```json
{
  "strategy_version_id": "uuid-of-version",
  "config": {
    "strategy_id": "uuid-of-strategy",
    "market": "BTCUSDT",
    "timeframe": "1h",
    "start_date": "2024-01-01T00:00:00",
    "end_date": "2024-06-01T00:00:00",
    "initial_capital": 10000.0,
    "commission": 0.001,
    "slippage": 0.0005
  }
}
```

Response (`BacktestResponse`, `status: "pending"`; `metrics`/`equity_curve`/`trades` are `null`).

Execution starts via `BackgroundTasks` immediately after commit. With Starlette's `TestClient`, background tasks run before the response returns, so tests observe the terminal status directly.

### GET /api/v1/backtests?strategy_id=&status=&limit=20&offset=0 → 200

```json
{ "items": [BacktestResponse], "total": 3 }
```

- `strategy_id`: optional UUID filter. `status`: optional, one of `pending|running|completed|failed` (anything else → `422`).
- `limit`: 1–100 (default 20). `offset`: ≥ 0 (default 0). Ordered by `created_at` desc.

### GET /api/v1/backtests/{id} → 200 | 404

Full `BacktestResponse` including metrics, equity curve, and trades when `completed`.

### DELETE /api/v1/backtests/{id} → 204 | 404

Hard delete (no versioning for runs — runs are immutable result snapshots, unlike strategies).

## 6. Execution Semantics (service)

`backtest_service.execute_backtest(backtest_id)`:

1. Load run row → set `running` + `started_at`, commit.
2. Load `StrategyVersion.graph` (snapshot at creation time — later strategy edits never affect a queued run).
3. `market_data = await load_market_data(market, timeframe, start_date, end_date)` (mock fallback per §3.4).
4. `result = BacktestEngine().run(graph, config, market_data)` — sync call, CPU-bound (Polars).
5. Validate strategy first inside `run` (existing behavior): invalid graph → `ValueError` → caught → `failed` + message.
6. Serialize `metrics`/`equity_curve`/`trades` via Pydantic `model_dump(mode="json")` into the JSON columns; set `completed` + `completed_at`, commit.
7. On any exception: rollback, set `failed` + `str(exc)` (truncated to 2000 chars) + `completed_at`, commit.

Each step uses its own session handling so a failure never leaves the row stuck in `running` (except a hard process kill, accepted for this phase — no watchdog).

## 7. Engine Fixes Included (phase-4 leftovers)

1. **`run_backtest` await bug** (`backtest_engine.py:339`): `return await engine.run(...)` raises `TypeError` at runtime because `run` is sync since phase 4 (no test covers it — latent). Fix: drop the `await`. `run_backtest` stays `async` (it awaits `load_market_data`, real I/O).
2. **No other engine changes.** Known limitation (documented, not fixed): `_execute_strategy` never evaluates `action.*` nodes, so runs yield 0 trades; metrics/equity degenerate but well-formed. Real signal execution belongs to a later engine spec.

## 8. Type Alignment (Pydantic ↔ Zod)

Verified against `packages/shared/src/types/backtest.ts`:

| Field | Pydantic | Zod | Verdict |
|---|---|---|---|
| `config.strategy_id` | `UUID` | `string().uuid()` | aligned |
| `config.market/timeframe` | `str` (no length check) | `min(1).max(50/20)` | backend looser — accepted (backend never rejects what Zod accepts) |
| `config.start_date/end_date` | `str` | `string().datetime()` | backend looser — accepted, same direction |
| `config.initial_capital/commission/slippage` | `gt(0)/[0,1]/[0,1]` + defaults | `positive/min/max` + same defaults | aligned |
| `status` | free `str` | enum `pending/running/completed/failed` | backend looser — accepted; service only ever writes the 4 enum values (§4) |
| `metrics` | all required except sharpe/sortino/calmar | same + extra optionals | backend subset — accepted (extra Zod fields optional) |

**Known drift (out of scope, frontend phase 7):**
- Pydantic `BacktestConfig` lacks `position_sizing`, `stop_loss`, `take_profit` (Zod has them optional). Engine ignores them today; adding them is a later engine spec.
- Engine emits `EquityPoint.timestamp` / `Trade.entry_time` via `str(ts)` (e.g. `"2024-01-01 00:00:00"`), which fails Zod `string().datetime()`. Normalizing to ISO-8601 is a later fix; Pydantic accepts any `str` today.

## 9. Testing Strategy (TDD)

New file `apps/backend/tests/test_backtests.py` (mirrors `test_strategies.py`, same SQLite-override conftest):

- `test_create_backtest` — POST valid → `201`, `status` terminal (`completed` under TestClient), `strategy_id` matches version's strategy.
- `test_create_backtest_canonicalizes_strategy_id` — config with a *different* (valid UUID) `strategy_id` → `201`, stored config uses the version's id (§3.5).
- `test_create_backtest_unknown_version` — random UUID → `404`.
- `test_create_backtest_invalid_body` — missing config → `422`.
- `test_get_backtest` — round-trip; completed run includes `metrics` with `initial_capital == 10000.0`, non-empty `equity_curve`.
- `test_list_backtests` — pagination + `status` filter.
- `test_delete_backtest` — `204`, then `404` on get.
- `test_get_backtest_not_found` — `404`.

Fixtures reuse a minimal valid graph (data.close → indicator.ema → comparator + action.buy/close, i.e. entry + exit so engine validation passes). Market data comes from the mock generator (no files needed).

## 10. Non-Functional Requirements

- **Perf:** mock path = 1000 bars; engine is single-threaded Polars, well under 5 s per run on dev hardware. `BackgroundTasks` keeps the POST response fast (< 200 ms to `201`).
- **Safety:** runs never mutate strategies/versions (read-only graph snapshot). Delete cascades via FK (`ondelete=CASCADE`).
- **Concurrency:** SQLite (tests) serializes writes; Postgres uses row-level locking per run id. Two runs of the same version are independent rows — no shared mutable state.
- **Logging:** `structlog` info on transitions (`backtest_id`, `status`); exception logged with traceback on `failed`.

## 11. Rollout Plan

1. Merge behind no flag (new endpoints only; zero impact on existing routes).
2. Verify manual flow in `/docs` against local PG (phase-5 exit criterion).
3. Phase 6 (MCP) consumes `backtest_service` — no route changes needed.

Rollback: revert the single commit (new files + route bodies); `backtests` table already exists via `init_db`/migrations, no schema change in this spec.

## 12. Out of Scope (explicitly NOT this spec)

- Real market-data ingestion / Parquet management (`market-data` spec).
- Live progress streaming (WS) — poll `GET {id}` instead.
- Rerun / cancel / bulk delete endpoints.
- Optimization / walk-forward / experiments (`Experiment` model untouched).
- Signal execution that actually opens trades (engine limitation §7.2).
- MCP wiring (phase 6, separate spec) and frontend (phase 7).
- `datetime.utcnow()` / `Dataset.metadata` warnings (phase 8 hardening).

## 13. Verification

```powershell
cd D:\StrategyLab\apps\backend
.venv\Scripts\python.exe -m pytest tests/test_backtests.py -q          # new, must be green
.venv\Scripts\python.exe -m pytest --no-header -p no:cacheprovider      # full suite: 48 + new, 0 failed
```

Manual: `/docs` → `POST /strategies` → `POST /backtests` → `GET /backtests/{id}` → metrics present.
