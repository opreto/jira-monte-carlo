import * as React from 'react'
import { cn } from '../../lib/utils'

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-xl',
      'bg-white/80 dark:bg-gray-900/80',
      'backdrop-blur-xl backdrop-saturate-150',
      'border border-white/20 dark:border-gray-700/30',
      'shadow-lg shadow-gray-900/5 dark:shadow-black/20',
      'transition-all duration-300',
      'hover:shadow-xl hover:shadow-primary-500/10 dark:hover:shadow-primary-400/10',
      'hover:border-white/30 dark:hover:border-gray-600/40',
      'hover:translate-y-[-2px]',
      'relative overflow-hidden',
      'before:absolute before:inset-0',
      'before:bg-gradient-to-br before:from-white/10 before:to-transparent',
      'before:pointer-events-none',
      className
    )}
    {...props}
  />
))
Card.displayName = 'Card'

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex flex-col space-y-1.5 p-6',
      'border-b border-gray-100/50 dark:border-gray-800/50',
      'bg-gradient-to-r from-transparent via-gray-50/20 to-transparent dark:via-gray-800/20',
      className
    )}
    {...props}
  />
))
CardHeader.displayName = 'CardHeader'

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight',
      'bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300',
      'bg-clip-text text-transparent',
      className
    )}
    {...props}
  />
))
CardTitle.displayName = 'CardTitle'

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn(
      'text-sm text-gray-600 dark:text-gray-400',
      'leading-relaxed',
      className
    )}
    {...props}
  />
))
CardDescription.displayName = 'CardDescription'

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div 
    ref={ref} 
    className={cn(
      'p-6 pt-0',
      'relative z-10',
      className
    )} 
    {...props} 
  />
))
CardContent.displayName = 'CardContent'

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'flex items-center p-6 pt-0',
      'border-t border-gray-100/30 dark:border-gray-800/30',
      'mt-auto',
      className
    )}
    {...props}
  />
))
CardFooter.displayName = 'CardFooter'

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }