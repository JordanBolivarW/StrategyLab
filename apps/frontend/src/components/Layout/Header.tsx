import { clsx } from 'clsx'

interface HeaderProps {
  title?: string
  children?: React.ReactNode
  className?: string
}

export function Header({ title, children, className }: HeaderProps) {
  return (
    <header className={clsx('border-b border-dark-border bg-dark-card/50 backdrop-blur-sm sticky top-0 z-40', className)}>
      <div className="toolbar">
        <div className="toolbar-group">
          {title && <h1 className="text-xl font-bold text-white">{title}</h1>}
        </div>
        <div className="toolbar-group">
          {children}
        </div>
      </div>
    </header>
  )
}