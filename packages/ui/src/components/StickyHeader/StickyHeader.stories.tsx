import type { Meta, StoryObj } from '@storybook/react'
import { StickyHeader } from './StickyHeader'

const meta = {
  title: 'Components/StickyHeader',
  component: StickyHeader,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
  argTypes: {
    offsetTop: {
      control: { type: 'number' },
      description: 'Distance from top of viewport when sticky',
    },
    className: {
      control: { type: 'text' },
      description: 'CSS class for the wrapper element',
    },
    stickyClassName: {
      control: { type: 'text' },
      description: 'Additional CSS class when sticky',
    },
  },
} satisfies Meta<typeof StickyHeader>

export default meta
type Story = StoryObj<typeof meta>

// Helper component to create scrollable content
const ScrollableContent = ({ lines = 50 }: { lines?: number }) => (
  <div className="p-4">
    {Array.from({ length: lines }, (_, i) => (
      <p key={i} className="mb-2 text-gray-600">
        This is line {i + 1} of scrollable content. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
      </p>
    ))}
  </div>
)

export const Default: Story = {
  render: (args) => (
    <div className="min-h-screen bg-gray-50">
      {/* Main header */}
      <header className="bg-teal-700 text-white p-8">
        <h1 className="text-3xl font-bold">Main Site Header</h1>
        <p className="mt-2">This header stays at the top</p>
      </header>

      {/* Sticky header */}
      <StickyHeader {...args}>
        <div className="bg-white shadow-lg border-b border-gray-200 p-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <h2 className="text-xl font-semibold">Sticky Section Header</h2>
            <button className="px-4 py-2 bg-teal-600 text-white rounded hover:bg-teal-700">
              Action Button
            </button>
          </div>
        </div>
      </StickyHeader>

      {/* Content */}
      <ScrollableContent lines={100} />
    </div>
  ),
  args: {
    offsetTop: 0,
  },
}

export const WithOffset: Story = {
  render: (args) => (
    <div className="min-h-screen bg-gray-50">
      {/* Fixed top bar */}
      <div className="fixed top-0 left-0 right-0 bg-gray-900 text-white p-2 z-50">
        <div className="max-w-6xl mx-auto text-sm">
          Fixed Top Bar (height: 40px)
        </div>
      </div>

      {/* Main content with padding for fixed bar */}
      <div className="pt-10">
        <header className="bg-teal-700 text-white p-8">
          <h1 className="text-3xl font-bold">Main Header</h1>
          <p className="mt-2">Below the fixed top bar</p>
        </header>

        <StickyHeader {...args}>
          <div className="bg-white shadow-lg border-b border-gray-200 p-4">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-xl font-semibold">Sticky Header with Offset</h2>
              <p className="text-sm text-gray-600">Sticks below the fixed top bar</p>
            </div>
          </div>
        </StickyHeader>

        <ScrollableContent lines={100} />
      </div>
    </div>
  ),
  args: {
    offsetTop: 40, // Offset to account for fixed top bar
  },
}

export const ScenarioSwitcher: Story = {
  render: (args) => {
    const [scenario, setScenario] = React.useState<'baseline' | 'adjusted'>('baseline')
    
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-gradient-to-r from-teal-700 to-teal-800 text-white p-8">
          <h1 className="text-4xl font-bold">Sprint Radar Analytics</h1>
          <p className="mt-2 text-teal-100">Monte Carlo Simulation Forecast</p>
        </header>

        <StickyHeader 
          {...args}
          stickyClassName="shadow-xl"
        >
          <div className="bg-white border-b border-gray-200 p-4">
            <div className="max-w-6xl mx-auto">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                    <span className="mr-2">📊</span>
                    Velocity Scenario Analysis
                  </h3>
                  <div className="flex items-center space-x-2 bg-gray-100 rounded-lg p-1">
                    <button
                      onClick={() => setScenario('baseline')}
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                        scenario === 'baseline'
                          ? 'bg-white text-teal-700 shadow-sm'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Baseline
                    </button>
                    <button
                      onClick={() => setScenario('adjusted')}
                      className={`px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                        scenario === 'adjusted'
                          ? 'bg-white text-teal-700 shadow-sm'
                          : 'text-gray-600 hover:text-gray-900'
                      }`}
                    >
                      Adjusted
                    </button>
                  </div>
                </div>
                
                <div className="text-sm text-gray-600">
                  {scenario === 'adjusted' ? (
                    <>
                      <span className="font-medium">Scenario:</span> Team velocity -20% for 3 sprints
                      <br />
                      <span className="font-medium">Impact:</span> +1.5 sprints to completion
                    </>
                  ) : (
                    <span className="text-gray-500">Baseline forecast without velocity adjustments</span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </StickyHeader>

        <main className="max-w-6xl mx-auto p-6">
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-2xl font-semibold mb-4">
              {scenario === 'baseline' ? 'Baseline' : 'Adjusted'} Forecast Results
            </h2>
            <p className="text-gray-600 mb-4">
              This section shows the {scenario} forecast with{scenario === 'adjusted' ? '' : 'out'} velocity adjustments.
            </p>
          </div>
          
          <ScrollableContent lines={80} />
        </main>
      </div>
    )
  },
  args: {
    offsetTop: 0,
  },
}

export const DynamicContent: Story = {
  render: (args) => {
    const [expanded, setExpanded] = React.useState(false)
    
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-teal-700 text-white p-8">
          <h1 className="text-3xl font-bold">Dynamic Content Example</h1>
          <p className="mt-2">The sticky header adjusts its height automatically</p>
        </header>

        <StickyHeader {...args}>
          <div className="bg-white shadow-lg border-b border-gray-200 p-4">
            <div className="max-w-6xl mx-auto">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-xl font-semibold">Expandable Sticky Header</h2>
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
                >
                  {expanded ? 'Collapse' : 'Expand'}
                </button>
              </div>
              
              {expanded && (
                <div className="mt-4 p-4 bg-gray-50 rounded">
                  <p className="text-gray-600 mb-2">
                    Additional content that expands the header height.
                  </p>
                  <p className="text-gray-600">
                    The wrapper maintains the correct height to prevent content jumps.
                  </p>
                </div>
              )}
            </div>
          </div>
        </StickyHeader>

        <ScrollableContent lines={100} />
      </div>
    )
  },
  args: {
    offsetTop: 0,
  },
}