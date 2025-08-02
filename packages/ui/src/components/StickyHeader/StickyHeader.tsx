import * as React from 'react'
import { cn } from '../../lib/utils'

export interface StickyHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
  stickyClassName?: string
  offsetTop?: number
  zIndex?: number
}

const StickyHeader = React.forwardRef<HTMLDivElement, StickyHeaderProps>(
  ({ children, className, stickyClassName, offsetTop = 0, zIndex = 100, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'sticky bg-white transition-shadow duration-200',
          className,
          stickyClassName
        )}
        style={{
          top: offsetTop,
          zIndex,
        }}
        {...props}
      >
        {children}
      </div>
    )
  }
)
StickyHeader.displayName = 'StickyHeader'

export { StickyHeader }