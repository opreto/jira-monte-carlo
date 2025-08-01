import React from 'react'
import { ReportData } from '../types'

// Professional Opreto-styled components with Hero archetype design
const Card = ({ children, className = '', elevated = false }: any) => (
  <div className={`rounded-lg bg-white border border-gray-200 ${elevated ? 'shadow-lg' : 'shadow-sm'} transition-all duration-200 hover:shadow-lg relative overflow-hidden ${className}`}>
    <div className="absolute inset-0 bg-gradient-to-br from-teal-50/5 to-transparent pointer-events-none" />
    {children}
  </div>
)

const CardHeader = ({ children, className = '' }: any) => (
  <div className={`px-6 py-4 border-b border-gray-100 ${className}`}>
    {children}
  </div>
)

const CardTitle = ({ children, className = '' }: any) => (
  <h3 className={`text-lg font-semibold font-sans text-gray-900 ${className}`}>
    {children}
  </h3>
)

const CardContent = ({ children, className = '' }: any) => (
  <div className={`p-6 ${className}`}>{children}</div>
)

// Professional MetricCard with Opreto styling and hexagonal accents
const MetricCard = ({ title, value, unit, description, trend, icon, size = 'md', highlight = false }: any) => (
  <Card className={`group hover:shadow-lg transition-all duration-300 ${highlight ? 'border-teal-500' : ''}`} elevated={highlight}>
    <CardContent className="text-center">
      <div className="flex flex-col items-center">
        {icon && (
          <div className="relative">
            <div className="absolute inset-0 bg-teal-100 rounded-lg transform rotate-45 scale-110" />
            <div className="relative text-teal-700 bg-white rounded-lg p-3 mb-3 shadow-sm">
              {icon}
            </div>
          </div>
        )}
        <div className="text-sm text-gray-600 mb-1 font-medium font-sans">{title}</div>
        <div className={`font-bold font-sans text-gray-900 ${size === 'sm' ? 'text-2xl' : 'text-3xl'}`}>
          {value}
          {unit && <span className="text-lg text-gray-600 ml-1">{unit}</span>}
        </div>
        {description && <div className="text-sm text-gray-500 mt-1">{description}</div>}
        {trend && (
          <div className={`text-sm mt-2 flex items-center gap-1 ${
            trend === 'up' ? 'text-green-600' : 
            trend === 'down' ? 'text-red-600' : 
            'text-gray-600'
          }`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} 
            <span className="font-medium">{trend}</span>
          </div>
        )}
      </div>
    </CardContent>
  </Card>
)

// Professional Table with Opreto styling
const Table = ({ children }: any) => (
  <div className="overflow-x-auto rounded-lg bg-white border border-gray-200 shadow-sm hover:shadow-md transition-shadow duration-200">
    <table className="min-w-full divide-y divide-gray-200">{children}</table>
  </div>
)

const TableHeader = ({ children }: any) => (
  <thead className="bg-gray-50">{children}</thead>
)

const TableBody = ({ children }: any) => (
  <tbody className="bg-white divide-y divide-gray-200">{children}</tbody>
)

const TableRow = ({ children, ...props }: any) => (
  <tr className="transition-all duration-150 hover:bg-teal-50/20 hover:shadow-sm" {...props}>{children}</tr>
)

const TableHead = ({ children }: any) => (
  <th className="px-6 py-3 text-left text-xs font-medium font-sans text-gray-700 uppercase tracking-wider">
    {children}
  </th>
)

const TableCell = ({ children, className = '' }: any) => (
  <td className={`px-6 py-4 whitespace-nowrap text-sm font-sans text-gray-900 ${className}`}>
    {children}
  </td>
)

// Hexagonal badge component
const HexBadge = ({ children, color = 'teal' }: any) => (
  <div className="relative inline-flex items-center justify-center">
    <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
      <polygon 
        points="50,5 90,25 90,75 50,95 10,75 10,25" 
        className={`fill-${color}-50 stroke-${color}-500`}
        strokeWidth="2"
      />
    </svg>
    <span className={`relative z-10 text-${color}-800 font-semibold px-4 py-2`}>
      {children}
    </span>
  </div>
)

// Chart component with Opreto styling and professional polish
const Chart = ({ data, layout, title }: any) => (
  <div className="rounded-lg bg-white border border-gray-200 shadow-sm overflow-hidden hover:shadow-md transition-shadow duration-200">
    <div 
      data-plotly
      data-plotly-data={JSON.stringify(data)}
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
      className="chart-placeholder bg-gray-50 flex items-center justify-center"
    >
      <div className="text-gray-400">Chart will render here</div>
    </div>
  </div>
)

// Opreto professional color palette
const chartColors = {
  primary: '#03564c', // Teal
  secondary: '#0E5473', // Cerulean Blue
  tertiary: '#6B1229', // Burgundy
  quaternary: '#FF8C00', // Dark Orange
  success: '#00A86B', // Jade Green
  danger: '#DC143C', // Crimson
  warning: '#FFA500', // Orange
}

interface SprintReportProps {
  data: ReportData
}

// Typography system with Opreto fonts
const fontStyles = `
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

export const MinimalSprintReport: React.FC<SprintReportProps> = ({ data }) => {
  const {
    projectName,
    generatedAt,
    remainingWork,
    velocityMetrics,
    simulationResults,
    processHealth,
    sprints,
  } = data

  // Format date
  const formattedDate = new Date(generatedAt).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })

  // Calculate completion percentage
  const completedWork = sprints.reduce((sum, sprint) => sum + sprint.completedPoints, 0)
  const totalWork = completedWork + remainingWork
  const completionPercentage = totalWork > 0 ? (completedWork / totalWork) * 100 : 0

  // Get confidence levels
  const p50 = simulationResults.percentiles['0.5'] || 0
  const p70 = simulationResults.percentiles['0.7'] || 0
  const p85 = simulationResults.percentiles['0.85'] || 0
  const p95 = simulationResults.percentiles['0.95'] || 0

  // SVG Icons with professional style
  const VelocityIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
    </svg>
  )

  const ProgressIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  )

  const HealthIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
    </svg>
  )

  const CalendarIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header with Hero gradient */}
      <style dangerouslySetInnerHTML={{ __html: fontStyles }} />
      <header className="bg-gradient-to-r from-teal-700 via-teal-800 to-teal-900 shadow-lg relative overflow-hidden">
        {/* Hero pattern overlay */}
        <div className="absolute inset-0 opacity-10">
          <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
            <pattern id="hexagons" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
              <polygon points="20,0 40,10 40,30 20,40 0,30 0,10" fill="none" stroke="white" strokeWidth="0.5" />
            </pattern>
            <rect width="100" height="100" fill="url(#hexagons)" />
          </svg>
        </div>
        <div className="absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 relative z-10">
          <h1 className="text-4xl md:text-5xl font-display text-white mb-2">
            {projectName} Sprint Performance Report
          </h1>
          <p className="text-lg text-teal-100">
            Monte Carlo Simulation Forecast • Generated on {formattedDate}
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Executive Summary */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Executive Summary</h2>
          <Card elevated>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 rounded-lg bg-gradient-to-br from-teal-50/50 to-transparent">
                  <div className="text-3xl font-bold text-teal-700">
                    {velocityMetrics.average.toFixed(1)}
                    <span className="text-lg text-gray-600 ml-1">pts/sprint</span>
                  </div>
                  <div className="text-sm text-gray-600 font-medium">Velocity</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-gradient-to-br from-cerulean-50/30 to-transparent">
                  <div className="text-3xl font-bold text-teal-700">
                    {completionPercentage.toFixed(1)}
                    <span className="text-lg text-gray-600 ml-1">%</span>
                  </div>
                  <div className="text-sm text-gray-600 font-medium">Progress</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-gradient-to-br from-green-50/30 to-transparent">
                  <div className="text-3xl font-bold text-teal-700">
                    {processHealth.score.toFixed(0)}
                    <span className="text-lg text-gray-600 ml-1">%</span>
                  </div>
                  <div className="text-sm text-gray-600 font-medium">Health Score</div>
                </div>
                <div className="text-center p-4 rounded-lg bg-gradient-to-br from-orange-50/30 to-transparent">
                  <div className="text-3xl font-bold text-teal-700">
                    {p85}
                    <span className="text-lg text-gray-600 ml-1">sprints</span>
                  </div>
                  <div className="text-sm text-gray-600 font-medium">85% Date</div>
                </div>
              </div>
              <div className="prose max-w-none text-gray-700 font-sans leading-relaxed">
                <p>
                  Based on historical velocity analysis of {sprints.length} sprints, the team has maintained
                  an average velocity of {velocityMetrics.average.toFixed(1)} story points per sprint
                  with a standard deviation of {velocityMetrics.stdDev.toFixed(1)} points.
                </p>
                <p className="mt-4">
                  Monte Carlo simulations (10,000 iterations) forecast project completion with:
                </p>
                <ul className="mt-2">
                  <li><span className="font-medium">50% confidence</span> in {p50} sprints</li>
                  <li><span className="font-medium">70% confidence</span> in {p70} sprints</li>
                  <li><span className="font-medium">85% confidence</span> in {p85} sprints</li>
                  <li><span className="font-medium">95% confidence</span> in {p95} sprints</li>
                </ul>
                <p className="mt-4">
                  The process health score of {processHealth.score.toFixed(0)}% indicates{' '}
                  <span className={`font-medium ${
                    processHealth.score >= 80 ? 'text-green-600' : 
                    processHealth.score >= 60 ? 'text-orange-600' : 'text-red-600'
                  }`}>
                    {processHealth.score >= 80 ? 'excellent' : processHealth.score >= 60 ? 'good' : 'areas for improvement in'}
                  </span>{' '}
                  team practices and workflow efficiency.
                </p>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Key Metrics */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Key Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <MetricCard
              title="Average Velocity"
              value={velocityMetrics.average.toFixed(1)}
              unit="points"
              description="Per sprint"
              trend={velocityMetrics.trend > 0 ? 'up' : velocityMetrics.trend < 0 ? 'down' : 'neutral'}
              icon={<VelocityIcon />}
              size="sm"
              highlight={true}
            />
            <MetricCard
              title="Remaining Work"
              value={remainingWork}
              unit="points"
              description="To complete"
              icon={<ProgressIcon />}
              size="sm"
            />
            <MetricCard
              title="Process Health"
              value={processHealth.score.toFixed(0)}
              unit="%"
              description="Overall score"
              trend={processHealth.score >= 70 ? 'up' : 'down'}
              icon={<HealthIcon />}
              size="sm"
            />
            <MetricCard
              title="Sprint Predictability"
              value={((velocityMetrics.stdDev / velocityMetrics.average) * 100).toFixed(0)}
              unit="%"
              description="Variance"
              trend="neutral"
              icon={<CalendarIcon />}
              size="sm"
            />
          </div>
        </section>

        {/* Velocity Analysis */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Velocity Analysis</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Chart
              title="Sprint Velocity Trend"
              data={[
                {
                  x: sprints.map(s => s.name),
                  y: sprints.map(s => s.completedPoints),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Completed',
                  line: {
                    color: chartColors.primary,
                    width: 3,
                  },
                  marker: {
                    size: 8,
                    color: chartColors.primary,
                  },
                },
                {
                  x: sprints.map(s => s.name),
                  y: sprints.map(s => s.committedPoints),
                  type: 'scatter',
                  mode: 'lines+markers',
                  name: 'Committed',
                  line: {
                    color: chartColors.secondary,
                    width: 2,
                    dash: 'dash',
                  },
                  marker: {
                    size: 6,
                    color: chartColors.secondary,
                  },
                },
              ]}
              layout={{
                height: 350,
                yaxis: {
                  title: 'Story Points',
                },
                margin: {
                  l: 50,
                  r: 20,
                  b: 50,
                  t: 40,
                },
              }}
            />
            <Card elevated>
              <CardHeader className="bg-gradient-to-r from-transparent via-teal-50/20 to-transparent">
                <CardTitle>Velocity Statistics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Average</div>
                    <div className="text-xl font-semibold text-gray-900">{velocityMetrics.average.toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Median</div>
                    <div className="text-xl font-semibold text-gray-900">{velocityMetrics.median.toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Std Dev</div>
                    <div className="text-xl font-semibold text-gray-900">{velocityMetrics.stdDev.toFixed(1)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Minimum</div>
                    <div className="text-xl font-semibold text-gray-900">{velocityMetrics.min.toFixed(0)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Maximum</div>
                    <div className="text-xl font-semibold text-gray-900">{velocityMetrics.max.toFixed(0)}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-600 font-medium">Trend</div>
                    <div className={`text-xl font-semibold ${
                      velocityMetrics.trend > 0 ? 'text-green-600' : 
                      velocityMetrics.trend < 0 ? 'text-red-600' : 'text-gray-600'
                    }`}>
                      {velocityMetrics.trend > 0 ? '+' : ''}{(velocityMetrics.trend * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* Monte Carlo Forecast */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Monte Carlo Forecast</h2>
          <Chart
            title="Completion Probability Distribution"
            data={[
              {
                x: Object.values(simulationResults.percentiles),
                y: Object.keys(simulationResults.percentiles).map(k => parseFloat(k) * 100),
                type: 'scatter',
                mode: 'lines+markers',
                name: 'Completion Probability',
                line: {
                  color: chartColors.primary,
                  width: 3,
                  shape: 'spline',
                },
                fill: 'tozeroy',
                fillcolor: 'rgba(3, 86, 76, 0.15)',
                marker: {
                  size: 8,
                  color: chartColors.primary,
                },
              },
            ]}
            layout={{
              height: 400,
              xaxis: {
                title: 'Sprints to Complete',
              },
              yaxis: {
                title: 'Confidence Level (%)',
                range: [0, 100],
              },
              margin: {
                l: 60,
                r: 20,
                b: 60,
                t: 40,
              },
            }}
          />
        </section>

        {/* Sprint Performance Details */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Sprint Performance Details</h2>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Sprint</TableHead>
                <TableHead>Committed</TableHead>
                <TableHead>Completed</TableHead>
                <TableHead>Completion %</TableHead>
                <TableHead>Variance</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {sprints.slice(-10).map((sprint, index) => {
                const completionRate = sprint.committedPoints > 0 
                  ? (sprint.completedPoints / sprint.committedPoints) * 100 
                  : 0
                const variance = sprint.completedPoints - sprint.committedPoints
                
                return (
                  <TableRow key={index}>
                    <TableCell className="font-medium">{sprint.name}</TableCell>
                    <TableCell>{sprint.committedPoints}</TableCell>
                    <TableCell>{sprint.completedPoints}</TableCell>
                    <TableCell>
                      <span className={`font-medium ${
                        completionRate >= 90 ? 'text-green-600' :
                        completionRate >= 70 ? 'text-orange-600' :
                        'text-red-600'
                      }`}>
                        {completionRate.toFixed(1)}%
                      </span>
                    </TableCell>
                    <TableCell>
                      <span className={`font-medium ${variance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {variance > 0 && '+'}{variance}
                      </span>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </section>

        {/* Process Health Breakdown */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Process Health Breakdown</h2>
          <Card elevated>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-sm text-gray-600 font-medium font-sans mb-1">Work In Progress</div>
                  <div className={`text-2xl font-bold ${
                    processHealth.wipScore >= 70 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {processHealth.wipScore.toFixed(0)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600 font-medium font-sans mb-1">Sprint Health</div>
                  <div className={`text-2xl font-bold ${
                    processHealth.sprintHealthScore >= 70 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {processHealth.sprintHealthScore.toFixed(0)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600 font-medium font-sans mb-1">Flow Efficiency</div>
                  <div className={`text-2xl font-bold ${
                    processHealth.flowEfficiencyScore >= 70 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {processHealth.flowEfficiencyScore.toFixed(0)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600 font-medium font-sans mb-1">Lead Time</div>
                  <div className={`text-2xl font-bold ${
                    processHealth.leadTimeScore >= 70 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {processHealth.leadTimeScore.toFixed(0)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600 font-medium font-sans mb-1">Defect Rate</div>
                  <div className={`text-2xl font-bold ${
                    processHealth.defectRateScore >= 70 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {processHealth.defectRateScore.toFixed(0)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-600 font-medium font-sans mb-1">Blocked Items</div>
                  <div className={`text-2xl font-bold ${
                    processHealth.blockedItemsScore >= 70 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {processHealth.blockedItemsScore.toFixed(0)}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-gray-50 to-teal-50/30 border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm text-gray-600 font-sans mb-2">
              Sprint Radar © {new Date().getFullYear()} • Agile Analytics Platform
            </p>
            <p className="text-xs text-gray-500 font-sans">
              Powered by Monte Carlo Simulations • Professional Analytics for Enterprise Teams
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}