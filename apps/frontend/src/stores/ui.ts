import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info' | 'warning'
}

interface UIState {
  // Sidebar
  sidebarOpen: boolean
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void

  // Theme
  darkMode: boolean
  toggleTheme: () => void

  // Toasts
  toasts: Toast[]
  addToast: (message: string, type: Toast['type']) => void
  removeToast: (id: string) => void

  // Modals
  modals: Record<string, { isOpen: boolean; data?: unknown }>
  openModal: (key: string, data?: unknown) => void
  closeModal: (key: string) => void
  isModalOpen: (key: string) => boolean

  // Loading states
  globalLoading: boolean
  setGlobalLoading: (loading: boolean) => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      sidebarOpen: true,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      darkMode: true,
      toggleTheme: () => set((state) => ({ darkMode: !state.darkMode })),

      toasts: [],
      addToast: (message, type) =>
        set((state) => ({
          toasts: [...state.toasts, { id: Date.now().toString(), message, type }],
        })),
      removeToast: (id) => set((state) => ({ toasts: state.toasts.filter((t) => t.id !== id) })),

      modals: {},
      openModal: (key, data) =>
        set((state) => ({ modals: { ...state.modals, [key]: { isOpen: true, data } } })),
      closeModal: (key) =>
        set((state) => ({ modals: { ...state.modals, [key]: { ...state.modals[key], isOpen: false } } })),
      isModalOpen: (key) => get().modals[key]?.isOpen ?? false,

      globalLoading: false,
      setGlobalLoading: (loading) => set({ globalLoading: loading }),
    }),
    {
      name: 'ui-store',
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        darkMode: state.darkMode,
      }),
    }
  )
)