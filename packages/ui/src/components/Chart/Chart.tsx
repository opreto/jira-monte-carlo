import * as React from 'react'
import Plot from 'react-plotly.js'
import { PlotParams } from 'react-plotly.js'
import { cn } from '../../lib/utils'
import { chartColors, chartLayouts } from './constants'

export interface ChartProps extends Partial<PlotParams> {
  title?: string
  className?: string
  containerClassName?: string
  responsive?: boolean
}

const Chart = React.forwardRef<HTMLDivElement, ChartProps>(
  (
    {
      title,
      className,
      containerClassName,
      responsive = true,
      data = [],
      layout = {},
      config = {},
      ...props
    },
    ref
  ) => {
    // Merge default layout with provided layout
    const mergedLayout = React.useMemo(
      () => ({
        title: title ? { text: title } : layout.title,
        font: {
          family:
            'ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif',
          size: 12,
          color: '#374151', // gray-700
          ...layout.font,
        },
        paper_bgcolor: 'rgba(0, 0, 0, 0)', // transparent
        plot_bgcolor: 'rgba(0, 0, 0, 0)', // transparent
        margin: {
          l: 50,
          r: 50,
          b: 50,
          t: title ? 60 : 30,
          pad: 4,
          ...layout.margin,
        },
        hovermode: 'closest' as const,
        showlegend: true,
        legend: {
          bgcolor: 'rgba(255, 255, 255, 0.9)',
          bordercolor: '#e5e7eb', // gray-200
          borderwidth: 1,
          ...layout.legend,
        },
        xaxis: {
          gridcolor: '#f3f4f6', // gray-100
          zerolinecolor: '#e5e7eb', // gray-200
          ...layout.xaxis,
        },
        yaxis: {
          gridcolor: '#f3f4f6', // gray-100
          zerolinecolor: '#e5e7eb', // gray-200
          ...layout.yaxis,
        },
        ...layout,
      }),
      [title, layout]
    )

    // Merge default config with provided config
    const mergedConfig = React.useMemo(
      () => ({
        displayModeBar: true,
        displaylogo: false,
        toImageButtonOptions: {
          format: 'png' as const,
          filename: title?.replace(/\s+/g, '-').toLowerCase() || 'chart',
          height: 600,
          width: 1000,
          scale: 2,
        },
        modeBarButtonsToRemove: ['lasso2d' as const, 'select2d' as const],
        ...config,
      }),
      [title, config]
    )

    return (
      <div
        ref={ref}
        className={cn(
          'relative w-full overflow-hidden rounded-xl',
          'bg-white/80 dark:bg-gray-900/80',
          'backdrop-blur-xl backdrop-saturate-150',
          'border border-white/20 dark:border-gray-700/30',
          'shadow-lg shadow-gray-900/5 dark:shadow-black/20',
          'transition-all duration-300',
          'hover:shadow-xl hover:shadow-primary-500/10 dark:hover:shadow-primary-400/10',
          containerClassName
        )}
      >
        <Plot
          data={data}
          layout={mergedLayout}
          config={mergedConfig}
          useResizeHandler={responsive}
          className={cn('w-full', className)}
          style={{ width: '100%', height: '100%' }}
          {...props}
        />
      </div>
    )
  }
)

Chart.displayName = 'Chart'


export { Chart }