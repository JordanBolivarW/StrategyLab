# Task: Web Interface (Phase 4)

## Spec Reference
[SPECS/web-interface.md](SPECS/web-interface.md)

## Approach
Implement the complete web interface for Strategy Lab MCP including:
1. Dashboard with market/chart/strategy layout
2. Strategy Builder with React Flow graph editor
3. Backtest Results with equity curve, metrics, trades
4. Results Panel with tabbed interface
5. Chart components with Lightweight Charts
6. Strategy Graph components with React Flow
7. API client, hooks, and state management

## Implementation Steps

### Phase 1: Core Infrastructure
- [ ] 1.1 Create UI component library (Button, Select, Input, Modal, Toast, Tabs)
- [ ] 1.2 Create Layout components (Header, Sidebar, Panel)
- [ ] 1.3 Set up Zustand stores (ui.ts, strategy.ts)
- [ ] 1.4 Configure API client with interceptors
- [ ] 1.5 Create TanStack Query hooks (useStrategies, useBacktest, useMarketData)

### Phase 2: Chart Components
- [ ] 2.1 Create Chart.tsx - Lightweight Charts wrapper with candlesticks
- [ ] 2.2 Create Indicators.tsx - Line/histogram series for indicators
- [ ] 2.3 Create TradeMarkers.tsx - Entry/exit markers with tooltips
- [ ] 2.4 Add crosshair, watermark, responsive resize

### Phase 3: Strategy Graph Components
- [ ] 3.1 Create NodeTypes.tsx - Custom node components for all 6 categories
- [ ] 3.2 Create NodePalette.tsx - Draggable sidebar palette with categories
- [ ] 3.3 Create StrategyGraph.tsx - React Flow container with validation
- [ ] 3.4 Add MiniMap, Controls, Background, undo/redo

### Phase 4: Pages
- [ ] 4.1 Create Dashboard.tsx - Main layout with tabs (Chart/Strategy/Results)
- [ ] 4.2 Create StrategyBuilder.tsx - Full-screen graph editor
- [ ] 4.3 Create BacktestResults.tsx - Equity curve, metrics, trades
- [ ] 4.4 Create ResultsPanel.tsx - 5-tab panel (Strategy/Results/Trades/Analytics/Versions)
- [ ] 4.5 Add routing (React Router)

### Phase 5: Integration & Polish
- [ ] 5.1 Connect Dashboard to live API (market data, strategies)
- [ ] 5.2 Connect StrategyBuilder to save/clone/validate endpoints
- [ ] 5.3 Connect BacktestResults to run backtest and display results
- [ ] 5.4 Add toast notifications, loading states, error handling
- [ ] 5.5 Add keyboard shortcuts, responsive design

## Files to Create/Modify

### New UI Components
| File | Description |
|------|-------------|
| `src/components/UI/Button.tsx` | Primary/secondary/danger variants |
| `src/components/UI/Select.tsx` | Styled select with options |
| `src/components/UI/Input.tsx` | Text/number/date inputs |
| `src/components/UI/Modal.tsx` | Accessible modal with portal |
| `src/components/UI/Toast.tsx` | Toast notifications |
| `src/components/UI/Tabs.tsx` | Tab navigation component |
| `src/components/Layout/Header.tsx` | Top bar with market/timeframe/date |
| `src/components/Layout/Sidebar.tsx` | Left sidebar with market list |
| `src/components/Layout/Panel.tsx` | Right panel with tabs |

### Chart Components
| File | Description |
|------|-------------|
| `src/components/Chart/Chart.tsx` | Main chart with candlesticks |
| `src/components/Chart/Indicators.tsx` | Indicator overlay series |
| `src/components/Chart/TradeMarkers.tsx` | Entry/exit markers |

### Strategy Graph Components
| File | Description |
|------|-------------|
| `src/components/StrategyGraph/NodeTypes.tsx` | 6 category node components |
| `src/components/StrategyGraph/NodePalette.tsx` | Draggable node palette |
| `src/components/StrategyGraph/StrategyGraph.tsx` | React Flow container |

### Pages
| File | Description |
|------|-------------|
| `src/pages/Dashboard.tsx` | Main view with 3 tabs |
| `src/pages/StrategyBuilder.tsx` | Full-screen graph editor |
| `src/pages/BacktestResults.tsx` | Results with equity curve |
| `src/pages/ResultsPanel.tsx` | 5-tab sidebar panel |

### Core Infrastructure
| File | Description |
|------|-------------|
| `src/stores/ui.ts` | UI state (sidebar, theme, toasts) |
| `src/stores/strategy.ts` | Current strategy state |
| `src/hooks/useStrategies.ts` | Strategy queries/mutations |
| `src/hooks/useBacktest.ts` | Backtest queries/mutations |
| `src/hooks/useMarketData.ts` | Market data queries |
| `src/api/client.ts` | Axios client with interceptors |
| `src/App.tsx` | Router with routes |

## Tests to Write
- [ ] Unit: Chart rendering with candles + indicators
- [ ] Unit: StrategyGraph node add/connect/validate
- [ ] Unit: NodePalette drag-and-drop
- [ ] Unit: Strategy validation logic
- [ ] Integration: Dashboard market switch updates chart
- [ ] Integration: StrategyBuilder save → appears in list
- [ ] Integration: Run backtest → shows results → compare
- [ ] E2E: Create strategy → run backtest → view results

## Acceptance Criteria (from Spec)
- [ ] AC1: Candlestick chart with zoom, pan, timeframe, indicators, trade markers
- [ ] AC2: Strategy Graph Editor with drag-drop, connections, validation
- [ ] AC3: Dashboard with market/timeframe/date selectors, 3 tabs
- [ ] AC4: Strategy Builder full-screen with palette, toolbar, shortcuts
- [ ] AC5: Backtest Results with equity curve, metrics grid, trades table
- [ ] AC6: Results Panel with 5 tabs (Strategy/Results/Trades/Analytics/Versions)
- [ ] AC7: Trade visualization with markers on chart
- [ ] AC8: Real-time toast notifications for actions

## Risks & Mitigations
- **React Flow + Lightweight Charts Canvas conflict** → Test early, use separate containers
- **Large graph performance** → Implement virtualization, limit nodes to 100
- **WebSocket for backtest progress** → Defer to future phase, use polling for now
- **Responsive design** → Test mobile sidebar collapse, chart resize

## Dependencies
- Phase 1: Foundation (complete)
- Phase 2: Backtesting engine (complete)
- Phase 3: MCP tools (complete)
- `@strategy-lab/shared` types package (built)
- Backend API running on localhost:8000

## Rollout Plan
- [ ] Feature flag: `web-interface`
- [ ] Gradual rollout: 100% (internal)
- [ ] Rollback: Revert to previous build