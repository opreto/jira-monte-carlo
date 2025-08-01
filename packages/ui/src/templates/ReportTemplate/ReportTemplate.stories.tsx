import type { Meta, StoryObj } from '@storybook/react'
import {
  ReportTemplate,
  ReportSection,
  ExecutiveSummary,
  MetricSummary,
} from './ReportTemplate'
import { MetricCard, MetricCardGrid } from '../../components/MetricCard'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/Table'
import { Chart, chartColors } from '../../components/Chart'
import { Card, CardContent, CardHeader, CardTitle } from '../../components/Card'
import { Grid } from '../../components/Layout'

const meta = {
  title: 'Templates/ReportTemplate',
  component: ReportTemplate,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof ReportTemplate>

export default meta
type Story = StoryObj<typeof meta>

export const BasicReport: Story = {
  args: {
    title: 'Sprint 42 Performance Report',
    subtitle: 'Team Alpha - Q1 2025',
    children: (
      <>
        <ReportSection title="Executive Summary">
          <ExecutiveSummary
            highlights={[
              { label: 'Sprint Velocity', value: 42, unit: 'points' },
              { label: 'Completion Rate', value: 93.3, unit: '%' },
              { label: 'Cycle Time', value: 2.8, unit: 'days' },
              { label: 'Quality Score', value: 'A+' },
            ]}
          >
            <p>
              Sprint 42 demonstrated strong performance with a 93.3% completion rate, 
              delivering 42 out of 45 committed story points. The team maintained 
              consistency with the 6-sprint average velocity of 42.5 points while 
              achieving the lowest bug rate in the past quarter.
            </p>
            <p>
              Key achievements include successful delivery of all critical features, 
              maintaining sub-3-day cycle times, and zero critical bugs in production. 
              The team's collaborative efforts resulted in improved code review 
              turnaround times and enhanced test coverage.
            </p>
          </ExecutiveSummary>
        </ReportSection>

        <ReportSection title="Key Metrics">
          <MetricSummary
            metrics={[
              { label: 'Stories Completed', value: '15 of 18', trend: 'neutral' },
              { label: 'Bug Rate', value: '0.12 per story', change: -25, trend: 'down' },
              { label: 'Team Capacity', value: '85%', change: 0, trend: 'neutral' },
              { label: 'PR Reviews', value: 156, change: 18, trend: 'up' },
              { label: 'Test Coverage', value: '87%', change: 3, trend: 'up' },
              { label: 'Deploy Frequency', value: '2.3 per day', change: 15, trend: 'up' },
            ]}
            columns={3}
          />
        </ReportSection>
      </>
    ),
  },
}

export const ComprehensiveReport: Story = {
  render: () => (
    <ReportTemplate
      title="Q1 2025 Sprint Performance Analysis"
      subtitle="Comprehensive Team Performance and Forecasting Report"
    >
      <ReportSection title="Executive Summary" spacing="md">
        <ExecutiveSummary
          highlights={[
            { label: 'Avg Velocity', value: 43.2, unit: 'points' },
            { label: 'Predictability', value: 94.5, unit: '%' },
            { label: 'Forecast Date', value: 'Apr 12' },
          ]}
        >
          <p>
            The Q1 2025 sprint performance analysis reveals consistent team velocity 
            with an average of 43.2 story points per sprint, representing a 7% 
            improvement over Q4 2024. Team predictability has reached 94.5%, 
            indicating mature estimation practices and stable delivery patterns.
          </p>
          <p>
            Based on current velocity trends and Monte Carlo simulations, the project 
            is forecasted to complete by April 12, 2025, with 85% confidence. This 
            represents a two-week improvement from the original baseline estimate.
          </p>
        </ExecutiveSummary>
      </ReportSection>

      <ReportSection title="Sprint Velocity Trends" spacing="md">
        <Card>
          <CardContent className="p-6">
            <Chart
              title="6-Sprint Velocity Trend"
              data={[
                {
                  x: ['Sprint 37', 'Sprint 38', 'Sprint 39', 'Sprint 40', 'Sprint 41', 'Sprint 42'],
                  y: [46, 40, 44, 35, 48, 42],
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
                  x: ['Sprint 37', 'Sprint 38', 'Sprint 39', 'Sprint 40', 'Sprint 41', 'Sprint 42'],
                  y: [48, 42, 45, 40, 50, 45],
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
                height: 400,
                yaxis: {
                  title: 'Story Points',
                },
              }}
            />
          </CardContent>
        </Card>
      </ReportSection>

      <ReportSection title="Team Performance Metrics" spacing="md">
        <MetricCardGrid cols={4}>
          <MetricCard
            title="Sprint Velocity"
            value={42}
            unit="points"
            trend="up"
            trendValue={5}
            trendLabel="vs average"
            size="sm"
          />
          <MetricCard
            title="Completion Rate"
            value="93.3"
            unit="%"
            trend="up"
            trendValue={2.3}
            trendLabel="vs last sprint"
            size="sm"
          />
          <MetricCard
            title="Cycle Time"
            value={2.8}
            unit="days"
            trend="down"
            trendValue={-12}
            trendLabel="improvement"
            size="sm"
          />
          <MetricCard
            title="Bug Rate"
            value={0.12}
            unit="per story"
            trend="down"
            trendValue={-25}
            trendLabel="reduction"
            size="sm"
          />
        </MetricCardGrid>
      </ReportSection>

      <ReportSection title="Sprint Details" spacing="md">
        <Card>
          <CardHeader>
            <CardTitle>Sprint Performance by Team Member</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Team Member</TableHead>
                  <TableHead>Stories Completed</TableHead>
                  <TableHead>Points Delivered</TableHead>
                  <TableHead>Avg Cycle Time</TableHead>
                  <TableHead>Quality Score</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                <TableRow>
                  <TableCell className="font-medium">Sarah Chen</TableCell>
                  <TableCell>8</TableCell>
                  <TableCell>21</TableCell>
                  <TableCell>2.3 days</TableCell>
                  <TableCell>A+</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Mike Johnson</TableCell>
                  <TableCell>6</TableCell>
                  <TableCell>13</TableCell>
                  <TableCell>3.1 days</TableCell>
                  <TableCell>A</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">Emily Davis</TableCell>
                  <TableCell>5</TableCell>
                  <TableCell>18</TableCell>
                  <TableCell>2.8 days</TableCell>
                  <TableCell>A+</TableCell>
                </TableRow>
                <TableRow>
                  <TableCell className="font-medium">David Kim</TableCell>
                  <TableCell>4</TableCell>
                  <TableCell>8</TableCell>
                  <TableCell>4.2 days</TableCell>
                  <TableCell>B+</TableCell>
                </TableRow>
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </ReportSection>

      <ReportSection title="Forecasting & Risk Analysis" spacing="md">
        <Grid cols={2} gap="lg">
          <Card>
            <CardContent className="p-6">
              <Chart
                title="Monte Carlo Completion Forecast"
                data={[
                  {
                    x: Array.from({ length: 100 }, (_, i) => new Date(2025, 2, 1 + i)),
                    y: Array.from({ length: 100 }, (_, i) => {
                      const base = 1 / (1 + Math.exp(-(i - 50) / 10))
                      return base + (Math.random() - 0.5) * 0.1
                    }),
                    type: 'scatter',
                    mode: 'lines',
                    name: 'Completion Probability',
                    line: {
                      color: chartColors.primary[0],
                      width: 3,
                    },
                    fill: 'tozeroy',
                    fillcolor: 'rgba(3, 86, 76, 0.2)',
                  },
                ]}
                layout={{
                  height: 300,
                  yaxis: {
                    title: 'Probability',
                    tickformat: '.0%',
                  },
                  xaxis: {
                    title: 'Date',
                  },
                }}
              />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Risk Assessment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium text-red-600">High Risk Items</h4>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                    <li>Technical debt in authentication module</li>
                    <li>Dependency on external API availability</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-yellow-600">Medium Risk Items</h4>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                    <li>Team member vacation schedule in April</li>
                    <li>Upcoming framework migration</li>
                    <li>Performance optimization requirements</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-green-600">Mitigation Strategies</h4>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                    <li>Allocate 20% capacity for tech debt</li>
                    <li>Implement circuit breaker for API calls</li>
                    <li>Cross-training for critical components</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </Grid>
      </ReportSection>
    </ReportTemplate>
  ),
}

export const MinimalReport: Story = {
  render: () => (
    <ReportTemplate
      title="Weekly Status Report"
      subtitle="Week of January 27, 2025"
      printable={false}
    >
      <ReportSection>
        <MetricSummary
          metrics={[
            { label: 'Stories In Progress', value: 12 },
            { label: 'Stories Completed', value: 8 },
            { label: 'Blockers', value: 2 },
            { label: 'Team Velocity', value: '85%' },
          ]}
          columns={4}
        />
      </ReportSection>

      <ReportSection>
        <Card>
          <CardHeader>
            <CardTitle>This Week's Highlights</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-inside list-disc space-y-2">
              <li>Completed user authentication feature ahead of schedule</li>
              <li>Resolved critical performance issue in data processing pipeline</li>
              <li>Onboarded new team member successfully</li>
              <li>Achieved 95% test coverage on new features</li>
            </ul>
          </CardContent>
        </Card>
      </ReportSection>
    </ReportTemplate>
  ),
}

export const CustomHeaderReport: Story = {
  render: () => (
    <ReportTemplate
      title="Custom Analytics Report"
      logo={
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded bg-[#03564c]" />
          <span className="font-semibold">My Company</span>
        </div>
      }
      headerActions={
        <div className="flex gap-2">
          <button className="text-sm text-gray-600 hover:text-gray-900">
            Share
          </button>
          <button className="text-sm text-gray-600 hover:text-gray-900">
            Download
          </button>
          <button className="text-sm text-gray-600 hover:text-gray-900">
            Settings
          </button>
        </div>
      }
      footerContent={
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Confidential - Internal Use Only</span>
          <span>Page 1 of 1</span>
        </div>
      }
    >
      <ReportSection title="Custom Content">
        <p className="text-gray-600">
          This demonstrates a report with custom header and footer content.
        </p>
      </ReportSection>
    </ReportTemplate>
  ),
}