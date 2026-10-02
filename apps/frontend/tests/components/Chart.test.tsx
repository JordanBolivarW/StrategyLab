import { render, screen } from '@testing-library/react'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import Chart from '../components/Chart/Chart'

vi.mock('lightweight-charts', () => ({
  createChart: vi.fn(() => ({
    addSeries: vi.fn(() => ({ setData: vi.fn(), setMarkers: vi.fn() })),
    resize: vi.fn(),
    remove: vi.fn(),
  })),
}))

describe('Chart', () => {
  const mockCandles = [
    { timestamp: '2024-01-01T00:00:00Z', open: 100, high: 105, low: 99, close: 103, volume: 1000 },
    { timestamp: '2024-01-01T01:00:00Z', open: 103, high: 108, low: 102, close: 106, volume: 1200 },
    { timestamp: '2024-01-01T02:00:00Z', open: 106, high: 110, low: 104, close: 108, volume: 1100 },
  ]

  const mockTrades = [
    { id: 1, type: 'LONG', entry_time: '2024-01-01T00:00:00Z', exit_time: '2024-01-01T01:00:00Z', entry_price: 100, exit_price: 106, quantity: 1, return_pct: 6, pnl: 600, reason_entry: 'Signal', reason_exit: 'TP', duration: '1h' },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders chart container', () => {
    render(<Chart data={mockCandles} indicators={[]} trades={mockTrades} />)
    const container = screen.getByTestId('chart-container')
    expect(container).toBeInTheDocument()
  })

  it('handles empty data', () => {
    render(<Chart data={[]} indicators={[]} trades={[]} />)
    const container = screen.getByTestId('chart-container')
    expect(container).toBeInTheDocument()
  })

  it('updates when data changes', () => {
    const { rerender } = render(<Chart data={mockCandles} indicators={[]} trades={[]} />)
    const newCandles = [...mockCandles, { timestamp: '2024-01-01T03:00:00Z', open: 108, high: 112, low: 107, close: 110, volume: 1300 }]
    rerender(<Chart data={newCandles} indicators={[]} trades={[]} />)
    // Should not throw
    expect(screen.getByTestId('chart-container')).toBeInTheDocument()
  })
})