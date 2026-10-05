# Spec: Strategy Graph

**Status:** draft (pending review / approval)
**Gates:** phases 1 (Strategy Engine) and 2 (Strategies CRUD) of `docs/orden-ejecucion.md`
**Supersedes:** the camelCase contract block in `SPECS/project-foundation.md` ("API / Interface") for everything graph-related. `project-foundation.md` remains valid for infra, stack, and roadmap.

## 1. User Story

As a trader (or an external AI agent via MCP), I want to define a strategy as a structured graph of nodes and edges with a single, unambiguous contract, so that the UI, the REST API, the backtest engine, and MCP tools all validate, store, version, and execute the exact same thing.

## 2. Acceptance Criteria

- [ ] `StrategyGraph` has exactly one canonical definition (`apps/backend/src/schemas`), and `packages/shared` validates the same graphs the backend accepts (fixtures `"1"`/`"e1"` pass on both sides)
- [ ] The 30 node types exist in exactly one registry; `StrategyEngine` and MCP discovery read from it
- [ ] `validate_graph` enforces entry + exit + DAG + known types + resolved handles, with deterministic, test-matched messages
- [ ] Drafts are storable: a graph without exit node returns `201` on create but `valid: false` on validate
- [ ] Every mutation creates a new version (decision A, §8); history is append-only
- [ ] `tests/test_backtest.py::TestStrategyEngineIntegration` (7 tests) passes
- [ ] `tests/test_strategies.py::TestStrategyAPI` (10 tests) passes (requires the `api-contracts` implementation)

## 3. Source-of-Truth Decision (approved)

**Pydantic (`apps/backend/src/schemas`) is canonical.** Consequences:

1. `packages/shared/src/types/strategy.ts` is aligned, not the other way round:
   - `StrategyNodeSchema.id`, `StrategyEdgeSchema.id/source/target`: `z.string().uuid()` → `z.string().min(1)` (backend tests use `"1"`, `"2"`, `"e1"`; Zod must accept them).
   - `StrategyGraphSchema`: remove `.min(1)` on `nodes`/`edges` (see §4, rule S1).
   - `StrategyGraphSchema.metadata`: `z.record(z.unknown()).default({})` (backend tests use `"metadata": {}`).
   - `StrategyMetadataSchema` (required `name`/`market`/`timeframe`) is **deprecated**: strategy-level fields live on the Strategy entity, not in `graph.metadata`. Keep the export for one release cycle, then delete.
2. `packages/python-shared` (`strategy_lab_shared`) has **0 imports** in the backend (verified). It is declared **canonically abandoned**: it is not kept in sync, and nothing new may import it. Physical removal is a later cleanup task, not this spec.
3. Naming is **snake_case** throughout this contract (what Pydantic and the tests already use).

## 4. Canonical Contract

```python
class StrategyGraphNode(BaseModel):
    id: str            # opaque, non-empty, unique within the graph. NOT necessarily a UUID.
    type: str          # must be a key of the node registry (§5)
    position: dict[str, float]   # editor coordinates; semantically ignored
    data: dict[str, Any]         # node parameters, validated per §7

class StrategyGraphEdge(BaseModel):
    id: str            # opaque, non-empty, unique within the graph
    source: str        # must reference an existing node id
    target: str        # must reference an existing node id
    sourceHandle: Optional[str] = None  # must be an output of the source type (§6)
    targetHandle: Optional[str] = None  # must be an input of the target type (§6)

class StrategyGraph(BaseModel):
    nodes: list[StrategyGraphNode]     # NO min-length at schema level (rule S1)
    edges: list[StrategyGraphEdge]     # NO min-length at schema level (rule S1)
    metadata: dict[str, Any] = {}      # free-form; no required keys
```

**S1 — emptiness is semantic, not syntactic.** Pydantic (and Zod) must accept `{"nodes": [], "edges": [], "metadata": {}}` at parse time. Rejecting emptiness belongs to `validate_graph`, because `test_strategy_validation_no_nodes` parses the empty graph first and expects `validate_graph` (not the schema) to return `("Graph must have at least one node")` as `errors[0]`.

**S2 — `position` is layout-only.** Validation and execution must ignore it.

**S3 — entity vs graph fields.** `name`, `description`, `market`, `timeframe` live on the Strategy entity (`StrategyBase`), never inside `graph.metadata`. `metadata` is a free-form bag (UI hints, agent notes).

## 5. Node Type Registry (single source)

The 30 node types below are the complete MVP set (matches `NodeTypeSchema`, `StrategyNodeType`, `StrategyEngine._load_node_types`, and `handle_list_node_types` — all four must converge here).

| Type | Category | Inputs | Outputs | Parameters (defaults) |
|---|---|---|---|---|
| `data.open|high|low|close|volume|timestamp` (×6) | data | — | `value` | — |
| `indicator.sma` | indicator | `source` | `value` | `period: int = 20` |
| `indicator.ema` | indicator | `source` | `value` | `period: int = 20` |
| `indicator.rsi` | indicator | `source` | `value` | `period: int = 14` |
| `indicator.macd` | indicator | `source` | `macd`, `signal`, `histogram` | `fast: int = 12`, `slow: int = 26`, `signal: int = 9` |
| `indicator.atr` | indicator | `high`, `low`, `close` | `value` | `period: int = 14` |
| `indicator.bollinger_bands` | indicator | `source` | `upper`, `middle`, `lower` | `period: int = 20`, `std_dev: float = 2.0` |
| `logic.gt|lt|gte|lte|cross_above|cross_below` (×6) | comparator | `a`, `b` | `result` | — |
| `logic.and|or` | logic | `a`, `b` | `result` | — |
| `logic.not` | logic | `a` | `result` | — |
| `action.buy|sell|long|short` (×4) | action | `condition` | `signal` | — |
| `action.close` | action | `condition` | `signal` | — |
| `risk.position_size` | risk | `risk_pct`, `equity` | `size` | `risk_pct: float` (no default) |
| `risk.stop_loss` | risk | `entry`, `pct` | `price` | `pct: float` (no default) |
| `risk.take_profit` | risk | `entry`, `pct` | `price` | `pct: float` (no default) |

**R1 — one registry module.** Implementation creates `src/services/node_registry.py` exposing `NODE_TYPES: dict[str, NodeDefinition]` with `id`, `name`, `category`, `description`, `inputs`, `outputs`, `parameters` (name, type, default, min, max). `StrategyEngine._load_node_types()` reads from it (same `category`/`inputs`/`outputs` shape as today). MCP `handle_list_node_types` / `handle_describe_node_type` **must** read from it when wired (phase 6); until then, `describe_node_type` stays stubbed and this spec does not change it.

**R2 — entry and exit sets (frozen by tests).**
Entry = `{action.buy, action.sell, action.long, action.short}`.
Exit = `{action.close, risk.stop_loss, risk.take_profit}`.

## 6. Handle Resolution (new; not validated today)

- **H1:** a present `sourceHandle` must be an output of the source node's type, else error.
- **H2:** a present `targetHandle` must be an input of the target node's type, else error.
- **H3:** absent handles are permitted (default wiring); no fan-in restriction. Signal-merging semantics belong to execution, not validation.

All existing fixtures comply (e.g. `value → a`, `result → condition`).

## 7. Parameter Validation (new; not validated today)

Node `data` is validated against the registry row:

- **P1:** unknown key → error (catches typos like `{"periodo": 20}`).
- **P2:** wrong type → error; `int` is accepted where `float` is expected (fixtures use `{"risk_pct": 1}`, `{"pct": 2}`).
- **P3:** missing keys are allowed; runtime defaults from the table in §5 apply.

All existing fixtures comply.

## 8. Validation Rules and Error Contract

`StrategyEngine.validate_graph(graph: StrategyGraph) -> tuple[bool, list[str]]` and `validate_strategy_graph(graph_dict: dict) -> tuple[bool, list[str]]` keep their signatures. Checks run in this fixed order; all errors are collected (no early return except E1, which the tests require at `errors[0]`):

| # | Rule | Message |
|---|---|---|
| E1 | no nodes | `Graph must have at least one node` |
| E2 | no edges (only when nodes exist) | `Graph must have at least one edge` |
| E3 | duplicate node id | `Duplicate node id: '<id>'` |
| E4 | duplicate edge id | `Duplicate edge id: '<id>'` |
| E5 | unknown `node.type` | `Unknown node type: <type>` |
| E6 | unknown param (P1) | `Unknown parameter '<p>' for node type '<t>'` |
| E7 | bad param type (P2) | `Invalid value for parameter '<p>' of node '<id>'` |
| E8 | no entry node (R2) | `Graph must have at least one entry node (buy/sell/long/short)` |
| E9 | no exit node (R2) | `Graph must have at least one exit node (close/stop_loss/take_profit)` |
| E10 | edge references missing node | `Edge '<e>' references unknown source node: <s>` / `... target node: <t>` |
| E11 | bad handle (H1/H2) | `Unknown output handle '<h>' for node type '<t>'` / `Unknown input handle '<h>' for node type '<t>'` |
| E12 | isolated node (no incoming and no outgoing edge) | `Node '<id>' is not connected to the graph` |
| E13 | cycle (DFS; self-loops included) | `Graph contains cycles` |

Messages E1, E2, E5, E8, E9, E13 keep their current wording: tests match `"at least one node"`, `"entry node"`, `"exit node"`, `"cycle"` literally. E10 extends the current message with the edge id (no test matches it today).

`get_execution_order` keeps Kahn's algorithm and raises `ValueError("Graph has cycles")` when the order is incomplete. `explain_strategy` keeps its output shape (tests match the substrings `ENTRY`, `POSITION MANAGEMENT`, `BUY`, `EMA`).

## 9. Versioning (decision A: every mutation versions)

- **V1 — never overwrite.** `strategy_versions` rows are append-only: no UPDATE, no DELETE except cascade on strategy delete.
- **V2 — any PATCH versions.** Changing any Strategy field (`name`, `description`, or `graph`) inserts a `StrategyVersion(version = current_version + 1)` with the full new graph and updates `strategies.current_version` in the same transaction. This is why `test_update_strategy` (name-only PATCH) expects `current_version == 2`.
- **V3 — auto changelog.** `graph` changed → `"graph updated"`; only metadata changed → `"metadata updated: <fields>"`; create → `"Initial version"`; clone → `"Cloned from '<name>'"`. An explicit `changelog` field may override it (endpoint detail, `api-contracts` scope).
- **V4 — create seeds version 1.** POST creates the Strategy with `current_version = 1` plus its first `StrategyVersion` row (`created_by="user"`).
- **V5 — clone.** Deep-copies the graph into a new Strategy with new ids, `current_version = 1`, plus its version-1 row. Name comes from the `name` query param, default `"<name> (copy)"` (`test_clone_strategy` passes `?name=Cloned Strategy` and expects `201`).
- **V6 — delete cascades.** `DELETE` removes the strategy and its versions/backtests/experiments via the existing FK cascades; subsequent GET is `404` (`test_delete_strategy`).

## 10. Drafts vs Valid Graphs

Creation endpoints accept any schema-valid graph; **semantic validity is not a precondition for storage**:

- The `test_create_strategy` graph (`data.close → ema → buy`, no exit) must return `201` **and** must validate as `(False, […exit…])`.
- `POST …/validate` returns `{valid, errors, node_count, edge_count}` with `200` for any existing strategy; it returns `404` only for an unknown id and `422` only for a malformed id. It never 4xx-es on semantic invalidity (`test_validate_strategy` asserts the keys, not the verdict).
- Execution paths (backtest `run`) require a valid graph and raise on invalid input — unchanged behavior.

## 11. Ownerless Strategies (pre-auth)

`Strategy.user_id` is `nullable=False` (`models/__init__.py:26`), but there is no auth router and `test_create_strategy` POSTs without any owner. Until the auth spec exists:

- **U1:** `Strategy.user_id` becomes nullable via an Alembic revision (phase 0/8 work).
- **U2:** POST without owner stores `user_id = NULL`.
- **U3:** `StrategyResponse.user_id` becomes `Optional[UUID]` to match.

## 12. Edge Cases

Nodos huérfanos (E12); `data.*` sin uso; múltiples entries (permitido, p. ej. buy + sell); múltiples exits (permitido); `risk.*` desconectados (E12, no excepción especial); self-loop (E13); tipo desconocido + edges que lo referencian (E5, sin errores secundarios inventados: la recolección continúa); edges duplicados con distinto id pero mismo source/target (permitido); `metadata` ausente → `{}`; `metadata: null` → `{}`; `position` con enteros (coerción `int → float`, los fixtures usan `{"x": 0}`).

## 13. Testing Strategy

```powershell
# Phase 1 gate (this spec, engine only)
.\.venv\Scripts\python.exe -m pytest tests/test_backtest.py::TestStrategyEngineIntegration -v
# Phase 2 gate (this spec semantics + api-contracts endpoints)
.\.venv\Scripts\python.exe -m pytest tests/test_strategies.py::TestStrategyAPI -v
```

Fixtures that pin behavior: `test_strategy_validation` (SMA crossover graph; fixture repaired 2026-10-05 to include an `action.close` exit node — the original contradicted `test_strategy_validation_no_exit`, which requires exit-less graphs to be invalid; all assertions unchanged), `test_strategy` fixture (SMA-cross graph, `metadata: {}`), `test_create_strategy` + `test_update_strategy_graph` graphs (creatable drafts without exit). Any new validation rule must be checked against every fixture in `tests/test_strategies.py` and `tests/test_backtest.py` before merging.

## 14. Out of Scope (other specs)

- `BacktestConfig` / `BacktestResult` alignment (TS has `position_sizing`, `stop_loss`, `take_profit`, extra metric fields; Pydantic lacks them) → `backtesting-engine` spec.
- Endpoint shapes, pagination (`items/total/page/page_size`), status codes → `api-contracts` spec.
- MCP write-tool wiring, `describe_node_type` → `mcp-server` spec.
- `BacktestEngine.run` being `async` while `test_backtest.py:86` calls it without `await` → `backtesting-engine` spec (flagged, not fixed here).
- Polars v1.x incompatibilities in `indicator_engine.py` (`rolling_mean(min_periods=…)`, `ewm_mean`, `pl.max_horizontal`) → covered by acceptance tests of the `backtesting-engine`/`indicators` work, not this spec.
- Market-data import, frontend graph editor, experiments, auth → `market-data`, `ui-graph-editor`, future specs.

## 15. Dependencies and Rollout

- **Phase 0 first:** move `dependencies` from `[tool.uv]` to `[project]` in `apps/backend/pyproject.toml`; align `packages/shared` per §3; Alembic revision for nullable `user_id` (U1). None of this changes runtime behavior.
- No feature flag: validation additions are backend-only and additive; all current fixtures comply with E1–E13, H1–H3, P1–P3 (verified against `tests/`).
- Known risk: stricter rules (E3, E4, E6, E7, E11, E12) could reject graphs stored before this spec. Backfill/migration of stored graphs is explicitly out of scope; `/validate` can be used to audit them later.

## 16. Notes

- Root `package.json` scripts `dev:backend`, `test:backend`, `lint:backend`, `typecheck:backend`, `db:*`, `mcp:dev` are broken (no `apps/backend/package.json`); backend commands run directly from `apps/backend` with the venv until fixed.
- `datetime.utcnow()` deprecations and the `Dataset.metadata` SAWarning stay for the hardening phase.
- `get_db_session` (`src/database.py`) is a plain async generator with `yield`, not an `@asynccontextmanager`-decorated function: FastAPI ≥ 0.118 no longer accepts bare context-manager functions in `Depends()` (live server returned 500 `'_AsyncGeneratorContextManager' object is not an async iterator` while tests, which override the dependency, stayed green). This pattern must be kept for all future dependencies.
