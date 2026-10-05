# Strategy Lab - Orden de ejecucion recomendado

**Fecha:** 2026-10-04
**Contexto:** derivado del smoke test (ver `docs/estado-actual.md`). El proyecto es SDD (SPEC -> Review -> Approve -> Plan -> Implement -> Verify -> Review) pero aun no existen specs por feature, asi que los **tests de `apps/backend/tests/`** se toman como fuente de verdad de aceptacion.

**Principio:** bottom-up (primero el nucleo de dominio) y vertical slice (primero una feature REST completa y visible, luego MCP, luego UI).

## Orden de fases

| # | Fase | Alcance | Por que despues de la anterior | Criterio de salida (Verify) |
|---|---|---|---|---|
| 0 | **Fundacion y tipos** | Verificar que `packages/shared` (TS) y `src/schemas` (Pydantic) no divergen en `StrategyGraph`, `BacktestConfig`, `BacktestResult`. Corregir el `pyproject.toml` (mover `dependencies` de `[tool.uv]` a `[project]`). | Base transversal: cualquier drift de tipos se propaga a frontend, MCP y tests. | `pnpm typecheck` verde y backend instala deps con `pip install -e .` sin pasos manuales. |
| 1 | **Strategy Engine (validacion de grafo)** | Completar `src/services/strategy_engine.py`: validar grafo (nodos/edges/conectividad), versionado y clonado. | Es el nucleo: Strategies API y MCP dependen de el. Falla hoy en `test_strategy_validation`. | `test_backtest.py::TestStrategyEngineIntegration::test_strategy_validation` pasa. |
| 2 | **Strategies API (CRUD)** | Implementar `src/api/v1/strategies.py` completo: list, create, get, update, delete, versions, clone, validate (usando service layer, nunca acceso directo a DB). | Depende solo de fase 1 + DB. Es la vertical slice mas visible. | **10 tests de `tests/test_strategies.py` pasan.** Proyecto pasa de scaffolding a feature usable. |
| 3 | **Indicators Engine** | Arreglar `src/services/indicator_engine.py` para **Polars v1.x** (sma, ema, rsi, macd, atr, bollinger_bands, compute/calculate). | Los motores de backtest y MCP consumen indicadores; corregir primero evita propagar errores de API. | Los 8 tests de `tests/test_indicators.py` dejan de dar error. |
| 4 | **Backtesting Engine** | Ajustar `src/services/backtest_engine.py`: ejecucion, metricas, equity curve, trades; corregir validaciones Pydantic. | Depende de fase 1 (estrategia valida) y fase 3 (indicadores para senales). | Los 4 errores `ERROR` de `tests/test_backtest.py::TestBacktestEngine` desaparecen. |
| 5 | **Backtests API** | Implementar `src/api/v1/backtests.py`: crear, ejecutar (BackgroundTasks), consultar estado/metricas/resultados. | Depende de fases 2 (existe la estrategia) y 4 (motor listo). Cierra el flujo principal del producto. | Flujo manual en `/docs`: crear estrategia -> lanzar backtest -> leer resultados. |
| 6 | **MCP (wiring de escritura)** | Completar los tools que responden `not implemented yet` (`list_strategies`, etc.) conectandolos a los servicios de las fases 1-5, respetando la regla de AGENTS.md: MCP comparte el service layer, nunca bypass a DB. | Requiere que los servicios existan (fases 1-5). Es el diferencial del producto (agentes). | `POST /api/v1/mcp/tools/call` funcional para tools de strategies/backtests. |
| 7 | **Frontend integration** | Conectar Dashboard, StrategyBuilder y BacktestResults a las APIs reales (TanStack Query), validar tipos compartidos en runtime (Zod) si hace drift. | Depende de APIs estables; la UI ya existe como scaffolding. | Flujo E2E manual: crear estrategia en el builder -> guardar -> listar -> lanzar backtest -> ver resultados. |
| 8 | **Hardening** | Fix de deprecaciones (`datetime.utcnow()` -> `datetime.now(UTC)`), warnings de SQLAlchemy (`metadata` en `Dataset`), lint/mypy/coverage, cobertura minima 80% backend. | Solo despues de funcionalidad completa, para no reescribir dos veces. | `pnpm lint`, `pnpm typecheck`, `pnpm test` en verde (o fallos justificados). |

## Dependencias graficas

```
0 (tipos/pyproject)
        |
        v
1 (strategy engine) ---> 2 (strategies REST) --+
        |                                       |
        v                                       v
3 (indicators) -------> 4 (backtest engine) --> 5 (backtests REST) --> 6 (MCP wiring)
                                                                      |
                                                                      v
                                                     7 (frontend integration) --> 8 (hardening)
```

## Notas

- Cada fase debe seguir **Red -> Green**: el test que falla hoy marca el objetivo.
- No implementar sin spec cuando se trate de features nuevas fuera de esta lista; los specs faltantes (`strategy-graph`, `api-contracts`, `backtesting-engine`, `mcp-server`, `ui-graph-editor`, `market-data`) deben escribirse aprobados antes de tocar esa area.
- Orden justificado por rendimiento de las pruebas: la fase 2 desbloquea 10 tests de golpe con la menor superficie de cambio; las fases 3-4 desbloquean los 13 errores + 4 fallos restantes.
