import { describe, it, expect } from 'vitest'
import {
  StrategyGraphSchema,
  StrategyNodeSchema,
  StrategyEdgeSchema,
  BacktestConfigSchema,
  MarketSchema,
  IndicatorDefinitionSchema,
  validateStrategyGraph,
  validateBacktestConfig,
  symbol,
  timeframe,
  uuid,
  dateRange,
} from '../src/utils/validation'

describe('Shared Validation', () => {
  describe('StrategyGraphSchema', () => {
    it('validates a valid strategy graph', () => {
      const validGraph = {
        nodes: [
          { id: '550e8400-e29b-41d4-a716-446655440000', type: 'data.close', position: { x: 0, y: 0 }, data: {} },
          { id: '550e8400-e29b-41d4-a716-446655440001', type: 'indicator.ema', position: { x: 200, y: 0 }, data: { period: 20 } },
          { id: '550e8400-e29b-41d4-a716-446655440002', type: 'action.buy', position: { x: 400, y: 0 }, data: {} },
        ],
        edges: [
          { id: '550e8400-e29b-41d4-a716-446655440003', source: '550e8400-e29b-41d4-a716-446655440000', target: '550e8400-e29b-41d4-a716-446655440001' },
          { id: '550e8400-e29b-41d4-a716-446655440004', source: '550e8400-e29b-41d4-a716-446655440001', target: '550e8400-e29b-41d4-a716-446655440002' },
        ],
        metadata: {},
      }

      const result = validateStrategyGraph(validGraph)
      expect(result.success).toBe(true)
    })

    it('rejects graph with no nodes', () => {
      const invalidGraph = {
        nodes: [],
        edges: [],
        metadata: {},
      }

      const result = validateStrategyGraph(invalidGraph)
      expect(result.success).toBe(false)
    })

    it('rejects graph with no edges', () => {
      const invalidGraph = {
        nodes: [
          { id: '550e8400-e29b-41d4-a716-446655440000', type: 'data.close', position: { x: 0, y: 0 }, data: {} },
        ],
        edges: [],
        metadata: {},
      }

      const result = validateStrategyGraph(invalidGraph)
      expect(result.success).toBe(false)
    })

    it('rejects invalid node type', () => {
      const invalidGraph = {
        nodes: [
          { id: '550e8400-e29b-41d4-a716-446655440000', type: 'invalid.type', position: { x: 0, y: 0 }, data: {} },
        ],
        edges: [],
        metadata: {},
      }

      const result = validateStrategyGraph(invalidGraph)
      expect(result.success).toBe(false)
    })
  })

  describe('BacktestConfigSchema', () => {
    it('validates a valid backtest config', () => {
      const validConfig = {
        strategy_id: '550e8400-e29b-41d4-a716-446655440000',
        market: 'BTCUSDT',
        timeframe: '1h',
        start_date: '2024-01-01T00:00:00Z',
        end_date: '2024-12-31T23:59:59Z',
        initial_capital: 10000,
        commission: 0.001,
        slippage: 0.0005,
      }

      const result = validateBacktestConfig(validConfig)
      expect(result.success).toBe(true)
    })

    it('rejects invalid date range', () => {
      const invalidConfig = {
        strategy_id: '550e8400-e29b-41d4-a716-446655440000',
        market: 'BTCUSDT',
        timeframe: '1h',
        start_date: '2024-12-31T23:59:59Z',
        end_date: '2024-01-01T00:00:00Z',
        initial_capital: 10000,
        commission: 0.001,
        slippage: 0.0005,
      }

      const result = validateBacktestConfig(invalidConfig)
      expect(result.success).toBe(false)
    })

    it('rejects negative capital', () => {
      const invalidConfig = {
        strategy_id: '550e8400-e29b-41d4-a716-446655440000',
        market: 'BTCUSDT',
        timeframe: '1h',
        start_date: '2024-01-01T00:00:00Z',
        end_date: '2024-12-31T23:59:59Z',
        initial_capital: -1000,
        commission: 0.001,
        slippage: 0.0005,
      }

      const result = validateBacktestConfig(invalidConfig)
      expect(result.success).toBe(false)
    })

    it('rejects commission > 1', () => {
      const invalidConfig = {
        strategy_id: '550e8400-e29b-41d4-a716-446655440000',
        market: 'BTCUSDT',
        timeframe: '1h',
        start_date: '2024-01-01T00:00:00Z',
        end_date: '2024-12-31T23:59:59Z',
        initial_capital: 10000,
        commission: 1.5,
        slippage: 0.0005,
      }

      const result = validateBacktestConfig(invalidConfig)
      expect(result.success).toBe(false)
    })
  })

  describe('Symbol validation', () => {
    it('accepts valid symbols', () => {
      expect(symbol.safeParse('BTCUSDT').success).toBe(true)
      expect(symbol.safeParse('ETHUSDT').success).toBe(true)
      expect(symbol.safeParse('SPY').success).toBe(true)
      expect(symbol.safeParse('EURUSD').success).toBe(true)
      expect(symbol.safeParse('AAPL').success).toBe(true)
    })

    it('rejects invalid symbols', () => {
      expect(symbol.safeParse('btcusdt').success).toBe(false)
      expect(symbol.safeParse('BTC/USDT').success).toBe(false)
      expect(symbol.safeParse('').success).toBe(false)
      expect(symbol.safeParse('A'.repeat(51)).success).toBe(false)
    })
  })

  describe('Timeframe validation', () => {
    it('accepts valid timeframes', () => {
      expect(timeframe.safeParse('1m').success).toBe(true)
      expect(timeframe.safeParse('5m').success).toBe(true)
      expect(timeframe.safeParse('15m').success).toBe(true)
      expect(timeframe.safeParse('1h').success).toBe(true)
      expect(timeframe.safeParse('4h').success).toBe(true)
      expect(timeframe.safeParse('1D').success).toBe(true)
      expect(timeframe.safeParse('1W').success).toBe(true)
      expect(timeframe.safeParse('1M').success).toBe(true)
    })

    it('rejects invalid timeframes', () => {
      expect(timeframe.safeParse('3m').success).toBe(false)
      expect(timeframe.safeParse('2h').success).toBe(false)
      expect(timeframe.safeParse('invalid').success).toBe(false)
    })
  })

  describe('UUID validation', () => {
    it('accepts valid UUIDs', () => {
      expect(uuid.safeParse('550e8400-e29b-41d4-a716-446655440000').success).toBe(true)
      expect(uuid.safeParse('00000000-0000-0000-0000-000000000000').success).toBe(true)
    })

    it('rejects invalid UUIDs', () => {
      expect(uuid.safeParse('not-a-uuid').success).toBe(false)
      expect(uuid.safeParse('550e8400-e29b-41d4-a716').success).toBe(false)
      expect(uuid.safeParse('').success).toBe(false)
    })
  })

  describe('Date range validation', () => {
    it('accepts valid date ranges', () => {
      const validRange = {
        start: '2024-01-01T00:00:00Z',
        end: '2024-12-31T23:59:59Z',
      }
      expect(dateRange.safeParse(validRange).success).toBe(true)
    })

    it('rejects end before start', () => {
      const invalidRange = {
        start: '2024-12-31T23:59:59Z',
        end: '2024-01-01T00:00:00Z',
      }
      expect(dateRange.safeParse(invalidRange).success).toBe(false)
    })

    it('rejects equal dates', () => {
      const invalidRange = {
        start: '2024-01-01T00:00:00Z',
        end: '2024-01-01T00:00:00Z',
      }
      expect(dateRange.safeParse(invalidRange).success).toBe(false)
    })
  })
})