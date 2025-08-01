import React from 'react'

// Design System Components for Sprint Radar Reports
// Following Opreto brand guidelines and analytics best practices

// Font Awesome v7 style icons implemented as inline SVG
// These follow Font Awesome design patterns for consistency

// Icon Components
export const Icons = {
  // ML/AI indicator - brain icon for ML insights
  mlInsight: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C9.61 2 7.33 3.02 5.75 4.75C4.17 6.48 3.14 8.85 3.02 11.42C2.94 13.1 3.29 14.77 4.01 16.26C4.73 17.75 5.79 19.02 7.11 19.94C7.66 20.29 8.23 20.59 8.83 20.82C9.37 21.03 9.95 21.17 10.53 21.22C10.54 20.65 10.67 20.1 10.91 19.6C11.15 19.09 11.5 18.65 11.93 18.29C12.36 17.94 12.86 17.69 13.4 17.56C13.93 17.43 14.48 17.42 15.02 17.53C15.56 17.64 16.07 17.87 16.52 18.19C16.97 18.52 17.35 18.94 17.62 19.42C17.9 19.9 18.06 20.44 18.1 21C18.14 21.55 18.05 22.11 17.84 22.62C18.4 22.45 18.95 22.24 19.46 21.96C20.78 21.21 21.85 20.11 22.57 18.78C23.3 17.45 23.65 15.94 23.58 14.42C23.51 12.9 23.02 11.44 22.16 10.19C21.3 8.94 20.1 7.95 18.71 7.32C18.58 6.47 18.26 5.67 17.77 4.98C17.17 4.14 16.37 3.47 15.44 3.04C14.51 2.6 13.48 2.42 12.46 2.5C12.31 2.42 12.16 2.3 12 2.25V2ZM12 8C12.53 8 13.04 8.21 13.41 8.59C13.79 8.96 14 9.47 14 10C14 10.53 13.79 11.04 13.41 11.41C13.04 11.79 12.53 12 12 12C11.47 12 10.96 11.79 10.59 11.41C10.21 11.04 10 10.53 10 10C10 9.47 10.21 8.96 10.59 8.59C10.96 8.21 11.47 8 12 8Z" />
    </svg>
  ),
  
  // Info icon for tooltips - question mark circle
  info: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path fillRule="evenodd" d="M2.25 12c0-5.385 4.365-9.75 9.75-9.75s9.75 4.365 9.75 9.75-4.365 9.75-9.75 9.75S2.25 17.385 2.25 12zm11.378-3.917c-.89-.777-2.366-.777-3.255 0a.75.75 0 01-.988-1.129c1.454-1.272 3.776-1.272 5.23 0 1.513 1.324 1.513 3.518 0 4.842a3.75 3.75 0 01-.837.552c-.676.328-1.028.774-1.028 1.152v.75a.75.75 0 01-1.5 0v-.75c0-1.279 1.06-2.107 1.875-2.502.182-.088.351-.199.503-.331.83-.727.83-1.857 0-2.584zM12 18a.75.75 0 100-1.5.75.75 0 000 1.5z" clipRule="evenodd" />
    </svg>
  ),
  
  // Trend icons
  trendUp: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </svg>
  ),
  
  trendDown: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="23 18 13.5 8.5 8.5 13.5 1 6" />
      <polyline points="17 18 23 18 23 12" />
    </svg>
  ),
  
  // Chart icon
  chart: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="18" y1="20" x2="18" y2="10" />
      <line x1="12" y1="20" x2="12" y2="4" />
      <line x1="6" y1="20" x2="6" y2="14" />
    </svg>
  ),
  
  // Calendar icon
  calendar: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  ),
  
  // Alert icon
  alert: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  ),
  
  // Check icon
  check: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  ),
  
  // Sprint/Agile icon (using a circular arrow for sprint cycles)
  sprint: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M23 4v6h-6" />
      <path d="M1 20v-6h6" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  ),
  
  // Health icon (using a heart with pulse)
  health: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
    </svg>
  ),
  
  // Forecast icon (using a forward arrow with dots)
  forecast: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <line x1="5" y1="12" x2="19" y2="12" />
      <polyline points="12 5 19 12 12 19" />
      <circle cx="4" cy="12" r="1" fill="currentColor" />
      <circle cx="8" cy="12" r="1" fill="currentColor" />
    </svg>
  ),
  
  // Settings/Configuration icon
  settings: (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 1v6m0 6v6m4.22-10.22l4.24-4.24M6.34 17.66l4.24-4.24m0 4.24l4.24 4.24M6.34 6.34l4.24 4.24" />
    </svg>
  ),
}

// Typography system with Opreto fonts
export const fontStyles = `
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
  
  /* Sublima font fallback to Georgia serif for display headings */
  .font-display {
    font-family: 'Sublima', Georgia, 'Times New Roman', serif;
    font-weight: 700;
    letter-spacing: -0.02em;
  }
  
  .font-sans {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
`

// Color palette
export const colors = {
  // Primary colors
  teal: {
    50: '#f0fdfa',
    100: '#ccfbf1',
    200: '#99f6e4',
    300: '#5eead4',
    400: '#2dd4bf',
    500: '#14b8a6',
    600: '#0d9488',
    700: '#0f766e',
    800: '#115e59',
    900: '#134e4a',
  },
  
  // Status colors
  success: '#00A86B',
  warning: '#FFA500',
  error: '#DC143C',
  info: '#0E5473',
  
  // Neutral colors
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },
}

// Professional Card component
interface CardProps {
  children: React.ReactNode
  className?: string
  elevated?: boolean
}

export const Card: React.FC<CardProps> = ({ children, className = '', elevated = false }) => (
  <div className={`rounded-lg bg-white border border-gray-200 ${elevated ? 'shadow-lg' : 'shadow-sm'} transition-all duration-200 hover:shadow-lg relative ${className}`}>
    <div className="absolute inset-0 bg-gradient-to-br from-teal-50/5 to-transparent pointer-events-none rounded-lg" />
    {children}
  </div>
)

export const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`px-6 py-4 border-b border-gray-100 ${className}`}>
    {children}
  </div>
)

export const CardTitle: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <h3 className={`text-lg font-semibold font-sans text-gray-900 ${className}`}>
    {children}
  </h3>
)

export const CardContent: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`p-6 ${className}`}>{children}</div>
)

// Professional Table components
export const Table: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div className="overflow-x-auto rounded-lg bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
    <table className="min-w-full divide-y divide-gray-200">{children}</table>
  </div>
)

export const TableHeader: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <thead className="bg-gray-50">{children}</thead>
)

export const TableBody: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <tbody className="bg-white divide-y divide-gray-200">{children}</tbody>
)

export const TableRow: React.FC<{ children: React.ReactNode } & React.HTMLAttributes<HTMLTableRowElement>> = ({ children, ...props }) => (
  <tr className="transition-all duration-150 hover:bg-teal-50/20 hover:shadow-sm" {...props}>{children}</tr>
)

export const TableHead: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <th className="px-6 py-3 text-left text-xs font-medium font-sans text-gray-700 uppercase tracking-wider">
    {children}
  </th>
)

export const TableCell: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <td className={`px-6 py-4 whitespace-nowrap text-sm font-sans text-gray-900 ${className}`}>
    {children}
  </td>
)

// ML Tooltip component with improved design
interface MLTooltipProps {
  children: React.ReactNode
  content: React.ReactNode
}

export const MLTooltip: React.FC<MLTooltipProps> = ({ children, content }) => (
  <div className="relative inline-flex items-center group">
    {children}
    <div className="ml-1.5 cursor-help relative flex items-center">
      <div className="w-5 h-5 bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded flex items-center justify-center shadow-sm group-hover:shadow-md transition-all duration-200">
        {Icons.mlInsight}
      </div>
      <div className="absolute z-[9999] invisible group-hover:visible bg-gray-900/95 backdrop-blur-sm text-white text-sm rounded-lg p-4 w-80 left-1/2 transform -translate-x-1/2 bottom-full mb-2 shadow-2xl font-sans leading-relaxed">
        <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 bg-gray-900/95 rotate-45"></div>
        <div className="flex items-start space-x-2 mb-2">
          <div className="text-purple-400">{Icons.mlInsight}</div>
          <div className="text-xs font-semibold text-purple-400 uppercase tracking-wider">Machine Learning Insight</div>
        </div>
        {content}
      </div>
    </div>
  </div>
)

// Info Tooltip component
interface InfoTooltipProps {
  children: React.ReactNode
  content: React.ReactNode
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({ children, content }) => (
  <div className="group relative inline-block">
    {children}
    <div className="absolute z-[9999] invisible group-hover:visible bg-gray-900 text-white text-sm normal-case tracking-normal rounded-lg p-4 w-72 right-0 bottom-full mb-2 shadow-2xl font-sans leading-relaxed">
      <div className="absolute -bottom-1 right-4 w-2 h-2 bg-gray-900 rotate-45"></div>
      {content}
    </div>
  </div>
)

// Chart Description component
interface ChartDescriptionProps {
  title?: string
  description?: string
  importance?: string
  lookFor?: string
}

export const ChartDescription: React.FC<ChartDescriptionProps> = ({ title, description, importance, lookFor }) => (
  <div className="bg-teal-50/30 rounded-lg p-4 mb-4 text-sm font-sans">
    {title && <div className="font-semibold text-teal-800 mb-1">{title}</div>}
    {description && <div className="text-gray-700 mb-2"><strong>What it shows:</strong> {description}</div>}
    {importance && <div className="text-gray-700 mb-2"><strong>Why it matters:</strong> {importance}</div>}
    {lookFor && <div className="text-gray-700"><strong>What to look for:</strong> {lookFor}</div>}
  </div>
)

// Chart wrapper component
interface ChartProps {
  data: any
  layout: any
  title?: string
  description?: string
  importance?: string
  lookFor?: string
  chartType?: string
}

export const Chart: React.FC<ChartProps> = ({ data, layout, title, description, importance, lookFor, chartType }) => (
  <div className="rounded-lg bg-white border border-gray-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-200">
    {description && (
      <div className="p-4 border-b border-gray-100">
        <ChartDescription
          description={description}
          importance={importance}
          lookFor={lookFor}
        />
      </div>
    )}
    <div 
      data-plotly
      data-plotly-data={JSON.stringify(data)}
      {...(chartType && { 'data-chart-type': chartType })}
      data-plotly-layout={JSON.stringify({
        ...layout,
        title: title ? { 
          text: title,
          font: {
            family: 'Sublima, Georgia, serif',
            size: 18,
            color: '#022d2c',
            weight: 600,
          }
        } : layout?.title,
        font: {
          family: 'Inter, system-ui, sans-serif',
          size: 12,
          color: '#495057',
        },
        paper_bgcolor: 'rgba(0, 0, 0, 0)',
        plot_bgcolor: 'rgba(0, 0, 0, 0)',
        xaxis: {
          gridcolor: 'rgba(229, 231, 235, 0.5)',
          zerolinecolor: 'rgba(209, 213, 219, 0.5)',
          tickfont: {
            color: '#6b7280',
          },
          ...layout?.xaxis,
        },
        yaxis: {
          gridcolor: 'rgba(229, 231, 235, 0.5)',
          zerolinecolor: 'rgba(209, 213, 219, 0.5)',
          tickfont: {
            color: '#6b7280',
          },
          ...layout?.yaxis,
        },
        legend: {
          bgcolor: 'rgba(255, 255, 255, 0.9)',
          bordercolor: 'rgba(229, 231, 235, 0.5)',
          borderwidth: 1,
          font: {
            color: '#4b5563',
          },
          ...layout?.legend,
        },
      })}
      data-plotly-config={JSON.stringify({ responsive: true, displayModeBar: false })}
      style={{ width: '100%', height: layout?.height || 400 }}
      className="chart-placeholder"
    />
  </div>
)

// Enhanced Header component with clean gradient
export const Header: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <header className="bg-gradient-to-r from-teal-700 via-teal-800 to-teal-900 shadow-lg relative overflow-hidden">
    {/* Subtle gradient overlay for depth */}
    <div className="absolute inset-0 bg-gradient-to-br from-black/10 via-transparent to-black/20 pointer-events-none" />
    <div className="relative z-10">
      {children}
    </div>
  </header>
)

// Metric Card component
interface MetricCardProps {
  title: string
  value: string | number | React.ReactNode
  unit?: string
  description?: string
  trend?: 'up' | 'down' | 'neutral'
  size?: 'sm' | 'md' | 'lg'
  highlight?: boolean
  tooltip?: string
}

export const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  unit, 
  description, 
  trend, 
  size = 'md', 
  highlight = false, 
  tooltip 
}) => (
  <Card className={`hover:shadow-md transition-all duration-200 ${highlight ? 'border-teal-500 border-2' : ''} overflow-visible`}>
    <CardContent className="p-4 relative">
      {tooltip && (
        <div className="absolute top-2 right-2 z-10">
          <InfoTooltip content={tooltip}>
            <div className="w-4 h-4 bg-gray-200 text-gray-600 rounded-full flex items-center justify-center hover:bg-gray-300 transition-colors cursor-help">
              {Icons.info}
            </div>
          </InfoTooltip>
        </div>
      )}
      <div className="text-xs text-gray-600 mb-1 font-sans uppercase tracking-wider text-center">
        {title}
      </div>
      <div className={`font-bold font-sans text-gray-900 text-center ${size === 'sm' ? 'text-xl' : size === 'lg' ? 'text-3xl' : 'text-2xl'}`}>
        {value}
        {unit && <span className="text-sm text-gray-600 ml-1 font-normal">{unit}</span>}
      </div>
      {description && <div className="text-xs text-gray-500 mt-1 text-center">{description}</div>}
      {trend && (
        <div className={`text-xs mt-1 flex items-center justify-center ${
          trend === 'up' ? 'text-green-600' : 
          trend === 'down' ? 'text-red-600' : 
          'text-gray-600'
        }`}>
          {trend === 'up' ? Icons.trendUp : trend === 'down' ? Icons.trendDown : '→'} 
        </div>
      )}
    </CardContent>
  </Card>
)