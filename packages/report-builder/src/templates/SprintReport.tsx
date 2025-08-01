import React from 'react'
import {
  ReportTemplate,
  ReportSection,
  ExecutiveSummary,
  MetricSummary,
  MetricCard,
  MetricCardGrid,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Grid,
  ChartSSR as Chart,
  chartColors,
  chartLayouts,
} from '@sprint-radar/ui'
import { ReportData } from '../types'

// chartColors and chartLayouts are now imported from @sprint-radar/ui

interface SprintReportProps {
  data: ReportData
}

export const SprintReport: React.FC<SprintReportProps> = ({ data }) => {
  const {
    projectName,
    generatedAt,
    remainingWork,
    velocityMetrics,
    simulationResults,
    processHealth,
    sprints,
    charts,
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

  return (
    <ReportTemplate
      title={`${projectName} Sprint Performance Report`}
      subtitle="Monte Carlo Simulation Forecast"
      date={formattedDate}
      printable={true}
    >
      <ReportSection title="Executive Summary" spacing="md">
        <ExecutiveSummary
          highlights={[
            { label: 'Velocity', value: velocityMetrics.average.toFixed(1), unit: 'pts/sprint' },
            { label: 'Progress', value: completionPercentage.toFixed(1), unit: '%' },
            { label: 'Health Score', value: processHealth.score.toFixed(0), unit: '%' },
            { label: '85% Date', value: `${p85} sprints` },
          ]}
        >
          <p>
            Based on historical velocity analysis of {sprints.length} sprints, the team has maintained
            an average velocity of {velocityMetrics.average.toFixed(1)} story points per sprint
            with a standard deviation of {velocityMetrics.stdDev.toFixed(1)} points.
          </p>
          <p>
            Monte Carlo simulations (10,000 iterations) forecast project completion with:
          </p>
          <ul>
            <li>50% confidence in {p50} sprints</li>
            <li>70% confidence in {p70} sprints</li>
            <li>85% confidence in {p85} sprints</li>
            <li>95% confidence in {p95} sprints</li>
          </ul>
          <p>
            The process health score of {processHealth.score.toFixed(0)}% indicates{' '}
            {processHealth.score >= 80 ? 'excellent' : processHealth.score >= 60 ? 'good' : 'areas for improvement in'}{' '}
            team practices and workflow efficiency.
          </p>
        </ExecutiveSummary>
      </ReportSection>

      <ReportSection title="Key Metrics" spacing="md">
        <MetricCardGrid cols={4}>
          <MetricCard
            title="Average Velocity"
            value={velocityMetrics.average.toFixed(1)}
            unit="points"
            description="Per sprint"
            trend={velocityMetrics.trend > 0 ? 'up' : velocityMetrics.trend < 0 ? 'down' : 'neutral'}
            trendValue={Math.abs(velocityMetrics.trend * 100).toFixed(1)}
            trendLabel="trend"
            size="sm"
          />
          <MetricCard
            title="Remaining Work"
            value={remainingWork}
            unit="points"
            description="To complete"
            size="sm"
          />
          <MetricCard
            title="Process Health"
            value={processHealth.score.toFixed(0)}
            unit="%"
            description="Overall score"
            trend={processHealth.score >= 70 ? 'up' : 'down'}
            size="sm"
          />
          <MetricCard
            title="Sprint Predictability"
            value={((velocityMetrics.stdDev / velocityMetrics.average) * 100).toFixed(0)}
            unit="%"
            description="Variance"
            trend="neutral"
            size="sm"
          />
        </MetricCardGrid>
      </ReportSection>

      <ReportSection title="Velocity Analysis" spacing="md">
        <Grid cols={2} gap="lg">
          <Card>
            <CardContent className="p-6">
              {charts?.velocityTrend ? (
                <Chart
                  data={charts.velocityTrend.data}
                  layout={{
                    ...chartLayouts.timeSeries,
                    ...charts.velocityTrend.layout,
                    height: 350,
                  }}
                />
              ) : (
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
                        color: chartColors.primary[0],
                        width: 3,
                      },
                      marker: {
                        size: 8,
                      },
                    },
                    {
                      x: sprints.map(s => s.name),
                      y: sprints.map(s => s.committedPoints),
                      type: 'scatter',
                      mode: 'lines+markers',
                      name: 'Committed',
                      line: {
                        color: chartColors.categorical[1],
                        width: 2,
                        dash: 'dash',
                      },
                      marker: {
                        size: 6,
                      },
                    },
                  ]}
                  layout={{
                    ...chartLayouts.timeSeries,
                    height: 350,
                    yaxis: {
                      ...chartLayouts.timeSeries.yaxis,
                      title: 'Story Points',
                    },
                  }}
                />
              )}
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Velocity Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <MetricSummary
                metrics={[
                  { label: 'Average', value: velocityMetrics.average.toFixed(1) },
                  { label: 'Median', value: velocityMetrics.median.toFixed(1) },
                  { label: 'Std Dev', value: velocityMetrics.stdDev.toFixed(1) },
                  { label: 'Minimum', value: velocityMetrics.min.toFixed(0) },
                  { label: 'Maximum', value: velocityMetrics.max.toFixed(0) },
                  { 
                    label: 'Trend', 
                    value: `${velocityMetrics.trend > 0 ? '+' : ''}${(velocityMetrics.trend * 100).toFixed(1)}%`,
                    trend: velocityMetrics.trend > 0 ? 'up' : velocityMetrics.trend < 0 ? 'down' : 'neutral'
                  },
                ]}
                columns={3}
              />
            </CardContent>
          </Card>
        </Grid>
      </ReportSection>

      <ReportSection title="Monte Carlo Forecast" spacing="md">
        <Card>
          <CardContent className="p-6">
            {charts?.monteCarloForecast ? (
              <Chart
                data={charts.monteCarloForecast.data}
                layout={{
                  ...charts.monteCarloForecast.layout,
                  height: 400,
                }}
              />
            ) : (
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
                      color: chartColors.primary[0],
                      width: 3,
                    },
                    fill: 'tozeroy',
                    fillcolor: 'rgba(3, 86, 76, 0.2)',
                    marker: {
                      size: 8,
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
                }}
              />
            )}
          </CardContent>
        </Card>
      </ReportSection>

      <ReportSection title="Sprint Performance Details" spacing="md">
        <Card>
          <CardContent>
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
                      <TableCell>{completionRate.toFixed(1)}%</TableCell>
                      <TableCell>
                        <span className={variance >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {variance > 0 && '+'}{variance}
                        </span>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </ReportSection>

      <ReportSection title="Process Health Breakdown" spacing="md">
        <Card>
          <CardContent>
            <MetricSummary
              metrics={[
                { 
                  label: 'Work In Progress', 
                  value: `${processHealth.wipScore.toFixed(0)}%`,
                  trend: processHealth.wipScore >= 70 ? 'up' : 'down'
                },
                { 
                  label: 'Sprint Health', 
                  value: `${processHealth.sprintHealthScore.toFixed(0)}%`,
                  trend: processHealth.sprintHealthScore >= 70 ? 'up' : 'down'
                },
                { 
                  label: 'Flow Efficiency', 
                  value: `${processHealth.flowEfficiencyScore.toFixed(0)}%`,
                  trend: processHealth.flowEfficiencyScore >= 70 ? 'up' : 'down'
                },
                { 
                  label: 'Lead Time', 
                  value: `${processHealth.leadTimeScore.toFixed(0)}%`,
                  trend: processHealth.leadTimeScore >= 70 ? 'up' : 'down'
                },
                { 
                  label: 'Defect Rate', 
                  value: `${processHealth.defectRateScore.toFixed(0)}%`,
                  trend: processHealth.defectRateScore >= 70 ? 'up' : 'down'
                },
                { 
                  label: 'Blocked Items', 
                  value: `${processHealth.blockedItemsScore.toFixed(0)}%`,
                  trend: processHealth.blockedItemsScore >= 70 ? 'up' : 'down'
                },
              ]}
              columns={3}
            />
          </CardContent>
        </Card>
      </ReportSection>
    </ReportTemplate>
  )
}