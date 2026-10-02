import { useState } from 'react'
import { useUIStore } from '@/stores'
import type { MarketResponse, StrategyGraph as StrategyGraphType } from '@/types/strategy'
import { Chart } from '@/components/Chart'
import { StrategyGraph } from '@/components/StrategyGraph'
import { ResultsPanel } from './ResultsPanel'
import { Header } from '@/components/Layout/Header'
import { Sidebar, SidebarSection, SidebarItem } from '@/components/Layout/Sidebar'
import { Panel } from '@/components/Layout/Panel'
import { Button, Select, Input } from '@/components/UI'
import { useMarketData } from '@/hooks'

const MARKETS: MarketResponse[] = [
  { symbol: 'BTCUSDT', name: 'Bitcoin / USDT', type: 'crypto', timeframes: ['5m', '15m', '1h', '4h', '1D'] },
  { symbol: 'ETHUSDT', name: 'Ethereum / USDT', type: 'crypto', timeframes: ['5m', '15m', '1h', '4h', '1D'] },
  { symbol: 'SPY', name: 'SPDR S&P 500 ETF', type: 'stock', timeframes: ['5m', '15m', '1h', '4h', '1D'] },
  { symbol: 'EURUSD', name: 'Euro / US Dollar', type: 'forex', timeframes: ['5m', '15m', '1h', '4h', '1D'] },
]

const TIMEFRAMES = ['5m', '15m', '1h', '4h', '1D']

type PanelTab = 'strategy' | 'results' | 'trades' | 'analytics' | 'versions'

export default function Dashboard() {
  const { sidebarOpen, setSidebarOpen, addToast } = useUIStore()
  const [selectedMarket, setSelectedMarket] = useState('BTCUSDT')
  const [selectedTimeframe, setSelectedTimeframe] = useState('1h')
  const [dateRange, setDateRange] = useState({ start: '2024-01-01', end: '2024-12-31' })
  const [activeTab, setActiveTab] = useState<'chart' | 'strategy' | 'results'>('chart')
  const [panelTab, setPanelTab] = useState<PanelTab>('strategy')

  const { data: marketData, isLoading } = useMarketData(selectedMarket, selectedTimeframe, dateRange.start, dateRange.end)

  const handleGraphChange = (_graph: StrategyGraphType) => {
    // Graph changes handled by StrategyBuilder page
  }

  const handleRunBacktest = async () => {
    addToast('Backtest feature coming soon!', 'info')
  }

  return (
    <div className="app-layout">
      <Header title="Strategy Lab">
        <div className="toolbar-group">
          <Select
            value={selectedMarket}
            onChange={(e) => setSelectedMarket(e.target.value)}
            className="w-48"
          >
            {MARKETS.map((m) => (
              <option key={m.symbol} value={m.symbol}>
                {m.symbol}
              </option>
            ))}
          </Select>
          <Select
            value={selectedTimeframe}
            onChange={(e) => setSelectedTimeframe(e.target.value)}
            className="w-24"
          >
            {TIMEFRAMES.map((tf) => (
              <option key={tf} value={tf}>
                {tf}
              </option>
            ))}
          </Select>
          <div className="flex items-center gap-2">
            <Input
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
              className="w-36"
            />
            <span className="text-gray-400">→</span>
            <Input
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
              className="w-36"
            />
          </div>
          <Button onClick={handleRunBacktest} disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Run Backtest'}
          </Button>
        </div>
      </Header>

      <main className="app-main">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)}>
          <SidebarSection title="Markets">
            {MARKETS.map((market) => (
              <SidebarItem
                key={market.symbol}
                label={market.symbol}
                badge={market.type}
                active={selectedMarket === market.symbol}
                onClick={() => setSelectedMarket(market.symbol)}
              />
            ))}
          </SidebarSection>
        </Sidebar>

        <div className="content-area flex-1 flex flex-col overflow-hidden">
          <div className="tab-bar border-b border-dark-border bg-dark-card flex items-center">
            <button
              className={`tab px-4 py-2 text-sm font-medium transition-colors cursor-pointer border-b-2 border-transparent ${activeTab === 'chart' ? 'text-primary-400 border-primary-500' : 'text-gray-400'}`}
              onClick={() => setActiveTab('chart')}
            >
              Chart
            </button>
            <button
              className={`tab px-4 py-2 text-sm font-medium transition-colors cursor-pointer border-b-2 border-transparent ${activeTab === 'strategy' ? 'text-primary-400 border-primary-500' : 'text-gray-400'}`}
              onClick={() => setActiveTab('strategy')}
            >
              Strategy
            </button>
            <button
              className={`tab px-4 py-2 text-sm font-medium transition-colors cursor-pointer border-b-2 border-transparent ${activeTab === 'results' ? 'text-primary-400 border-primary-500' : 'text-gray-400'}`}
              onClick={() => setActiveTab('results')}
            >
              Results
            </button>
          </div>

          <div className="flex-1 flex overflow-hidden">
            {activeTab === 'chart' && (
              <div className="chart-area relative">
                <Chart
                  data={marketData?.candles || []}
                  trades={[]}
                />
              </div>
            )}

            {activeTab === 'strategy' && (
              <div className="flex-1">
                <StrategyGraph
                  strategyId={null}
                  initialGraph={{ nodes: [], edges: [], metadata: {} }}
                  onChange={handleGraphChange}
                  readOnly={false}
                />
              </div>
            )}

            {activeTab === 'results' && (
              <ResultsPanel />
            )}
          </div>

          <Panel
            tabs={[
              { id: 'strategy', label: 'Strategy' },
              { id: 'results', label: 'Results' },
              { id: 'trades', label: 'Trades' },
              { id: 'analytics', label: 'Analytics' },
              { id: 'versions', label: 'Versions' },
            ]}
            activeTab={panelTab}
            onTabChange={(tabId: PanelTab) => setPanelTab(tabId)}
          >
            <div className="space-y-4">
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Strategy Info</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Market</span>
                    <span className="font-mono">{selectedMarket}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Timeframe</span>
                    <span className="font-mono">{selectedTimeframe}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Period</span>
                    <span className="font-mono">{dateRange.start} → {dateRange.end}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-2">Quick Actions</h3>
                <div className="space-y-2">
                  <Button className="w-full justify-start" variant="secondary">New Strategy</Button>
                  <Button className="w-full justify-start" variant="secondary">Load Strategy</Button>
                  <Button className="w-full justify-start" variant="secondary">Compare Versions</Button>
                </div>
              </div>
            </div>
          </Panel>
        </div>
      </main>
    </div>
  )
}