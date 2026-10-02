import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { BacktestCreate } from '../types/strategy'

export function useBacktests(strategyId?: string, status?: string) {
  return useQuery({
    queryKey: ['backtests', strategyId, status],
    queryFn: () => api.listBacktests(strategyId, status),
  })
}

export function useBacktest(id: string | undefined) {
  return useQuery({
    queryKey: ['backtest', id],
    queryFn: () => api.getBacktest(id!),
    enabled: !!id,
  })
}

export function useRunBacktest() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: BacktestCreate) => api.createBacktest(data),
    onSuccess: (newBacktest) => {
      queryClient.invalidateQueries({ queryKey: ['backtests'] })
      return newBacktest
    },
  })
}

export function useBacktestTrades(id: string | undefined) {
  return useQuery({
    queryKey: ['backtestTrades', id],
    queryFn: () => api.getBacktestTrades(id!),
    enabled: !!id,
  })
}

export function useBacktestMetrics(id: string | undefined) {
  return useQuery({
    queryKey: ['backtestMetrics', id],
    queryFn: () => api.getBacktestMetrics(id!),
    enabled: !!id,
  })
}