import * as React from 'react'
import { cn } from '../../lib/utils'

export interface ChartSSRProps {
  title?: string
  className?: string
  containerClassName?: string
  data?: any[]
  layout?: any
  config?: any
  responsive?: boolean
}

/**
 * Server-side rendering safe version of Chart component
 * Renders a placeholder div that can be hydrated client-side with Plotly
 */
export const ChartSSR = React.forwardRef<HTMLDivElement, ChartSSRProps>(
  ({ title, className, containerClassName, data = [], layout = {}, config = {}, responsive = true }, ref) => {
    const mergedLayout = {
      ...layout,
      title: title || layout.title,
    }

    const mergedConfig = {
      responsive,
      displayModeBar: false,
      ...config,
    }

    return (
      <div
        ref={ref}
        className={cn(
          'relative w-full overflow-hidden rounded-lg border border-gray-200 bg-white shadow-sm',
          containerClassName
        )}
      >
        <div
          data-plotly
          data-plotly-data={JSON.stringify(data)}
          data-plotly-layout={JSON.stringify(mergedLayout)}
          data-plotly-config={JSON.stringify(mergedConfig)}
          className={cn('w-full bg-gray-50 flex items-center justify-center', className)}
          style={{ height: mergedLayout.height || 400 }}
        >
          <div className="text-gray-400">Loading chart...</div>
        </div>
      </div>
    )
  }
)

ChartSSR.displayName = 'ChartSSR'

export default ChartSSR