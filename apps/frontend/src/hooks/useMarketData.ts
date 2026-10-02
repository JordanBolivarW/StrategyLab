import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function useMarkets() {
  return useQuery({
    queryKey: ['markets'],
    queryFn: () => api.listMarkets(),
  })
}

export function useMarket(symbol: string | undefined) {
  return useQuery({
    queryKey: ['market', symbol],
    queryFn: () => api.getMarket(symbol!),
    enabled: !!symbol,
  })
}

export function useMarketData(
  symbol: string | undefined,
  timeframe: string,
  startDate?: string,
  endDate?: string,
  limit = 1000
) {
  return useQuery({
    queryKey: ['marketData', symbol, timeframe, startDate, endDate],
    queryFn: () => api.getMarketData(symbol!, timeframe, startDate, endDate, limit),
    enabled: !!symbol && !!timeframe,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}

export function useMcpTools() {
  return useQuery({
    queryKey: ['mcpTools'],
    queryFn: () => api.listMcpTools(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  })
}