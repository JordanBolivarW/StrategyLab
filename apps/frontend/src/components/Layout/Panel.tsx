import { clsx } from 'clsx'
import type { ReactNode } from 'react'
import { Tabs, TabPanel } from '../UI/Tabs'

interface PanelProps<T extends string = string> {
  tabs: Array<{ id: T; label: string; icon?: ReactNode }>
  activeTab: T
  onTabChange: (tabId: T) => void
  children: ReactNode
  className?: string
}

export function Panel<T extends string = string>({ tabs, activeTab, onTabChange, children, className }: PanelProps<T>) {
  return (
    <aside className={clsx('w-80 border-l border-dark-border bg-dark-card flex flex-col overflow-hidden', className)}>
      <Tabs
        tabs={tabs.map(t => ({ id: t.id, label: t.label, icon: t.icon }))}
        activeTab={activeTab}
        onChange={(tabId: string) => onTabChange(tabId as T)}
        variant="pills"
        className="flex border-b border-dark-border bg-dark-card/50"
      />
      <div className="flex-1 overflow-y-auto">
        {tabs.map((tab) => (
          <TabPanel key={tab.id} id={tab.id} activeTab={activeTab}>
            <div className="p-4">{children}</div>
          </TabPanel>
        ))}
      </div>
    </aside>
  )
}

interface SimplePanelProps {
  title: string
  children: ReactNode
  className?: string
}

export function SimplePanel({ title, children, className }: SimplePanelProps) {
  return (
    <div className={clsx('bg-dark-card border border-dark-border rounded-xl', className)}>
      <div className="px-6 py-4 border-b border-dark-border">
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      <div className="p-6">{children}</div>
    </div>
  )
}