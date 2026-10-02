# Strategy Lab Frontend

React 18 + TypeScript + Vite + React Flow + Lightweight Charts

## Setup

```bash
# From monorepo root
cd apps/frontend

# Install dependencies
pnpm install
```

## Development

```bash
# Start dev server with HMR
pnpm dev

# Or from monorepo root
pnpm dev:frontend
```

## Building

```bash
# Type check + build
pnpm build

# Type check only
pnpm typecheck
```

## Testing

```bash
# Unit/Integration tests
pnpm test

# Watch mode
pnpm test:watch

# E2E tests
pnpm test:e2e
```

## Linting

```bash
# Lint
pnpm lint

# Format
pnpm format
```

## Project Structure

```
apps/frontend/
├── public/                 # Static assets
├── src/
│   ├── api/               # API client
│   ├── components/
│   │   ├── Chart/         # Lightweight Charts wrapper
│   │   └── StrategyGraph/ # React Flow graph editor
│   ├── hooks/             # React Query hooks
│   ├── pages/             # Page components
│   ├── stores/            # Zustand stores
│   ├── types/             # TypeScript types
│   ├── App.tsx            # Root component
│   ├── main.tsx           # Entry point
│   └── index.css          # Global styles (Tailwind)
├── tests/                 # Vitest + React Testing Library
├── playwright.config.ts   # E2E config
├── vitest.config.ts       # Unit test config
├── tailwind.config.js
├── vite.config.ts
├── tsconfig.json
└── package.json
```

## Key Technologies

- **React 18** - UI framework
- **TypeScript 5** - Type safety
- **Vite** - Build tool + HMR
- **React Flow** - Strategy graph editor
- **Lightweight Charts** - Financial charting (TradingView)
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Tailwind CSS** - Styling
- **Zod** - Runtime validation
- **React Hook Form** - Forms
- **Vitest** - Unit testing
- **Playwright** - E2E testing

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_WS_URL` | `ws://localhost:8000` | WebSocket URL |

## Custom Components

### Chart (`components/Chart/Chart.tsx`)
Wrapper around Lightweight Charts for candlestick charts with indicator overlays and trade markers.

### StrategyGraph (`components/StrategyGraph/StrategyGraph.tsx`)
React Flow-based visual strategy builder with:
- Drag-and-drop node palette
- Custom node types (Data, Indicators, Logic, Actions, Risk)
- Edge connections with handles
- Mini-map and controls

### Node Types (`components/StrategyGraph/NodeTypes.tsx`)
- **Data Nodes**: Open, High, Low, Close, Volume
- **Indicator Nodes**: SMA, EMA, RSI, MACD, ATR, Bollinger Bands
- **Logic Nodes**: AND, OR, NOT, Comparators (>, <, >=, <=, Cross Above/Below)
- **Action Nodes**: Buy, Sell, Long, Short, Close
- **Risk Nodes**: Position Size, Stop Loss, Take Profit

## API Integration

All API calls go through `src/api/client.ts` which uses Axios with:
- Base URL from `VITE_API_URL`
- Automatic error handling
- Type-safe request/response

## State Management

- **TanStack Query**: Server state (strategies, backtests, market data)
- **Zustand**: UI state (sidebar, theme, modals, toasts), current strategy

## Adding New Pages

1. Create component in `src/pages/`
2. Add route in `App.tsx`
3. Add navigation in Dashboard sidebar

## Theming

Tailwind config in `tailwind.config.js` with:
- Dark theme (slate-900 background)
- Primary color: Sky-500/600
- Custom components: `.btn`, `.input`, `.card`, `.panel`