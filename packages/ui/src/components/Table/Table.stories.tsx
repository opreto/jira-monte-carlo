import type { Meta, StoryObj } from '@storybook/react'
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from './Table'

const meta = {
  title: 'Components/Table',
  component: Table,
  tags: ['autodocs'],
} satisfies Meta<typeof Table>

export default meta
type Story = StoryObj<typeof meta>

export const Default: Story = {
  render: () => (
    <Table>
      <TableCaption>A list of your recent invoices.</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[100px]">Invoice</TableHead>
          <TableHead>Status</TableHead>
          <TableHead>Method</TableHead>
          <TableHead className="text-right">Amount</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">INV001</TableCell>
          <TableCell>Paid</TableCell>
          <TableCell>Credit Card</TableCell>
          <TableCell className="text-right">$250.00</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">INV002</TableCell>
          <TableCell>Pending</TableCell>
          <TableCell>PayPal</TableCell>
          <TableCell className="text-right">$150.00</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">INV003</TableCell>
          <TableCell>Unpaid</TableCell>
          <TableCell>Bank Transfer</TableCell>
          <TableCell className="text-right">$350.00</TableCell>
        </TableRow>
      </TableBody>
      <TableFooter>
        <TableRow>
          <TableCell colSpan={3}>Total</TableCell>
          <TableCell className="text-right">$750.00</TableCell>
        </TableRow>
      </TableFooter>
    </Table>
  ),
}

export const SprintVelocity: Story = {
  render: () => (
    <Table>
      <TableCaption>Team velocity over the last 6 sprints</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Sprint</TableHead>
          <TableHead>Committed Points</TableHead>
          <TableHead>Completed Points</TableHead>
          <TableHead>Velocity %</TableHead>
          <TableHead className="text-right">Carry Over</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">Sprint 42</TableCell>
          <TableCell>45</TableCell>
          <TableCell>42</TableCell>
          <TableCell>93.3%</TableCell>
          <TableCell className="text-right">3</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Sprint 41</TableCell>
          <TableCell>50</TableCell>
          <TableCell>48</TableCell>
          <TableCell>96.0%</TableCell>
          <TableCell className="text-right">2</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Sprint 40</TableCell>
          <TableCell>40</TableCell>
          <TableCell>35</TableCell>
          <TableCell>87.5%</TableCell>
          <TableCell className="text-right">5</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Sprint 39</TableCell>
          <TableCell>45</TableCell>
          <TableCell>44</TableCell>
          <TableCell>97.8%</TableCell>
          <TableCell className="text-right">1</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Sprint 38</TableCell>
          <TableCell>42</TableCell>
          <TableCell>40</TableCell>
          <TableCell>95.2%</TableCell>
          <TableCell className="text-right">2</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Sprint 37</TableCell>
          <TableCell>48</TableCell>
          <TableCell>46</TableCell>
          <TableCell>95.8%</TableCell>
          <TableCell className="text-right">2</TableCell>
        </TableRow>
      </TableBody>
      <TableFooter>
        <TableRow>
          <TableCell>Average</TableCell>
          <TableCell>45</TableCell>
          <TableCell>42.5</TableCell>
          <TableCell>94.3%</TableCell>
          <TableCell className="text-right">2.5</TableCell>
        </TableRow>
      </TableFooter>
    </Table>
  ),
}

export const TeamPerformance: Story = {
  render: () => (
    <Table>
      <TableCaption>Team performance metrics for current sprint</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Team Member</TableHead>
          <TableHead>Role</TableHead>
          <TableHead>Stories Completed</TableHead>
          <TableHead>Points Delivered</TableHead>
          <TableHead>Avg Cycle Time</TableHead>
          <TableHead className="text-right">PR Reviews</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">Sarah Chen</TableCell>
          <TableCell>Senior Engineer</TableCell>
          <TableCell>8</TableCell>
          <TableCell>21</TableCell>
          <TableCell>2.3 days</TableCell>
          <TableCell className="text-right">15</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Mike Johnson</TableCell>
          <TableCell>Engineer</TableCell>
          <TableCell>6</TableCell>
          <TableCell>13</TableCell>
          <TableCell>3.1 days</TableCell>
          <TableCell className="text-right">12</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Emily Davis</TableCell>
          <TableCell>Lead Engineer</TableCell>
          <TableCell>5</TableCell>
          <TableCell>18</TableCell>
          <TableCell>2.8 days</TableCell>
          <TableCell className="text-right">22</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">David Kim</TableCell>
          <TableCell>Junior Engineer</TableCell>
          <TableCell>4</TableCell>
          <TableCell>8</TableCell>
          <TableCell>4.2 days</TableCell>
          <TableCell className="text-right">8</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">Lisa Wang</TableCell>
          <TableCell>Senior Engineer</TableCell>
          <TableCell>7</TableCell>
          <TableCell>19</TableCell>
          <TableCell>2.5 days</TableCell>
          <TableCell className="text-right">18</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  ),
}

export const BugMetrics: Story = {
  render: () => (
    <Table>
      <TableCaption>Bug metrics by priority</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Priority</TableHead>
          <TableHead>Open</TableHead>
          <TableHead>In Progress</TableHead>
          <TableHead>Resolved</TableHead>
          <TableHead>Avg Resolution Time</TableHead>
          <TableHead className="text-right">Total</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-red-500" />
              Critical
            </span>
          </TableCell>
          <TableCell>2</TableCell>
          <TableCell>1</TableCell>
          <TableCell>15</TableCell>
          <TableCell>1.2 days</TableCell>
          <TableCell className="text-right">18</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-orange-500" />
              High
            </span>
          </TableCell>
          <TableCell>8</TableCell>
          <TableCell>5</TableCell>
          <TableCell>42</TableCell>
          <TableCell>3.5 days</TableCell>
          <TableCell className="text-right">55</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-yellow-500" />
              Medium
            </span>
          </TableCell>
          <TableCell>15</TableCell>
          <TableCell>8</TableCell>
          <TableCell>89</TableCell>
          <TableCell>5.8 days</TableCell>
          <TableCell className="text-right">112</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">
            <span className="inline-flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
              Low
            </span>
          </TableCell>
          <TableCell>32</TableCell>
          <TableCell>12</TableCell>
          <TableCell>156</TableCell>
          <TableCell>12.3 days</TableCell>
          <TableCell className="text-right">200</TableCell>
        </TableRow>
      </TableBody>
      <TableFooter>
        <TableRow>
          <TableCell>Total</TableCell>
          <TableCell>57</TableCell>
          <TableCell>26</TableCell>
          <TableCell>302</TableCell>
          <TableCell>-</TableCell>
          <TableCell className="text-right">385</TableCell>
        </TableRow>
      </TableFooter>
    </Table>
  ),
}

export const ProjectForecast: Story = {
  render: () => (
    <Table>
      <TableCaption>Monte Carlo simulation results for project completion</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Confidence Level</TableHead>
          <TableHead>Completion Date</TableHead>
          <TableHead>Remaining Sprints</TableHead>
          <TableHead>Total Points</TableHead>
          <TableHead className="text-right">Buffer Days</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">50% (Likely)</TableCell>
          <TableCell>March 15, 2025</TableCell>
          <TableCell>8</TableCell>
          <TableCell>340</TableCell>
          <TableCell className="text-right">0</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">70% (Probable)</TableCell>
          <TableCell>March 29, 2025</TableCell>
          <TableCell>9</TableCell>
          <TableCell>340</TableCell>
          <TableCell className="text-right">14</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">85% (Conservative)</TableCell>
          <TableCell>April 12, 2025</TableCell>
          <TableCell>10</TableCell>
          <TableCell>340</TableCell>
          <TableCell className="text-right">28</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">95% (Very Conservative)</TableCell>
          <TableCell>April 26, 2025</TableCell>
          <TableCell>11</TableCell>
          <TableCell>340</TableCell>
          <TableCell className="text-right">42</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  ),
}

export const CycleTimeDistribution: Story = {
  render: () => (
    <Table>
      <TableCaption>Story cycle time distribution by size</TableCaption>
      <TableHeader>
        <TableRow>
          <TableHead>Story Size</TableHead>
          <TableHead>Count</TableHead>
          <TableHead>Min Time</TableHead>
          <TableHead>Avg Time</TableHead>
          <TableHead>Max Time</TableHead>
          <TableHead className="text-right">P95</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell className="font-medium">XS (1 point)</TableCell>
          <TableCell>45</TableCell>
          <TableCell>0.5 days</TableCell>
          <TableCell>1.2 days</TableCell>
          <TableCell>3.0 days</TableCell>
          <TableCell className="text-right">2.5 days</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">S (2-3 points)</TableCell>
          <TableCell>82</TableCell>
          <TableCell>1.0 days</TableCell>
          <TableCell>2.8 days</TableCell>
          <TableCell>6.0 days</TableCell>
          <TableCell className="text-right">5.2 days</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">M (5 points)</TableCell>
          <TableCell>56</TableCell>
          <TableCell>2.0 days</TableCell>
          <TableCell>4.5 days</TableCell>
          <TableCell>9.0 days</TableCell>
          <TableCell className="text-right">7.8 days</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">L (8 points)</TableCell>
          <TableCell>23</TableCell>
          <TableCell>3.5 days</TableCell>
          <TableCell>7.2 days</TableCell>
          <TableCell>14.0 days</TableCell>
          <TableCell className="text-right">12.5 days</TableCell>
        </TableRow>
        <TableRow>
          <TableCell className="font-medium">XL (13+ points)</TableCell>
          <TableCell>8</TableCell>
          <TableCell>5.0 days</TableCell>
          <TableCell>11.5 days</TableCell>
          <TableCell>21.0 days</TableCell>
          <TableCell className="text-right">19.0 days</TableCell>
        </TableRow>
      </TableBody>
    </Table>
  ),
}

export const WithoutBorder: Story = {
  render: () => (
    <div className="rounded-lg border p-4">
      <Table>
        <TableHeader>
          <TableRow className="border-b-0 hover:bg-transparent">
            <TableHead className="h-auto pb-2 pt-0">Metric</TableHead>
            <TableHead className="h-auto pb-2 pt-0 text-right">Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow className="border-b-0 hover:bg-transparent">
            <TableCell className="py-1">Sprint Velocity</TableCell>
            <TableCell className="py-1 text-right font-medium">42 points</TableCell>
          </TableRow>
          <TableRow className="border-b-0 hover:bg-transparent">
            <TableCell className="py-1">Team Capacity</TableCell>
            <TableCell className="py-1 text-right font-medium">85%</TableCell>
          </TableRow>
          <TableRow className="border-b-0 hover:bg-transparent">
            <TableCell className="py-1">Completion Rate</TableCell>
            <TableCell className="py-1 text-right font-medium">93.3%</TableCell>
          </TableRow>
          <TableRow className="border-b-0 hover:bg-transparent">
            <TableCell className="py-1">Bug Rate</TableCell>
            <TableCell className="py-1 text-right font-medium">0.12 per story</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  ),
}