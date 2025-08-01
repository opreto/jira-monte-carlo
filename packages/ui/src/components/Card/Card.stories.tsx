import type { Meta, StoryObj } from '@storybook/react'
import { Button } from '../../primitives/Button'
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from './Card'

const meta = {
  title: 'Components/Card',
  component: Card,
  tags: ['autodocs'],
} satisfies Meta<typeof Card>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Sprint Velocity</CardTitle>
        <CardDescription>Average story points completed per sprint</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="text-4xl font-bold">42</div>
        <p className="text-gray-600 text-sm mt-2">
          +12% from last quarter
        </p>
      </CardContent>
    </Card>
  ),
}

export const WithFooter: Story = {
  render: () => (
    <Card className="w-[350px]">
      <CardHeader>
        <CardTitle>Project Status</CardTitle>
        <CardDescription>Current sprint progress and health</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Completed</span>
            <span className="font-semibold">24/30</span>
          </div>
          <div className="flex justify-between">
            <span>In Progress</span>
            <span className="font-semibold">4</span>
          </div>
          <div className="flex justify-between">
            <span>Blocked</span>
            <span className="font-semibold text-red-600">2</span>
          </div>
        </div>
      </CardContent>
      <CardFooter>
        <Button className="w-full">View Details</Button>
      </CardFooter>
    </Card>
  ),
}

export const MetricCard: Story = {
  render: () => (
    <Card className="w-[250px]">
      <CardContent className="p-6">
        <div className="space-y-2">
          <p className="text-sm text-gray-600">Total Story Points</p>
          <p className="text-3xl font-bold text-[#03564c]">1,248</p>
          <p className="text-xs text-gray-500">Last 90 days</p>
        </div>
      </CardContent>
    </Card>
  ),
}

export const ChartCard: Story = {
  render: () => (
    <Card className="w-[600px]">
      <CardHeader>
        <CardTitle>Velocity Trend</CardTitle>
        <CardDescription>Story points completed over the last 10 sprints</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-64 bg-gray-100 rounded flex items-center justify-center text-gray-500">
          Chart placeholder
        </div>
      </CardContent>
    </Card>
  ),
}