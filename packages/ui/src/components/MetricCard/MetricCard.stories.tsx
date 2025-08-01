import type { Meta, StoryObj } from '@storybook/react'
import { MetricCard, MetricCardGrid } from './MetricCard'

const meta = {
  title: 'Components/MetricCard',
  component: MetricCard,
  tags: ['autodocs'],
  args: {
    title: 'Sprint Velocity',
    value: 42,
    unit: 'points',
  },
} satisfies Meta<typeof MetricCard>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {}

export const WithDescription: Story = {
  args: {
    title: 'Sprint Velocity',
    value: 42,
    unit: 'points',
    description: 'Average over last 6 sprints',
  },
}

export const WithPositiveTrend: Story = {
  args: {
    title: 'Completion Rate',
    value: '93.3',
    unit: '%',
    trend: 'up',
    trendValue: 5.2,
    trendLabel: 'vs last sprint',
  },
}

export const WithNegativeTrend: Story = {
  args: {
    title: 'Bug Rate',
    value: 0.23,
    unit: 'per story',
    trend: 'down',
    trendValue: -15,
    trendLabel: 'improvement',
  },
}

export const WithNeutralTrend: Story = {
  args: {
    title: 'Team Capacity',
    value: 85,
    unit: '%',
    trend: 'neutral',
    trendValue: 0,
    trendLabel: 'no change',
  },
}

export const SmallSize: Story = {
  args: {
    title: 'Stories Completed',
    value: 8,
    size: 'sm',
    trend: 'up',
    trendValue: 2,
  },
}

export const LargeSize: Story = {
  args: {
    title: 'Project Progress',
    value: 68,
    unit: '%',
    size: 'lg',
    description: 'Based on Monte Carlo simulation',
    trend: 'up',
    trendValue: 12,
    trendLabel: 'this month',
  },
}

export const WithIcon: Story = {
  args: {
    title: 'Active Sprints',
    value: 3,
    icon: (
      <svg
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    ),
  },
}

export const WithFooter: Story = {
  args: {
    title: 'Forecast Confidence',
    value: '85',
    unit: '%',
    footer: (
      <div className="mt-3 border-t pt-3">
        <p className="text-xs text-gray-600">
          Project completion by April 12, 2025
        </p>
      </div>
    ),
  },
}

export const MetricCardGridExample: Story = {
  render: () => (
    <MetricCardGrid cols={3}>
      <MetricCard
        title="Sprint Velocity"
        value={42}
        unit="points"
        trend="up"
        trendValue={5}
        trendLabel="vs average"
      />
      <MetricCard
        title="Completion Rate"
        value="93.3"
        unit="%"
        trend="up"
        trendValue={2.3}
        trendLabel="vs last sprint"
      />
      <MetricCard
        title="Cycle Time"
        value={2.8}
        unit="days"
        trend="down"
        trendValue={-12}
        trendLabel="improvement"
      />
      <MetricCard
        title="Bug Rate"
        value={0.12}
        unit="per story"
        trend="down"
        trendValue={-25}
        trendLabel="reduction"
      />
      <MetricCard
        title="Team Capacity"
        value={85}
        unit="%"
        trend="neutral"
        trendValue={0}
        trendLabel="stable"
      />
      <MetricCard
        title="PR Reviews"
        value={156}
        trend="up"
        trendValue={18}
        trendLabel="this sprint"
      />
    </MetricCardGrid>
  ),
}

export const DashboardMetrics: Story = {
  render: () => (
    <div className="space-y-6">
      <div>
        <h3 className="mb-4 text-lg font-semibold">Key Performance Indicators</h3>
        <MetricCardGrid cols={4}>
          <MetricCard
            title="Sprint Progress"
            value={78}
            unit="%"
            trend="up"
            trendValue={12}
            description="Day 8 of 10"
            size="sm"
          />
          <MetricCard
            title="Stories Done"
            value="15/18"
            trend="neutral"
            description="3 in progress"
            size="sm"
          />
          <MetricCard
            title="Velocity Trend"
            value={42}
            unit="pts"
            trend="up"
            trendValue={5}
            description="6-sprint avg"
            size="sm"
          />
          <MetricCard
            title="Quality Score"
            value="A+"
            trend="up"
            description="Zero defects"
            size="sm"
          />
        </MetricCardGrid>
      </div>

      <div>
        <h3 className="mb-4 text-lg font-semibold">Project Forecasting</h3>
        <MetricCardGrid cols={3}>
          <MetricCard
            title="50% Confidence Date"
            value="Mar 15"
            description="Most likely completion"
            footer={
              <div className="mt-2 text-xs text-gray-600">
                8 sprints remaining at current velocity
              </div>
            }
          />
          <MetricCard
            title="85% Confidence Date"
            value="Apr 12"
            description="Conservative estimate"
            trend="neutral"
            trendValue="28"
            trendLabel="days buffer"
            footer={
              <div className="mt-2 text-xs text-gray-600">
                10 sprints with risk buffer included
              </div>
            }
          />
          <MetricCard
            title="Completion Probability"
            value={92}
            unit="%"
            description="By target date (Apr 1)"
            trend="up"
            trendValue={7}
            trendLabel="vs last week"
            footer={
              <div className="mt-2 text-xs text-gray-600">
                Based on 10,000 Monte Carlo simulations
              </div>
            }
          />
        </MetricCardGrid>
      </div>
    </div>
  ),
}

export const TeamMetrics: Story = {
  render: () => (
    <MetricCardGrid cols={2}>
      <MetricCard
        title="Sarah Chen"
        value={21}
        unit="points delivered"
        description="Senior Engineer"
        trend="up"
        trendValue={15}
        trendLabel="above average"
        icon={
          <div className="flex h-full w-full items-center justify-center rounded-full bg-green-100 text-xs font-medium text-green-800">
            SC
          </div>
        }
      />
      <MetricCard
        title="Mike Johnson"
        value={13}
        unit="points delivered"
        description="Engineer"
        trend="neutral"
        trendValue={0}
        trendLabel="on track"
        icon={
          <div className="flex h-full w-full items-center justify-center rounded-full bg-blue-100 text-xs font-medium text-blue-800">
            MJ
          </div>
        }
      />
      <MetricCard
        title="Emily Davis"
        value={18}
        unit="points delivered"
        description="Lead Engineer"
        trend="up"
        trendValue={8}
        trendLabel="exceeding target"
        icon={
          <div className="flex h-full w-full items-center justify-center rounded-full bg-purple-100 text-xs font-medium text-purple-800">
            ED
          </div>
        }
      />
      <MetricCard
        title="David Kim"
        value={8}
        unit="points delivered"
        description="Junior Engineer"
        trend="up"
        trendValue={33}
        trendLabel="improving"
        icon={
          <div className="flex h-full w-full items-center justify-center rounded-full bg-orange-100 text-xs font-medium text-orange-800">
            DK
          </div>
        }
      />
    </MetricCardGrid>
  ),
}