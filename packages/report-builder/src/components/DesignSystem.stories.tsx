import React from 'react'
import type { Meta, StoryObj } from '@storybook/react'
import {
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
  colors,
  fontStyles
} from './DesignSystem'

// Meta configuration
const meta: Meta = {
  title: 'Sprint Radar/Design System',
  parameters: {
    layout: 'padded',
    docs: {
      description: {
        component: 'Design system components for Sprint Radar analytics reports following Opreto brand guidelines.'
      }
    }
  }
}

export default meta

// Font Styles Story
export const Typography: StoryObj = {
  render: () => (
    <div>
      <style dangerouslySetInnerHTML={{ __html: fontStyles }} />
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-4xl text-gray-900 mb-2">Display Heading (Sublima)</h1>
          <p className="text-gray-600">Used for main report titles and section headers</p>
        </div>
        <div>
          <h2 className="font-sans text-2xl font-semibold text-gray-900 mb-2">Sans Serif Heading (Inter)</h2>
          <p className="font-sans text-gray-600">Used for subsections and general text content</p>
        </div>
        <div>
          <p className="font-sans text-sm text-gray-700">
            Regular body text in Inter font family. This is the primary font for all report content,
            providing excellent readability at various sizes.
          </p>
        </div>
      </div>
    </div>
  )
}

// Color Palette Story
export const ColorPalette: StoryObj = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-xl font-semibold mb-4">Primary Colors (Teal)</h3>
        <div className="grid grid-cols-5 gap-4">
          {Object.entries(colors.teal).map(([shade, color]) => (
            <div key={shade} className="text-center">
              <div 
                className="w-full h-20 rounded-lg shadow-sm mb-2" 
                style={{ backgroundColor: color }}
              />
              <p className="text-sm font-mono">{shade}</p>
              <p className="text-xs text-gray-600">{color}</p>
            </div>
          ))}
        </div>
      </div>
      
      <div>
        <h3 className="text-xl font-semibold mb-4">Status Colors</h3>
        <div className="grid grid-cols-4 gap-4">
          {Object.entries({ 
            success: colors.success, 
            warning: colors.warning, 
            error: colors.error, 
            info: colors.info 
          }).map(([name, color]) => (
            <div key={name} className="text-center">
              <div 
                className="w-full h-20 rounded-lg shadow-sm mb-2" 
                style={{ backgroundColor: color }}
              />
              <p className="text-sm font-semibold capitalize">{name}</p>
              <p className="text-xs font-mono text-gray-600">{color}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// Icons Story
export const IconLibrary: StoryObj = {
  render: () => (
    <div className="grid grid-cols-4 gap-6">
      {Object.entries(Icons).map(([name, icon]) => (
        <div key={name} className="text-center p-4 border border-gray-200 rounded-lg">
          <div className="flex justify-center mb-2 text-gray-700">
            {React.cloneElement(icon as React.ReactElement, { className: 'w-8 h-8' })}
          </div>
          <p className="text-sm font-mono">{name}</p>
        </div>
      ))}
    </div>
  )
}

// Card Components Story
export const Cards: StoryObj = {
  render: () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Basic Card</CardTitle>
        </CardHeader>
        <CardContent>
          <p>This is a basic card with standard shadow and hover effects.</p>
        </CardContent>
      </Card>
      
      <Card elevated>
        <CardHeader>
          <CardTitle>Elevated Card</CardTitle>
        </CardHeader>
        <CardContent>
          <p>This card has enhanced shadow for more visual prominence.</p>
        </CardContent>
      </Card>
    </div>
  )
}

// Table Component Story
export const TableComponent: StoryObj = {
  render: () => (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Sprint</TableHead>
          <TableHead>Completed Points</TableHead>
          <TableHead>Velocity</TableHead>
          <TableHead>Health Score</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow>
          <TableCell>Sprint 21</TableCell>
          <TableCell>45</TableCell>
          <TableCell>42.5</TableCell>
          <TableCell>
            <span className="text-green-600 font-semibold">85%</span>
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Sprint 22</TableCell>
          <TableCell>38</TableCell>
          <TableCell>41.2</TableCell>
          <TableCell>
            <span className="text-orange-600 font-semibold">72%</span>
          </TableCell>
        </TableRow>
        <TableRow>
          <TableCell>Sprint 23</TableCell>
          <TableCell>52</TableCell>
          <TableCell>43.8</TableCell>
          <TableCell>
            <span className="text-green-600 font-semibold">91%</span>
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  )
}

// Tooltip Components Story
export const Tooltips: StoryObj = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-semibold mb-4">ML Tooltip</h3>
        <MLTooltip content="This is an ML-powered insight. Machine learning algorithms analyze your sprint patterns to identify trends and make predictions about future performance.">
          <span className="text-gray-700">Hover over the ML indicator to see insights</span>
        </MLTooltip>
      </div>
      
      <div>
        <h3 className="text-lg font-semibold mb-4">Info Tooltip</h3>
        <p className="text-gray-700">
          <InfoTooltip content="This tooltip provides additional context and explanations for metrics and features throughout the report.">
            Average Velocity
          </InfoTooltip>
        </p>
      </div>
    </div>
  )
}

// Metric Cards Story
export const MetricCards: StoryObj = {
  render: () => (
    <div className="grid grid-cols-3 gap-4">
      <MetricCard
        title="Remaining Work"
        value="127"
        unit="points"
        tooltip="Total story points remaining in the backlog"
        size="sm"
      />
      
      <MetricCard
        title="Average Velocity"
        value="42.5"
        unit="per sprint"
        tooltip="Rolling average of completed points per sprint"
        trend="up"
        size="sm"
        highlight={true}
      />
      
      <MetricCard
        title="Health Score"
        value="85"
        unit="%"
        tooltip="Overall process health across multiple dimensions"
        trend="neutral"
        size="sm"
      />
    </div>
  )
}

// Chart Description Story
export const ChartDescriptions: StoryObj = {
  render: () => (
    <div className="space-y-4">
      <ChartDescription
        title="Velocity Trend Chart"
        description="Shows team velocity over the last 10 sprints with trend line"
        importance="Helps identify if team performance is improving, declining, or stable"
        lookFor="Consistency in velocity and direction of the trend line"
      />
      
      <ChartDescription
        description="Monte Carlo simulation results showing completion probability"
        importance="Provides risk-adjusted forecasts for project completion"
        lookFor="The spread between optimistic and pessimistic scenarios"
      />
    </div>
  )
}

// Header Component Story
export const HeaderComponent: StoryObj = {
  render: () => (
    <Header>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-4xl md:text-5xl font-display text-white mb-2">
          Sprint Radar Analytics: Project Phoenix
        </h1>
        <p className="text-lg text-teal-100">
          Monte Carlo Simulation Forecast • Generated on December 13, 2024
        </p>
      </div>
    </Header>
  )
}

// Complete Report Section Story
export const ReportSection: StoryObj = {
  render: () => (
    <div className="bg-gray-50 p-8">
      <style dangerouslySetInnerHTML={{ __html: fontStyles }} />
      
      <section className="mb-10">
        <h2 className="text-3xl font-display text-gray-900 mb-6 border-b-2 border-teal-100 pb-2">
          Process Health Score
        </h2>
        
        <Card elevated>
          <CardContent>
            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center">
                <div className="text-6xl font-bold text-green-600">
                  85%
                </div>
                <MLTooltip content="Overall health score calculated from WIP limits, sprint consistency, flow efficiency, and other key metrics.">
                  <span className="ml-4 text-gray-600">Overall Health</span>
                </MLTooltip>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Strengths</h4>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    Consistent velocity over last 5 sprints
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    Low defect escape rate (< 5%)
                  </li>
                  <li className="flex items-start">
                    <span className="text-green-600 mr-2">✓</span>
                    Good sprint completion rate (88%)
                  </li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Areas for Improvement</h4>
                <ul className="space-y-1 text-sm text-gray-700">
                  <li className="flex items-start">
                    <span className="text-orange-600 mr-2">→</span>
                    Reduce WIP in "In Progress" column
                  </li>
                  <li className="flex items-start">
                    <span className="text-orange-600 mr-2">→</span>
                    Address aging items in backlog
                  </li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}