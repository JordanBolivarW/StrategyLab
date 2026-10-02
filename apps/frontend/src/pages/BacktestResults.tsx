import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'
import { Chart } from '@/components/Chart'
import { ResultsPanel } from './ResultsPanel'
import { Header } from '@/components/Layout/Header'
import { Panel } from '@/components/Layout/Panel'

export default function BacktestResults() {
  const { id } = useParams()

  const { data: backtest, isLoading } = useQuery({
    queryKey: ['backtest', id],
    queryFn: () => api.getBacktest(id!),
    enabled: !!id,
  })

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (!backtest) {
    return (
      <div className="flex h-full items-center justify-center text-gray-400">
        Backtest not found
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <Header title="Backtest Results">
        <div className="toolbar-group">
          <h2 className="text-lg font-semibold">Backtest Results</h2>
          <span className={`px-2 py-1 rounded text-xs font-medium ${
            backtest.status === 'completed' ? 'bg-green-500/20 text-green-400' :
            backtest.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
            backtest.status === 'failed' ? 'bg-red-500/20 text-red-400' :
            'bg-gray-500/20 text-gray-400'
          }`}>
            {backtest.status}
          </span>
        </div>
        <div className="toolbar-group">
          <button className="btn-secondary">Export</button>
          <button className="btn-secondary">Share</button>
        </div>
      </Header>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1">
          <Chart
            data={backtest.equity_curve?.points || []}
            trades={backtest.trades?.trades || []}
            seriesType="line"
          />
        </div>

        <Panel
          tabs={[
            { id: 'metrics', label: 'Metrics' },
            { id: 'trades', label: 'Trades' },
            { id: 'equity', label: 'Equity Curve' },
            { id: 'analytics', label: 'Analytics' },
          ]}
          activeTab="metrics"
          onTabChange={() => {}}
        >
          <ResultsPanel backtest={backtest} />
        </Panel>
      </div>
    </div>
  )
}