import type { BacktestResponse } from '@/types/strategy'

interface ResultsPanelProps {
  backtest?: BacktestResponse
}

export function ResultsPanel({ backtest }: ResultsPanelProps) {
  const metrics = backtest?.metrics

  if (!metrics) {
    return (
      <div className="h-full flex items-center justify-center text-gray-400">
        No metrics available
      </div>
    )
  }

  const metricCards = [
    { label: 'Return', value: `${metrics.return_pct >= 0 ? '+' : ''}${metrics.return_pct.toFixed(2)}%`, positive: metrics.return_pct >= 0 },
    { label: 'Buy & Hold', value: `${metrics.buy_hold_return_pct >= 0 ? '+' : ''}${metrics.buy_hold_return_pct.toFixed(2)}%`, positive: metrics.buy_hold_return_pct >= 0 },
    { label: 'Max Drawdown', value: `-${metrics.max_drawdown_pct.toFixed(2)}%`, negative: true },
    { label: 'Win Rate', value: `${metrics.win_rate_pct.toFixed(2)}%` },
    { label: 'Profit Factor', value: metrics.profit_factor.toFixed(2) },
    { label: 'Total Trades', value: metrics.total_trades.toString() },
    { label: 'Avg Trade', value: `${metrics.avg_trade_pct >= 0 ? '+' : ''}${metrics.avg_trade_pct.toFixed(2)}%`, positive: metrics.avg_trade_pct >= 0 },
    { label: 'Sharpe Ratio', value: metrics.sharpe_ratio?.toFixed(2) || 'N/A' },
    { label: 'Sortino Ratio', value: metrics.sortino_ratio?.toFixed(2) || 'N/A' },
    { label: 'Calmar Ratio', value: metrics.calmar_ratio?.toFixed(2) || 'N/A' },
  ]

  return (
    <div className="h-full flex flex-col">
      <div className="flex border-b border-dark-border mb-4">
        {(['metrics', 'trades', 'equity', 'analytics'] as const).map((view) => (
          <button
            key={view}
            className={`panel-tab px-4 py-2 text-sm font-medium ${
              'text-gray-400 hover:text-white hover:bg-dark-border transition-colors cursor-pointer border-b-2 border-transparent'
            }`}
            onClick={() => {}}
          >
            {view.charAt(0).toUpperCase() + view.slice(1)}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="results-grid grid grid-cols-2 gap-4 p-4">
          {metricCards.map((metric) => (
            <div key={metric.label} className="metric-card bg-dark-bg/50 border border-dark-border rounded-lg p-4">
              <div className="metric-label text-xs text-gray-400 uppercase tracking-wider mb-1">{metric.label}</div>
              <div className={`metric-value text-2xl font-bold font-mono ${metric.positive ? 'text-green-400' : metric.negative ? 'text-red-400' : ''}`}>
                {metric.value}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}