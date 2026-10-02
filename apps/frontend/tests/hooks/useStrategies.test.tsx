import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { vi, describe, it, expect, beforeEach } from 'vitest'
import { useStrategies } from '../hooks/useStrategies'
import { api } from '../api/client'

vi.mock('../api/client', () => ({
  api: {
    listStrategies: vi.fn(),
    getStrategy: vi.fn(),
    createStrategy: vi.fn(),
    updateStrategy: vi.fn(),
    deleteStrategy: vi.fn(),
    cloneStrategy: vi.fn(),
    getStrategyVersions: vi.fn(),
    validateStrategy: vi.fn(),
  },
}))

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}

describe('useStrategies', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('fetches strategies', async () => {
    const mockStrategies = {
      items: [
        { id: '1', name: 'Test 1', market: 'BTCUSDT', timeframe: '1h', graph: { nodes: [], edges: [], metadata: {} }, current_version: 1, user_id: 'u1', created_at: '', updated_at: '' },
        { id: '2', name: 'Test 2', market: 'ETHUSDT', timeframe: '1h', graph: { nodes: [], edges: [], metadata: {} }, current_version: 1, user_id: 'u1', created_at: '', updated_at: '' },
      ],
      total: 2,
      page: 1,
      page_size: 20,
    }
    api.listStrategies.mockResolvedValue(mockStrategies)

    const { result } = renderHook(() => useStrategies(1, 20), { wrapper: createWrapper() })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(result.current.data?.items).toHaveLength(2)
    expect(api.listStrategies).toHaveBeenCalledWith(1, 20, undefined)
  })

  it('fetches strategies with market filter', async () => {
    const mockStrategies = { items: [], total: 0, page: 1, page_size: 20 }
    api.listStrategies.mockResolvedValue(mockStrategies)

    const { result } = renderHook(() => useStrategies(1, 20, 'BTCUSDT'), { wrapper: createWrapper() })

    await waitFor(() => expect(result.current.isSuccess).toBe(true))
    expect(api.listStrategies).toHaveBeenCalledWith(1, 20, 'BTCUSDT')
  })
})