import React, { useEffect, useRef, useState } from 'react'
import { cn } from '../../lib/utils'

export interface StickyHeaderProps {
  children: React.ReactNode
  className?: string
  stickyClassName?: string
  offsetTop?: number
  onStickyChange?: (isSticky: boolean) => void
}

export const StickyHeader: React.FC<StickyHeaderProps> = ({
  children,
  className,
  stickyClassName,
  offsetTop = 0,
  onStickyChange,
}) => {
  const [isSticky, setIsSticky] = useState(false)
  const [height, setHeight] = useState<number | 'auto'>('auto')
  const headerRef = useRef<HTMLDivElement>(null)
  const sentinelRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!sentinelRef.current) return

    const observer = new IntersectionObserver(
      ([entry]) => {
        const shouldBeSticky = !entry.isIntersecting
        setIsSticky(shouldBeSticky)
        onStickyChange?.(shouldBeSticky)
      },
      {
        rootMargin: `-${offsetTop}px 0px 0px 0px`,
        threshold: [0],
      }
    )

    observer.observe(sentinelRef.current)

    return () => {
      observer.disconnect()
    }
  }, [offsetTop, onStickyChange])

  // Lock the height when sticky to prevent reflows
  useEffect(() => {
    if (contentRef.current) {
      if (isSticky) {
        // Lock the height to current content height
        const rect = contentRef.current.getBoundingClientRect()
        setHeight(rect.height)
      } else {
        // Restore auto height when not sticky
        setHeight('auto')
      }
    }
  }, [isSticky])

  // Monitor content changes and update height if sticky
  useEffect(() => {
    if (!contentRef.current || !isSticky) return

    const resizeObserver = new ResizeObserver((entries) => {
      for (const entry of entries) {
        if (entry.target === contentRef.current) {
          setHeight(entry.contentRect.height)
        }
      }
    })

    resizeObserver.observe(contentRef.current)

    return () => {
      resizeObserver.disconnect()
    }
  }, [isSticky])

  return (
    <>
      {/* Invisible sentinel element to detect when header should become sticky */}
      <div ref={sentinelRef} aria-hidden="true" />
      
      {/* Main header wrapper */}
      <div
        ref={headerRef}
        className={cn('sticky-header-wrapper', className)}
        style={{
          height: isSticky ? height : 'auto',
        }}
      >
        {/* Actual header content */}
        <div
          ref={contentRef}
          className={cn(
            'sticky-header-content transition-all duration-200',
            isSticky && [
              'fixed left-0 right-0 z-50',
              stickyClassName
            ]
          )}
          style={{
            top: isSticky ? offsetTop : 'auto',
          }}
        >
          {children}
        </div>
      </div>
    </>
  )
}