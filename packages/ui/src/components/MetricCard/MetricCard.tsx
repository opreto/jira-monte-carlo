import * as React from 'react'
import { cn } from '../../lib/utils'
import { Card, CardContent, CardHeader } from '../Card'
import { cva, type VariantProps } from 'class-variance-authority'

const metricCardVariants = cva('', {
  variants: {
    trend: {
      up: 'text-emerald-600 dark:text-emerald-400',
      down: 'text-rose-600 dark:text-rose-400',
      neutral: 'text-gray-600 dark:text-gray-400',
    },
  },
})

export interface MetricCardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof metricCardVariants> {
  title: string
  value: string | number
  unit?: string
  description?: string
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string | number
  trendLabel?: string
  icon?: React.ReactNode
  footer?: React.ReactNode
  size?: 'sm' | 'md' | 'lg'
}

const MetricCard = React.forwardRef<HTMLDivElement, MetricCardProps>(
  (
    {
      className,
      title,
      value,
      unit,
      description,
      trend,
      trendValue,
      trendLabel,
      icon,
      footer,
      size = 'md',
      ...props
    },
    ref
  ) => {
    return (
      <Card 
        ref={ref} 
        className={cn(
          'group hover:shadow-glow hover:shadow-primary-500/20',
          'transition-all duration-500',
          className
        )} 
        {...props}
      >
        <CardHeader
          className={cn(
            'flex flex-row items-start justify-between space-y-0',
            'relative',
            {
              'pb-2': size === 'sm',
              'pb-3': size === 'md',
              'pb-4': size === 'lg',
            }
          )}
        >
          <div className="space-y-1">
            <p
              className={cn('font-medium leading-none tracking-tight text-gray-700 dark:text-gray-300', {
                'text-xs': size === 'sm',
                'text-sm': size === 'md',
                'text-base': size === 'lg',
              })}
            >
              {title}
            </p>
            {description && (
              <p
                className={cn('text-gray-500 dark:text-gray-400', {
                  'text-xs': size === 'sm' || size === 'md',
                  'text-sm': size === 'lg',
                })}
              >
                {description}
              </p>
            )}
          </div>
          {icon && (
            <div
              className={cn(
                'text-primary-500 dark:text-primary-400',
                'bg-primary-50 dark:bg-primary-950/30',
                'rounded-lg p-2',
                'shadow-sm shadow-primary-200/50 dark:shadow-primary-900/30',
                {
                  'h-4 w-4': size === 'sm',
                  'h-5 w-5': size === 'md',
                  'h-6 w-6': size === 'lg',
                }
              )}
            >
              {icon}
            </div>
          )}
        </CardHeader>
        <CardContent
          className={cn({
            'pb-2': size === 'sm',
            'pb-3': size === 'md',
            'pb-4': size === 'lg',
          })}
        >
          <div className="space-y-1">
            <div className="flex items-baseline gap-1">
              <span
                className={cn(
                  'font-bold tracking-tight',
                  'bg-gradient-to-r from-gray-900 to-gray-700 dark:from-gray-100 dark:to-gray-300',
                  'bg-clip-text text-transparent',
                  {
                    'text-xl': size === 'sm',
                    'text-2xl sm:text-3xl': size === 'md',
                    'text-3xl sm:text-4xl': size === 'lg',
                  }
                )}
              >
                {value}
              </span>
              {unit && (
                <span
                  className={cn('font-medium text-gray-600 dark:text-gray-400', {
                    'text-sm': size === 'sm',
                    'text-base': size === 'md',
                    'text-lg': size === 'lg',
                  })}
                >
                  {unit}
                </span>
              )}
            </div>
            {(trend || trendValue) && (
              <div
                className={cn(
                  'flex items-center gap-1',
                  {
                    'text-xs': size === 'sm',
                    'text-sm': size === 'md' || size === 'lg',
                  },
                  trend && metricCardVariants({ trend })
                )}
              >
                {trend && <TrendIcon trend={trend} />}
                {trendValue && (
                  <span className="font-medium">
                    {trend === 'up' && '+'}
                    {trendValue}
                    {typeof trendValue === 'number' && '%'}
                  </span>
                )}
                {trendLabel && <span className="text-gray-600 dark:text-gray-400">{trendLabel}</span>}
              </div>
            )}
          </div>
          {footer}
        </CardContent>
      </Card>
    )
  }
)
MetricCard.displayName = 'MetricCard'

// Trend icon component
const TrendIcon = ({ trend }: { trend: 'up' | 'down' | 'neutral' }) => {
  if (trend === 'up') {
    return (
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="h-4 w-4"
      >
        <path
          d="M8 12V4M8 4L4 8M8 4L12 8"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    )
  }

  if (trend === 'down') {
    return (
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="h-4 w-4"
      >
        <path
          d="M8 4V12M8 12L12 8M8 12L4 8"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    )
  }

  return (
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="h-4 w-4"
    >
      <path
        d="M4 8H12"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
    </svg>
  )
}

// MetricCardGrid component for layout
export interface MetricCardGridProps extends React.HTMLAttributes<HTMLDivElement> {
  cols?: 2 | 3 | 4
}

const MetricCardGrid = React.forwardRef<HTMLDivElement, MetricCardGridProps>(
  ({ className, cols = 3, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'grid gap-4',
          {
            'grid-cols-1 sm:grid-cols-2': cols === 2,
            'grid-cols-1 sm:grid-cols-2 lg:grid-cols-3': cols === 3,
            'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4': cols === 4,
          },
          className
        )}
        {...props}
      />
    )
  }
)
MetricCardGrid.displayName = 'MetricCardGrid'

export { MetricCard, MetricCardGrid }