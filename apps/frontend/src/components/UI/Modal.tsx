import type { ReactNode} from 'react';
import { Fragment, useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'
import { clsx } from 'clsx'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  showCloseButton?: boolean
}

export function Modal({ isOpen, onClose, title, children, size = 'md', showCloseButton = true }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  useEffect(() => {
    const overlay = overlayRef.current
    const handleOverlayClick = (e: MouseEvent) => {
      if (e.target === overlay) onClose()
    }

    if (isOpen) {
      overlay?.addEventListener('click', handleOverlayClick)
    }

    return () => {
      overlay?.removeEventListener('click', handleOverlayClick)
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  const sizes = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    full: 'max-w-4xl',
  }

  return createPortal(
    <Fragment>
      <div
        ref={overlayRef}
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-fade-in"
        aria-hidden="true"
      />
      <div
        ref={contentRef}
        className={clsx(
          'fixed inset-0 z-50 flex items-center justify-center p-4 animate-slide-up',
          sizes[size]
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby={title ? 'modal-title' : undefined}
      >
        <div className="w-full bg-dark-card border border-dark-border rounded-xl shadow-xl overflow-hidden">
          {(title || showCloseButton) && (
            <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border">
              {title && <h2 id="modal-title" className="text-lg font-semibold text-white">{title}</h2>}
              {showCloseButton && (
                <button
                  onClick={onClose}
                  className="p-1 rounded-lg text-gray-400 hover:text-white hover:bg-dark-border transition-colors"
                  aria-label="Close modal"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          )}
          <div className="p-6">{children}</div>
        </div>
      </div>
    </Fragment>,
    document.body
  )
}