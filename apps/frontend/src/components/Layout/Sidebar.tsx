import { clsx } from 'clsx'
import type { ReactNode } from 'react'

interface SidebarProps {
  isOpen: boolean
  onClose?: () => void
  children: ReactNode
  className?: string
}

export function Sidebar({ isOpen, onClose, children, className }: SidebarProps) {
  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden animate-fade-in"
          onClick={onClose}
          aria-hidden="true"
        />
      )}
      <aside
        className={clsx(
          'w-64 border-r border-dark-border bg-dark-card flex flex-col overflow-hidden lg:flex lg:block',
          isOpen ? 'translate-x-0' : '-translate-x-full',
          'transition-transform duration-300 ease-in-out',
          className
        )}
      >
        {children}
      </aside>
    </>
  )
}

interface SidebarSectionProps {
  title?: string
  children: ReactNode
  className?: string
}

export function SidebarSection({ title, children, className }: SidebarSectionProps) {
  return (
    <div className={clsx('p-4 border-b border-dark-border', className)}>
      {title && <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-400 mb-3">{title}</h3>}
      {children}
    </div>
  )
}

interface SidebarItemProps {
  label: string
  icon?: ReactNode
  badge?: string
  active?: boolean
  onClick?: () => void
  className?: string
}

export function SidebarItem({ label, icon, badge, active, onClick, className }: SidebarItemProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'w-full px-3 py-2 rounded-lg cursor-pointer transition-colors mb-1 flex items-center justify-between',
        active
          ? 'bg-primary-600/20 border border-primary-500/50 text-white'
          : 'hover:bg-dark-border text-gray-300 hover:text-white',
        className
      )}
    >
      <div className="flex items-center gap-2">
        {icon && <span className="text-lg">{icon}</span>}
        <span className="font-medium">{label}</span>
      </div>
      {badge && (
        <span className="text-xs px-2 py-0.5 rounded-full bg-primary-600/20 text-primary-400 border border-primary-500/50">
          {badge}
        </span>
      )}
    </button>
  )
}