import { useCallback, useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { StrategyGraph } from '@/components/StrategyGraph'
import { api } from '@/api/client'
import { Header } from '@/components/Layout/Header'
import { Button, Select, Input } from '@/components/UI'
import type { StrategyGraph as StrategyGraphType } from '@/types/strategy'

interface BuilderStrategy {
  name: string
  description: string
  market: string
  timeframe: string
  graph: StrategyGraphType
}

export default function StrategyBuilder() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [strategy, setStrategy] = useState<BuilderStrategy | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)

  const loadStrategy = useCallback(async () => {
    setLoading(true)
    try {
      const data = await api.getStrategy(id!)
      setStrategy({ ...data, description: data.description ?? '' })
    } catch (error) {
      console.error('Failed to load strategy:', error)
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    if (id) {
      loadStrategy()
    } else {
      // New strategy - create empty graph
      setStrategy({
        name: '',
        description: '',
        market: 'BTCUSDT',
        timeframe: '1h',
        graph: {
          nodes: [],
          edges: [],
          metadata: {},
        },
      })
    }
  }, [id, loadStrategy])

  const handleSave = async (graph: StrategyGraphType | undefined) => {
    if (!strategy || !graph) return
    setSaving(true)
    try {
      if (id) {
        await api.updateStrategy(id, { ...strategy, graph })
      } else {
        const newStrategy = await api.createStrategy({ ...strategy, graph })
        navigate(`/strategy/${newStrategy.id}`)
      }
    } catch (error) {
      console.error('Failed to save strategy:', error)
    } finally {
      setSaving(false)
    }
  }

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setStrategy((prev) => prev ? { ...prev, name: e.target.value } : null)
  }

  const handleMarketChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStrategy((prev) => prev ? { ...prev, market: e.target.value } : null)
  }

  const handleTimeframeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setStrategy((prev) => prev ? { ...prev, timeframe: e.target.value } : null)
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col">
      <Header title={id ? 'Edit Strategy' : 'New Strategy'}>
        <div className="toolbar-group">
          <Input
            value={strategy?.name || ''}
            onChange={handleNameChange}
            placeholder="Strategy name"
            className="w-64"
          />
          <Select
            value={strategy?.market || 'BTCUSDT'}
            onChange={handleMarketChange}
            className="w-40"
          >
            <option value="BTCUSDT">BTCUSDT</option>
            <option value="ETHUSDT">ETHUSDT</option>
            <option value="SPY">SPY</option>
            <option value="EURUSD">EURUSD</option>
          </Select>
          <Select
            value={strategy?.timeframe || '1h'}
            onChange={handleTimeframeChange}
            className="w-24"
          >
            <option value="5m">5m</option>
            <option value="15m">15m</option>
            <option value="1h">1h</option>
            <option value="4h">4h</option>
            <option value="1D">1D</option>
          </Select>
        </div>
        <div className="toolbar-group">
          <Button onClick={() => handleSave(strategy?.graph)} disabled={saving}>
            {saving ? 'Saving...' : 'Save Strategy'}
          </Button>
          <Button variant="secondary" onClick={() => navigate('/')}>
            Back
          </Button>
        </div>
      </Header>

      <div className="flex-1 flex overflow-hidden">
        <StrategyGraph
          strategyId={id || null}
          initialGraph={strategy?.graph}
          onChange={(g: StrategyGraphType) => setStrategy((prev) => prev ? { ...prev, graph: g } : null)}
          readOnly={false}
        />
      </div>
    </div>
  )
}