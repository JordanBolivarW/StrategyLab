import { clsx } from 'clsx'

interface Tab {
  id: string
  label: string
  icon?: React.ReactNode
  disabled?: boolean
}

interface TabsProps {
  tabs: Tab[]
  activeTab: string
  onChange: (tabId: string) => void
  variant?: 'default' | 'pills' | 'underline'
  className?: string
}

export function Tabs({ tabs, activeTab, onChange, variant = 'default', className }: TabsProps) {
  const variantStyles = {
    default: 'border-b border-dark-border',
    pills: '',
    underline: 'border-b border-dark-border',
  }

  const tabStyles = {
    default: 'px-4 py-2 text-sm font-medium text-gray-400 hover:text-white hover:bg-dark-border transition-colors cursor-pointer border-b-2 border-transparent',
    pills: 'px-4 py-2 text-sm font-medium text-gray-400 hover:text-white rounded-lg transition-colors cursor-pointer',
    underline: 'px-4 py-2 text-sm font-medium text-gray-400 hover:text-white cursor-pointer border-b-2 border-transparent',
  }

  const activeStyles = {
    default: 'text-primary-400 border-primary-500',
    pills: 'bg-primary-600 text-white',
    underline: 'text-primary-400 border-primary-500',
  }

  return (
    <div className={clsx(variantStyles[variant], className)} role="tablist">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`${tab.id}-panel`}
          id={`${tab.id}-tab`}
          onClick={() => !tab.disabled && onChange(tab.id)}
          disabled={tab.disabled}
          className={clsx(
            tabStyles[variant],
            activeTab === tab.id && activeStyles[variant],
            tab.disabled && 'opacity-50 cursor-not-allowed',
            'flex items-center gap-2'
          )}
        >
          {tab.icon && <span className="flex-shrink-0">{tab.icon}</span>}
          {tab.label}
        </button>
      ))}
    </div>
  )
}

interface TabPanelProps {
  id: string
  activeTab: string
  children: React.ReactNode
  className?: string
}

export function TabPanel({ id, activeTab, children, className }: TabPanelProps) {
  if (activeTab !== id) return null

  return (
    <div
      role="tabpanel"
      id={`${id}-panel`}
      aria-labelledby={`${id}-tab`}
      className={clsx('animate-fade-in', className)}
    >
      {children}
    </div>
  )
}