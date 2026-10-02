# Strategy Lab MCP — Initial Product Vision

## 1. Visión del producto

Strategy Lab MCP será una plataforma de investigación y backtesting de estrategias de trading diseñada para que tanto humanos como agentes de inteligencia artificial puedan crear, modificar, probar, comparar e iterar estrategias utilizando una misma representación estructurada.

La aplicación tendrá una interfaz sencilla inspirada conceptualmente en herramientas como TradingView, pero con un enfoque mucho más específico:
- análisis de datos históricos;
- creación visual de estrategias;
- backtesting;
- comparación de resultados;
- optimización;
- experimentación;
- versionado;
- integración nativa mediante MCP.

El objetivo no es construir otro TradingView.
El objetivo es crear un laboratorio de estrategias algorítmicas donde el usuario pueda pasar rápidamente de una idea a una estrategia comprobable.

> **Propuesta principal:** Construye una estrategia visualmente, pruébala contra años de datos históricos y permite que agentes de IA la analicen, modifiquen e iteren mediante MCP sin que Strategy Lab necesite integrar una IA propia.

---

## 2. Principio fundamental

> Todo lo que pueda hacer un usuario desde la interfaz debe poder hacerlo también un agente externo mediante MCP.

Arquitectura conceptual:
```
                         CORE
               ┌────────────────────┐
               │ Strategy Engine    │
               │ Backtest Engine    │
               │ Market Data        │
               │ Analytics          │
               │ Optimizer          │
               │ Versioning         │
               └─────────┬──────────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
            ▼            ▼            ▼
           WEB           MCP          API
            │             │
            ▼             ▼
          HUMANO      AGENTE IA
```

---

## 3. Sin IA propia

Strategy Lab será agnóstico respecto al modelo de IA. No dependerá de OpenAI, Anthropic, Gemini, ni API keys de proveedores.

Expondrá funcionalidades mediante MCP. El usuario usará herramientas externas compatibles: ChatGPT, OpenCode, Claude, Cursor, IDEs, agentes personalizados.

---

## 4. Flujo objetivo (< 5 min)

```
Seleccionar mercado → Seleccionar periodo → Construir estrategia → Ejecutar backtest
→ Analizar resultados → Crear variante → Comparar → Iterar
```

---

## 5. Pantalla principal (4 componentes)

```
┌──────────────────────────────────────────────────────────────┐
│ BTCUSDT ▼      4H ▼       2022 → 2026     ▶ RUN BACKTEST   │
├───────────────┬──────────────────────────────────────────────┤
│               │                                              │
│ MERCADOS      │                 GRÁFICO                      │
│               │                                              │
│ BTCUSDT       │            Velas japonesas                   │
│ ETHUSDT       │                                              │
│ SPY           │      ───── EMA 20                            │
│ EURUSD        │      ───── EMA 50                            │
│               │        ▲ Buy      ▼ Sell                     │
│               │                                              │
├───────────────┴──────────────────────────────────────────────┤
│ Strategy │ Results │ Trades │ Analytics │ Versions          │
├────────────────────────────┬─────────────────────────────────┤
│                            │                                 │
│ STRATEGY GRAPH             │ RESULTS                         │
│                            │                                 │
│ EMA20 ─┐                   │ Return           +38%           │
│        ├─ Cross ─ BUY      │ Drawdown         -11%           │
│ EMA50 ─┘                   │ Win Rate          54%            │
│                            │ Profit Factor      1.7           │
│                            │ Trades             143           │
└────────────────────────────┴─────────────────────────────────┘
```

---

## 6-10. Strategy Graph & Definition

- Estrategia = **grafo estructurado** (nodes[] + edges[])
- JSON como representación persistente
- Separación clara: SIGNAL → ENTRY → POSITION MANAGEMENT → EXIT
- Nodos: Datos, Indicadores, Comparadores, Lógica, Acciones, Riesgo, Tiempo, Matemática

---

## 11-13. Market Data

- Importación manual: CSV, JSON, Parquet
- Conectores futuros: Binance, Coinbase, Polygon, Alpaca, OANDA, Dukascopy
- MVP: BTCUSDT, ETHUSDT, SPY, EURUSD | 5m, 15m, 1h, 4h, 1D

---

## 14-18. Backtest Engine

- Recorrido cronológico vela a vela
- Config: Capital, Comisión, Slippage, Position Sizing, Periodo, Timeframe, SL/TP
- Evitar look-ahead bias desde arquitectura
- Resultados: Return, Drawdown, Win Rate, Profit Factor, Trades, Equity Curve, Trade Log

---

## 19-23. Comparación y Versionado

- Comparar estrategias/versiones lado a lado
- Versionado obligatorio (nunca sobrescribir)
- Strategy Diff: cambios + impacto en métricas

---

## 22-23. Experimentos

```
Experiment: hypothesis + changes + dataset + backtest + results + conclusion
```
- Ramas de experimentación (como git branches)
- Promover/descartar

---

## 24-32. MCP (Central)

**Discovery:** get_platform_capabilities, list_markets, describe_market, list_indicators, describe_indicator, list_node_types, describe_node_type
**Strategies:** list_strategies, get_strategy, create_strategy, clone_strategy, update_strategy, validate_strategy, get_strategy_versions, get_strategy_diff
**Backtesting:** run_backtest, get_backtest, list_backtests, get_backtest_trades, get_backtest_metrics
**Comparación:** compare_backtests, compare_strategies, compare_strategy_versions
**Experimentos (futuro):** create_experiment, get_experiment, list_experiments, promote_experiment, discard_experiment
**Optimización (futuro):** run_optimization, get_optimization, get_optimization_results

`describe_indicator` y `describe_node_type` permiten a agentes aprender dinámicamente.

---

## 33-34. Casos de uso MCP

Usuario en OpenCode/Claude/ChatGPT:
> "Toma mi estrategia BTC Trend v4. Analiza sus resultados. Quiero disminuir el drawdown sin perder >5% rentabilidad. Crea 3 variantes. Ejecuta backtests. Compáralas."

Agente ejecuta: get_strategy → get_backtest → clone_strategy → update_strategy → run_backtest (x3) → compare_backtests

---

## 35. Strategy Explain (sin IA)

Generación automática de explicación legible desde el Strategy Graph.

---

## 36-37. Optimización vs IA

- **Strategy Lab:** Optimización matemática (grid search, parameter ranges)
- **IA externa:** Reasoning, hypothesis generation, strategy modification

---

## 38-41. Protección contra Overfitting

- TRAIN / VALIDATION / TEST splits obligatorios
- Locked Test Dataset (no optimizar contra TEST)
- Walk-Forward Analysis (futuro)
- Monte Carlo (futuro)

---

## 42-43. Seguridad MCP y Sin Trading Real

Tools separadas: Read, Write, Compute. **NO trading real en MVP.**
Evolución: Historical Research → Paper Trading → Live Data → Broker Integration → Live Trading

---

## 44-48. Stack Sugerido

- **Frontend:** React, TypeScript, React Flow, Lightweight Charts
- **Backend:** FastAPI, Python
- **Motor cuantitativo:** Python, NumPy, Polars
- **Persistencia:** PostgreSQL + Parquet
- **Arquitectura:** Core API + Services + MCP Server (comparten servicios, no BD directa)

---

## 49-51. Arquitectura y Auditoría

- MCP usa misma capa de servicios que REST API
- Auditoría: created_by, source, client, timestamp

---

## 52-60. MVP y Roadmap (10 fases)

**MVP Core:** Market Dataset Engine, Strategy Schema, Strategy Graph, Indicator Engine, Backtest Engine, Metrics Engine, Strategy Versioning
**MVP UI:** Candlestick Chart, Market/Timeframe/Date Selectors, Strategy Node Editor, Backtest Button, Results Panel, Trade Markers, Strategy Versions
**MVP Indicadores:** SMA, EMA, RSI, MACD, ATR, Bollinger Bands
**MVP Lógica:** >, <, >=, <=, Cross Above/Below, AND, OR, NOT
**MVP Trading Nodes:** Long, Short, Close, Stop Loss, Take Profit, Position Size
**MVP MCP:** 20 tools (discovery, strategies, backtesting, comparison)

**Roadmap:** Foundation → Backtesting → MCP → Web → Experimentation → Validation → Optimization → Advanced Research → Real-time → Execution

---

## 61. Diferenciales

1. **Visual Strategy Builder** — sin programar
2. **Structured Strategy Graph** — definición formal, no código arbitrario
3. **Backtesting** — comprobar ideas vs histórico
4. **Versioning** — historial completo
5. **Experiments** — probar hipótesis sin destruir
6. **MCP Native** — agentes externos crean/modifican/iteran
7. **Model Agnostic** — sin dependencia de proveedor IA
8. **AI without embedded IA** — aprovechar agentes sin LLM interno

---

## 62. Experiencia final

Usuario desde OpenCode:
> "Conéctate a Strategy Lab. Busca BTC Trend. Analiza último backtest. Reduce drawdown <10%. No pierdas >5% rentabilidad. Crea hasta 5 experimentos. Modifica: EMA Fast/Slow, RSI, SL, TP. Ejecuta backtests. No uses dataset TEST. Compara y guarda variantes."

Resultado: variantes aparecen en Strategy Lab con velas, indicadores, entradas, salidas, resultados, diff vs original.

---

## 63. Visión larga

```
                       STRATEGY LAB
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   VISUAL BUILDER       AI AGENTS          QUANT ENGINE
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                     EXPERIMENTATION
                            │
                ┌───────────┼────────────┐
                │           │            │
             BACKTEST   OPTIMIZATION  VALIDATION
                │           │            │
                └───────────┼────────────┘
                            │
                            ▼
                      PAPER TRADING
                            │
                            ▼
                       LIVE TRADING
```

Núcleo simple: **Datos + Estrategia + Backtesting + Experimentación + MCP**

---

## 64. Definición final

**Strategy Lab MCP** = plataforma visual de investigación de estrategias de trading que permite crear estrategias mediante programación gráfica, probarlas sobre datos históricos, analizar rendimiento, versionarlas, compararlas y mejorarlas mediante experimentación.

Arquitectura **MCP-native**: agentes externos consultan mercados, crean estrategias, modifican parámetros, ejecutan backtests, comparan resultados e iteran hipótesis sin que la plataforma integre un modelo de IA propio ni dependa de API keys de proveedores.

**Strategy Graph** = fuente de verdad compartida (humanos, web, motores cuantitativos, agentes).

Prioridad: **motor de investigación confiable, reproducible y extensible** antes de trading en tiempo real.

> **Humans design. AI experiments. Strategy Lab proves.**