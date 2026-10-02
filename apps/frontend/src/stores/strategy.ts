import { create } from 'zustand'
import type { StrategyGraph } from '../types/strategy'

interface StrategyState {
  currentStrategyId: string | null
  setCurrentStrategyId: (id: string | null) => void

  currentGraph: StrategyGraph | null
  setCurrentGraph: (graph: StrategyGraph | null) => void
  updateNodeInGraph: (nodeId: string, data: Partial<Record<string, unknown>>) => void
  updateNodePosition: (nodeId: string, position: { x: number; y: number }) => void
  addNodeToGraph: (node: StrategyGraph['nodes'][0]) => void
  removeNodeFromGraph: (nodeId: string) => void
  addEdgeToGraph: (edge: StrategyGraph['edges'][0]) => void
  removeEdgeFromGraph: (edgeId: string) => void

  unsavedChanges: boolean
  setUnsavedChanges: (value: boolean) => void
  markSaved: () => void

  // History for undo/redo
  history: StrategyGraph[]
  historyIndex: number
  pushHistory: (graph: StrategyGraph) => void
  undo: () => StrategyGraph | null
  redo: () => StrategyGraph | null
  canUndo: () => boolean
  canRedo: () => boolean
}

const MAX_HISTORY = 50

export const useStrategyStore = create<StrategyState>((set, get) => ({
  currentStrategyId: null,
  setCurrentStrategyId: (id) => set({ currentStrategyId: id }),

  currentGraph: null,
  setCurrentGraph: (graph) => set({ currentGraph: graph, unsavedChanges: !!graph }),
  updateNodeInGraph: (nodeId, data) =>
    set((state) => ({
      currentGraph: state.currentGraph
        ? {
            ...state.currentGraph,
            nodes: state.currentGraph.nodes.map((n) =>
              n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
            ),
          }
        : null,
      unsavedChanges: true,
    })),
  updateNodePosition: (nodeId, position) =>
    set((state) => ({
      currentGraph: state.currentGraph
        ? {
            ...state.currentGraph,
            nodes: state.currentGraph.nodes.map((n) =>
              n.id === nodeId ? { ...n, position } : n
            ),
          }
        : null,
      unsavedChanges: true,
    })),
  addNodeToGraph: (node) =>
    set((state) => ({
      currentGraph: state.currentGraph
        ? { ...state.currentGraph, nodes: [...state.currentGraph.nodes, node] }
        : { nodes: [node], edges: [], metadata: {} },
      unsavedChanges: true,
    })),
  removeNodeFromGraph: (nodeId) =>
    set((state) => ({
      currentGraph: state.currentGraph
        ? {
            ...state.currentGraph,
            nodes: state.currentGraph.nodes.filter((n) => n.id !== nodeId),
            edges: state.currentGraph.edges.filter(
              (e) => e.source !== nodeId && e.target !== nodeId
            ),
          }
        : null,
      unsavedChanges: true,
    })),
  addEdgeToGraph: (edge) =>
    set((state) => ({
      currentGraph: state.currentGraph
        ? { ...state.currentGraph, edges: [...state.currentGraph.edges, edge] }
        : { nodes: [], edges: [edge], metadata: {} },
      unsavedChanges: true,
    })),
  removeEdgeFromGraph: (edgeId) =>
    set((state) => ({
      currentGraph: state.currentGraph
        ? {
            ...state.currentGraph,
            edges: state.currentGraph.edges.filter((e) => e.id !== edgeId),
          }
        : null,
      unsavedChanges: true,
    })),

  unsavedChanges: false,
  setUnsavedChanges: (value) => set({ unsavedChanges: value }),
  markSaved: () => set({ unsavedChanges: false }),

  history: [],
  historyIndex: -1,
  pushHistory: (graph) =>
    set((state) => {
      const newHistory = state.history.slice(0, state.historyIndex + 1)
      newHistory.push(graph)
      if (newHistory.length > MAX_HISTORY) newHistory.shift()
      return { history: newHistory, historyIndex: newHistory.length - 1 }
    }),
  undo: () => {
    const { history, historyIndex } = get()
    if (historyIndex <= 0) return null
    const newIndex = historyIndex - 1
    set({ historyIndex: newIndex })
    return history[newIndex]
  },
  redo: () => {
    const { history, historyIndex } = get()
    if (historyIndex >= history.length - 1) return null
    const newIndex = historyIndex + 1
    set({ historyIndex: newIndex })
    return history[newIndex]
  },
  canUndo: () => get().historyIndex > 0,
  canRedo: () => get().historyIndex < get().history.length - 1,
}))