import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api } from '../api/client'
import type { StrategyCreate, StrategyUpdate } from '../types/strategy'

export function useStrategies(page = 1, pageSize = 20, market?: string) {
  return useQuery({
    queryKey: ['strategies', page, pageSize, market],
    queryFn: () => api.listStrategies(page, pageSize, market),
  })
}

export function useStrategy(id: string | undefined) {
  return useQuery({
    queryKey: ['strategy', id],
    queryFn: () => api.getStrategy(id!),
    enabled: !!id,
  })
}

export function useCreateStrategy() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (data: StrategyCreate) => api.createStrategy(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })
}

export function useUpdateStrategy() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: StrategyUpdate }) => api.updateStrategy(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
      queryClient.invalidateQueries({ queryKey: ['strategy', id] })
    },
  })
}

export function useDeleteStrategy() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.deleteStrategy(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })
}

export function useCloneStrategy() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, name }: { id: string; name: string }) => api.cloneStrategy(id, name),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['strategies'] })
    },
  })
}

export function useStrategyVersions(id: string | undefined) {
  return useQuery({
    queryKey: ['strategyVersions', id],
    queryFn: () => api.getStrategyVersions(id!),
    enabled: !!id,
  })
}

export function useValidateStrategy(id: string | undefined) {
  return useQuery({
    queryKey: ['validateStrategy', id],
    queryFn: () => api.validateStrategy(id!),
    enabled: !!id,
  })
}