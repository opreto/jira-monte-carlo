import React from 'react'
import { ReportData } from '../types'
import { 
  fontStyles, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  Table, 
  TableHeader, 
  TableBody, 
  TableRow, 
  TableHead, 
  TableCell,
  MLTooltip,
  InfoTooltip,
  ChartDescription,
  Chart,
  Header,
  MetricCard,
  Icons,
  colors
} from '../components/DesignSystem'


// Process Health Component
const ProcessHealthBreakdown = ({ healthMetrics }: { healthMetrics: any }) => {
  if (!healthMetrics.health_score_breakdown || healthMetrics.health_score_breakdown.length === 0) {
    return (
      <div className="bg-orange-50 rounded-lg p-4 mb-4">
        <p className="text-orange-800 font-sans">
          <strong>Limited Health Data:</strong> Additional metrics require more complete data fields 
          (created dates, labels, etc.) to provide detailed insights.
        </p>
      </div>
    )
  }

  // Sort components to render ones without detail_items first to avoid SSR truncation issues
  const sortedComponents = [...healthMetrics.health_score_breakdown].sort((a, b) => {
    const aHasDetails = a.detail_items && a.detail_items.length > 0;
    const bHasDetails = b.detail_items && b.detail_items.length > 0;
    if (aHasDetails && !bHasDetails) return 1;
    if (!aHasDetails && bHasDetails) return -1;
    return 0;
  });

  return (
    <div className="mt-6">
      <h3 className="text-xl font-display text-gray-900 mb-4">Score Breakdown & Insights</h3>
      {sortedComponents.map((component: any, index: number) => {
        try {
          return (
            <Card key={index} className="mb-4">
              <CardContent>
                <div className="flex justify-between items-center mb-3">
                  <h4 className="text-lg font-semibold font-sans text-gray-900">{component.name || 'Unknown'}</h4>
                  <span className={`text-2xl font-bold ${
                    component.score >= 0.8 ? 'text-green-600' :
                    component.score >= 0.6 ? 'text-orange-600' :
                    'text-red-600'
                  }`}>
                    {Math.round((component.score || 0) * 100)}%
                  </span>
                </div>
                <p className="text-gray-600 text-sm font-sans mb-3">{component.description || ''}</p>
                
                {component.insights && component.insights.length > 0 && (
              <div className="mb-3">
                <strong className="text-sm font-sans text-gray-800">Current State:</strong>
                <ul className="mt-1 space-y-1">
                  {component.insights.map((insight: string, i: number) => (
                    <li key={i} className="text-sm text-gray-600 font-sans flex items-start">
                      <span className="text-teal-500 mr-2">•</span>
                      {insight}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {component.recommendations && component.recommendations.length > 0 && (
              <div className="mb-3">
                <strong className="text-sm font-sans text-gray-800">Recommendations:</strong>
                <ul className="mt-1 space-y-1">
                  {component.recommendations.map((rec: string, i: number) => (
                    <li key={i} className="text-sm text-gray-700 font-sans italic flex items-start">
                      <span className="text-teal-500 mr-2">→</span>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {component.detail_items && component.detail_items.length > 0 && (
              <details className="mt-3">
                <summary className="cursor-pointer text-sm text-teal-600 font-medium font-sans hover:text-teal-700">
                  View {component.detail_items.length > 10 ? `first 10 of ${component.detail_items.length}` : component.detail_items.length} affected items ▶
                </summary>
                <div className="mt-3 max-h-64 overflow-y-auto">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Key</TableHead>
                        <TableHead>Summary</TableHead>
                        <TableHead>Age</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Assignee</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {/* Limit to first 10 items to prevent SSR issues */}
                      {component.detail_items.slice(0, 10).map((item: any, i: number) => (
                        <TableRow key={i}>
                          <TableCell>
                            <span className="text-teal-600 font-medium">{item.key}</span>
                          </TableCell>
                          <TableCell>
                            {item.summary.length > 50 ? item.summary.substring(0, 50) + '...' : item.summary}
                          </TableCell>
                          <TableCell>{item.age_days} days</TableCell>
                          <TableCell>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              item.type === 'abandoned' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
                            }`}>
                              {item.status}
                            </span>
                          </TableCell>
                          <TableCell>{item.assignee}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {component.detail_items.length > 10 && (
                    <p className="text-sm text-gray-600 mt-2 text-center italic">
                      Showing first 10 of {component.detail_items.length} items
                    </p>
                  )}
                </div>
              </details>
            )}
              </CardContent>
            </Card>
          )
        } catch (error) {
          console.error(`Error rendering component ${index}:`, error)
          return (
            <Card key={index} className="mb-4 border-red-200">
              <CardContent>
                <div className="text-red-600">
                  <h4 className="text-lg font-semibold">{component?.name || `Component ${index}`}</h4>
                  <p className="text-sm">Error rendering this component</p>
                </div>
              </CardContent>
            </Card>
          )
        }
      })}
    </div>
  )
}


interface SprintReportProps {
  data: ReportData
}

export const EnhancedSprintReport: React.FC<SprintReportProps> = ({ data }) => {
  const {
    projectName,
    generatedAt,
    remainingWork,
    velocityMetrics,
    simulationResults,
    processHealth,
    sprints,
    jql_query,
    velocity_field,
    model_info,
    num_simulations,
    reporting_capabilities,
    charts,
    summary_stats,
    combinedScenarioData,
    scenarioBanner,
    ml_decisions,
    scenarioCharts,
  } = data
  
  // State for scenario switching
  const [currentScenario, setCurrentScenario] = React.useState(
    combinedScenarioData?.current_view || 'baseline'
  )
  
  // Use scenario data if available
  const activeScenarioData = currentScenario === 'baseline' 
    ? combinedScenarioData?.baseline 
    : currentScenario === 'adjusted' 
    ? combinedScenarioData?.adjusted 
    : null
    
  const displaySimulationResults = activeScenarioData && activeScenarioData.percentiles ? {
    percentiles: {
      '0.5': activeScenarioData.percentiles.p50,
      '0.7': activeScenarioData.percentiles.p70,
      '0.85': activeScenarioData.percentiles.p85,
      '0.95': activeScenarioData.percentiles.p95,
    }
  } : simulationResults

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
  const p50 = displaySimulationResults.percentiles['0.5'] || 0
  const p70 = displaySimulationResults.percentiles['0.7'] || 0
  const p85 = displaySimulationResults.percentiles['0.85'] || 0
  const p95 = displaySimulationResults.percentiles['0.95'] || 0

  return (
    <div className="min-h-screen bg-gray-50">
      <style dangerouslySetInnerHTML={{ __html: fontStyles }} />
      
      {/* Sticky Scenario Panel */}
      {combinedScenarioData && (
        <div className="sticky top-0 z-50 bg-white shadow-lg border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <h3 className="text-lg font-semibold font-sans text-gray-900 flex items-center">
                  <span className="mr-2">{Icons.chart}</span>
                  Velocity Scenario Analysis
                </h3>
                <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1" id="scenario-switcher">
                  <button
                    data-scenario="baseline"
                    className={`scenario-btn px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                      currentScenario === 'baseline'
                        ? 'bg-white text-teal-700 shadow-sm active'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Baseline
                  </button>
                  <button
                    data-scenario="adjusted"
                    className={`scenario-btn px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                      currentScenario === 'adjusted'
                        ? 'bg-white text-teal-700 shadow-sm active'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    Adjusted
                  </button>
                </div>
              </div>
              
              <div className="text-sm text-gray-600">
                <div className="scenario-description" data-scenario="adjusted" style={{ display: currentScenario === 'adjusted' ? 'block' : 'none' }}>
                  <span className="font-medium">Scenario:</span> {combinedScenarioData.scenario.description}
                  <br />
                  <span className="font-medium">Impact:</span> {combinedScenarioData.scenario.comparison}
                </div>
                <div className="scenario-description" data-scenario="baseline" style={{ display: currentScenario === 'baseline' ? 'block' : 'none' }}>
                  <span className="text-gray-500">Baseline forecast without velocity adjustments</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      <Header>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
          <h1 className="text-4xl md:text-5xl font-display text-white mb-2">
            {model_info?.report_title || 'Sprint Radar Analytics'}: {projectName}
          </h1>
          <p className="text-lg text-teal-100">
            {model_info?.report_subtitle || 'Monte Carlo Simulation Forecast'} • Generated on {formattedDate}
          </p>
        </div>
      </Header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* JQL Query Display */}
        {(jql_query || data.jql_queries) && (
          <section className="mb-8">
            <Card>
              <CardHeader>
                <CardTitle>Data Selection Queries</CardTitle>
              </CardHeader>
              <CardContent>
                {data.jql_queries?.forecast && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Forecast Query (Backlog Items):</h4>
                    <pre className="bg-gray-50 p-3 rounded-lg overflow-x-auto">
                      <code className="text-sm font-mono text-gray-800">{data.jql_queries.forecast}</code>
                    </pre>
                  </div>
                )}
                {data.jql_queries?.history && (
                  <div className="mb-4">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">History Query (Velocity Calculation):</h4>
                    <pre className="bg-gray-50 p-3 rounded-lg overflow-x-auto">
                      <code className="text-sm font-mono text-gray-800">{data.jql_queries.history}</code>
                    </pre>
                  </div>
                )}
                {!data.jql_queries && jql_query && (
                  <pre className="bg-gray-50 p-4 rounded-lg overflow-x-auto">
                    <code className="text-sm font-mono text-gray-800">{jql_query}</code>
                  </pre>
                )}
              </CardContent>
            </Card>
          </section>
        )}

        {/* Key Metrics */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Key Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <MetricCard
              title="Remaining Work"
              value={remainingWork.toFixed(1)}
              unit={velocity_field || "points"}
              tooltip="Total amount of work remaining in the backlog based on story point estimates"
              size="sm"
            />
            <MetricCard
              title="Average Velocity"
              value={velocityMetrics.average.toFixed(1)}
              unit="per sprint"
              tooltip="Average story points completed per sprint, calculated from historical data"
              trend={velocityMetrics.trend > 0 ? 'up' : velocityMetrics.trend < 0 ? 'down' : 'neutral'}
              size="sm"
              highlight={true}
            />
            <div className="metric-card-wrapper">
              <MetricCard
                title="50% Confidence"
                value={<span 
                  className="scenario-value"
                  data-baseline-value={combinedScenarioData?.baseline?.percentiles?.p50 || p50}
                  data-adjusted-value={combinedScenarioData?.adjusted?.percentiles?.p50 || p50}
                >{p50}</span>}
                unit="sprints"
                tooltip="50% probability of completing all work within this many sprints"
                size="sm"
              />
            </div>
            <div className="metric-card-wrapper">
              <MetricCard
                title="70% Confidence"
                value={<span 
                  className="scenario-value"
                  data-baseline-value={combinedScenarioData?.baseline?.percentiles?.p70 || p70}
                  data-adjusted-value={combinedScenarioData?.adjusted?.percentiles?.p70 || p70}
                >{p70}</span>}
                unit="sprints"
                tooltip="70% probability of completing all work within this many sprints"
                size="sm"
              />
            </div>
            <div className="metric-card-wrapper">
              <MetricCard
                title="85% Confidence"
                value={<span 
                  className="scenario-value"
                  data-baseline-value={combinedScenarioData?.baseline?.percentiles?.p85 || p85}
                  data-adjusted-value={combinedScenarioData?.adjusted?.percentiles?.p85 || p85}
                >{p85}</span>}
                unit="sprints"
                tooltip="85% probability of completing all work within this many sprints (recommended for commitments)"
                size="sm"
              />
            </div>
            <div className="metric-card-wrapper">
              <MetricCard
                title="95% Confidence"
                value={<span 
                  className="scenario-value"
                  data-baseline-value={combinedScenarioData?.baseline?.percentiles?.p95 || p95}
                  data-adjusted-value={combinedScenarioData?.adjusted?.percentiles?.p95 || p95}
                >{p95}</span>}
                unit="sprints"
                tooltip="95% probability of completing all work within this many sprints (conservative estimate)"
                size="sm"
              />
            </div>
          </div>
        </section>

        {/* Probability Distribution Chart */}
        {charts?.probability_distribution && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Probability Distribution</h2>
            <Chart
              data={charts.probability_distribution.data}
              layout={charts.probability_distribution.layout}
              chartType="probability_distribution"
              description="The likelihood of completing work in different numbers of sprints."
              importance="Helps set realistic expectations and manage stakeholder commitments."
              lookFor="The shape of the distribution (narrow = predictable, wide = uncertain) and where your target date falls on the curve."
            />
          </section>
        )}

        {/* Forecast Timeline */}
        {charts?.forecast_timeline && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Forecast Timeline</h2>
            <Chart
              data={charts.forecast_timeline.data}
              layout={charts.forecast_timeline.layout}
              chartType="forecast_timeline"
              description="Projected completion dates with different confidence levels."
              importance="Visualizes the range of possible outcomes and risk levels."
              lookFor="The spread between optimistic (50%) and conservative (95%) estimates indicates project uncertainty."
            />
          </section>
        )}

        {/* Velocity Trend */}
        {charts?.velocity_trend && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Historical Velocity Trend</h2>
            <Card elevated>
              <CardContent className="relative overflow-visible">
                {ml_decisions?.decisions?.find(d => d.decision_type === 'lookback_period') && (
                  <div className="absolute top-4 right-4 z-20">
                    <MLTooltip content={
                      <div>
                        <div className="font-semibold mb-2">ML Model: {ml_decisions.decisions.find(d => d.decision_type === 'lookback_period').model_name}</div>
                        <div className="mb-2"><strong>Decision:</strong> Using {ml_decisions.decisions.find(d => d.decision_type === 'lookback_period').value} sprints lookback</div>
                        {ml_decisions.decisions.find(d => d.decision_type === 'lookback_period').confidence && (
                          <div><strong>Confidence:</strong> {(ml_decisions.decisions.find(d => d.decision_type === 'lookback_period').confidence * 100).toFixed(0)}%</div>
                        )}
                      </div>
                    }>
                      <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center cursor-help hover:bg-purple-200 transition-colors">
                        {Icons.mlInsight}
                      </div>
                    </MLTooltip>
                  </div>
                )}
                <Chart
                  data={charts.velocity_trend.data}
                  layout={charts.velocity_trend.layout}
                  description="Team velocity over recent sprints with trend line."
                  importance="Reveals if team performance is improving, declining, or stable."
                  lookFor="Consistency (low variance = predictable), trend direction, and any outliers that might skew forecasts."
                />
              </CardContent>
            </Card>
          </section>
        )}

        {/* Confidence Intervals */}
        {charts?.confidence_intervals && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Confidence Intervals</h2>
            <Chart
              data={charts.confidence_intervals.data}
              layout={charts.confidence_intervals.layout}
              chartType="confidence_intervals"
              description="Different confidence levels for project completion based on Monte Carlo simulation."
              importance="Higher confidence levels provide more buffer for uncertainty and risk."
              lookFor="Width of intervals (narrow = more certain) and which confidence level aligns with your risk tolerance."
            />
          </section>
        )}

        {/* Aging Work Items */}
        {charts?.aging_distribution && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Aging Work Items</h2>
            <Chart
              data={charts.aging_distribution.data}
              layout={charts.aging_distribution.layout}
              description="Distribution of work items by age category."
              importance="Identifies stuck or abandoned work that needs attention."
              lookFor="High numbers in the 'Stale' or 'Abandoned' categories indicate process bottlenecks."
            />
          </section>
        )}

        {/* Average Age by Status */}
        {charts?.aging_by_status && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Average Age by Status</h2>
            <Chart
              data={charts.aging_by_status.data}
              layout={charts.aging_by_status.layout}
              description="Average time items spend in each status."
              importance="Reveals workflow bottlenecks and process inefficiencies."
              lookFor="Statuses with unusually high average ages that may need process improvements."
            />
          </section>
        )}

        {/* Work In Progress by Status */}
        {charts?.wip_by_status && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Work In Progress by Status</h2>
            <Chart
              data={charts.wip_by_status.data}
              layout={charts.wip_by_status.layout}
              description="Current work items in each workflow status."
              importance="Helps identify WIP limit violations and workflow imbalances."
              lookFor="Status columns exceeding WIP limits (shown as dashed lines) indicate bottlenecks."
            />
          </section>
        )}

        {/* Sprint Completion Trend */}
        {charts?.sprint_completion_trend && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Sprint Completion Trend</h2>
            <Card elevated>
              <CardContent className="relative overflow-visible">
                <div className="absolute top-4 right-4 z-20">
                  <MLTooltip content={
                    ml_decisions?.decisions?.find(d => d.decision_type === 'sprint_health_lookback') ? (
                      <div>
                        <div className="font-semibold mb-2">ML Model: {ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').model_name}</div>
                        <div className="mb-2"><strong>Decision:</strong> Using {ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').value} sprints lookback</div>
                        {ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').confidence && (
                          <div><strong>Confidence:</strong> {(ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').confidence * 100).toFixed(0)}%</div>
                        )}
                      </div>
                    ) : (
                      "ML Analysis: Sprint completion trends are analyzed using pattern recognition to identify systemic issues. Consistent under-delivery may indicate overcommitment, while high variance suggests estimation problems."
                    )
                  }>
                    <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center cursor-help hover:bg-purple-200 transition-colors">
                      {Icons.mlInsight}
                    </div>
                  </MLTooltip>
                </div>
                <Chart
                  data={charts.sprint_completion_trend.data}
                  layout={charts.sprint_completion_trend.layout}
                  description="Historical sprint completion rates showing team delivery consistency."
                  importance="Reveals team's ability to meet commitments and estimation accuracy."
                  lookFor="Trends below average or high variance indicate planning or execution issues."
                />
              </CardContent>
            </Card>
          </section>
        )}

        {/* Sprint Scope Changes */}
        {charts?.sprint_scope_changes && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Sprint Scope Changes</h2>
            <Card elevated>
              <CardContent className="relative overflow-visible">
                <div className="absolute top-4 right-4 z-20">
                  <MLTooltip content={
                    ml_decisions?.decisions?.find(d => d.decision_type === 'sprint_health_lookback') ? (
                      <div>
                        <div className="font-semibold mb-2">ML Model: {ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').model_name}</div>
                        <div className="mb-2"><strong>Decision:</strong> Using {ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').value} sprints lookback</div>
                        {ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').confidence && (
                          <div><strong>Confidence:</strong> {(ml_decisions.decisions.find(d => d.decision_type === 'sprint_health_lookback').confidence * 100).toFixed(0)}%</div>
                        )}
                      </div>
                    ) : (
                      "ML Analysis: Scope changes are tracked to identify patterns. Frequent mid-sprint additions suggest poor planning or external pressures. The trend line shows if scope management is improving or deteriorating."
                    )
                  }>
                    <div className="w-6 h-6 bg-purple-100 rounded-full flex items-center justify-center cursor-help hover:bg-purple-200 transition-colors">
                      {Icons.mlInsight}
                    </div>
                  </MLTooltip>
                </div>
                <Chart
                  data={charts.sprint_scope_changes.data}
                  layout={charts.sprint_scope_changes.layout}
                  description="Story points added or removed during sprints after commitment."
                  importance="Indicates planning quality and requirements stability."
                  lookFor="Large or frequent scope changes suggest planning or stakeholder management issues."
                />
              </CardContent>
            </Card>
          </section>
        )}

        {/* Process Health Score */}
        <section className="mb-10">
          <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Process Health Score</h2>
          <Card elevated>
            <CardContent>
              <div className="text-center mb-6">
                <div className={`text-6xl font-bold ${
                  processHealth.score >= 80 ? 'text-green-600' :
                  processHealth.score >= 60 ? 'text-orange-600' :
                  'text-red-600'
                }`}>
                  {processHealth.score.toFixed(0)}%
                </div>
                <div className="text-gray-600 mt-2">Overall Health</div>
              </div>
              
              {charts?.health_score_gauge && (
                <div className="mb-6">
                  <Chart
                    data={charts.health_score_gauge.data}
                    layout={charts.health_score_gauge.layout}
                  />
                </div>
              )}

              {/* Health Score Bar Chart */}
              {processHealth.health_score_breakdown && processHealth.health_score_breakdown.length > 0 && (
                <div className="mb-6">
                  <Chart
                    data={[{
                      type: 'bar',
                      orientation: 'h',
                      y: processHealth.health_score_breakdown.map((comp: any) => comp.name).reverse(),
                      x: processHealth.health_score_breakdown.map((comp: any) => Math.round(comp.score * 100)).reverse(),
                      text: processHealth.health_score_breakdown.map((comp: any) => `${Math.round(comp.score * 100)}%`).reverse(),
                      textposition: 'outside',
                      marker: {
                        color: processHealth.health_score_breakdown.map((comp: any) => 
                          comp.score >= 0.8 ? '#00A86B' : 
                          comp.score >= 0.6 ? '#FFA500' : 
                          '#DC143C'
                        ).reverse()
                      }
                    }]}
                    layout={{
                      title: 'Health Score Components',
                      xaxis: {
                        title: 'Score (%)',
                        range: [0, 110],
                        showgrid: true,
                        gridcolor: 'rgba(229, 231, 235, 0.5)'
                      },
                      yaxis: {
                        title: '',
                        automargin: true
                      },
                      margin: { l: 150, r: 50, t: 50, b: 50 },
                      height: 300,
                      bargap: 0.3
                    }}
                  />
                </div>
              )}

              {/* Process Health Breakdown */}
              <ProcessHealthBreakdown healthMetrics={processHealth} />
            </CardContent>
          </Card>
        </section>

        {/* Completion Forecast Summary */}
        {summary_stats && Object.keys(summary_stats).length > 0 && (
          <section className="mb-10">
            <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">Completion Forecast Summary</h2>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Confidence Level</TableHead>
                  <TableHead>Sprints to Complete</TableHead>
                  <TableHead>Completion Date</TableHead>
                  <TableHead>Probability</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(summary_stats).map(([level, data]: [string, any]) => (
                  <TableRow key={level} className={data.class}>
                    <TableCell className="font-medium">{level}</TableCell>
                    <TableCell>{data.sprints} sprints</TableCell>
                    <TableCell>{data.date}</TableCell>
                    <TableCell>{data.probability}% chance of completing by this date</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </section>
        )}

      </main>

      {/* Footer */}
      <footer className="bg-gradient-to-r from-gray-50 to-teal-50/30 border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <p className="text-sm text-gray-600 font-sans mb-2">
              Sprint Radar © {new Date().getFullYear()} • Agile Analytics Platform by Opreto
              {reporting_capabilities && (
                <span className="ml-2">
                  • 
                  <MLTooltip content={
                    <div>
                      <div className="font-semibold mb-2">Data Quality Analysis</div>
                      <div className="mb-2">
                        <span className="font-medium">Quality Score:</span> {(reporting_capabilities.data_quality_score * 100).toFixed(0)}%
                      </div>
                      <div className="mb-2">
                        <span className="font-medium">Available Reports:</span> {reporting_capabilities.available_reports.length}
                      </div>
                      {reporting_capabilities.unavailable_reports && Object.keys(reporting_capabilities.unavailable_reports).length > 0 && (
                        <div>
                          <div className="font-medium mb-1">Unavailable Reports ({Object.keys(reporting_capabilities.unavailable_reports).length}):</div>
                          {Object.entries(reporting_capabilities.unavailable_reports).map(([report, fields]: [string, any]) => (
                            <div key={report} className="text-xs ml-2">
                              • {report}: Missing {fields.join(', ')}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  }>
                    <span className="text-teal-600 cursor-help ml-1">Data Quality: {(reporting_capabilities.data_quality_score * 100).toFixed(0)}%</span>
                  </MLTooltip>
                </span>
              )}
            </p>
            {model_info?.methodology_description && (
              <p className="text-xs text-gray-500 font-sans">{model_info.methodology_description}</p>
            )}
            {num_simulations && (
              <p className="text-xs text-gray-500 font-sans">
                Based on {num_simulations.toLocaleString()} iterations • Analysis of historical data and velocity metrics
              </p>
            )}
          </div>
        </div>
      </footer>
    </div>
  )
}