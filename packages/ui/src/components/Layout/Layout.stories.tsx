import type { Meta, StoryObj } from '@storybook/react'
import {
  Container,
  Header,
  HeaderLogo,
  HeaderNav,
  HeaderActions,
  Footer,
  FooterSection,
  Main,
  PageLayout,
  Section,
  Grid,
} from './Layout'
import { Button } from '../../primitives/Button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../Card'

const meta = {
  title: 'Components/Layout',
  component: Container,
  tags: ['autodocs'],
  parameters: {
    layout: 'fullscreen',
  },
} satisfies Meta<typeof Container>

export default meta
type Story = StoryObj<typeof meta>

export const ContainerSizes: Story = {
  render: () => (
    <div className="space-y-8 py-8">
      <Container size="sm" className="border-2 border-dashed border-gray-300 py-4">
        <p className="text-center text-sm text-gray-600">Small Container (max-w-3xl)</p>
      </Container>
      <Container size="md" className="border-2 border-dashed border-gray-300 py-4">
        <p className="text-center text-sm text-gray-600">Medium Container (max-w-5xl)</p>
      </Container>
      <Container size="lg" className="border-2 border-dashed border-gray-300 py-4">
        <p className="text-center text-sm text-gray-600">Large Container (max-w-7xl) - Default</p>
      </Container>
      <Container size="xl" className="border-2 border-dashed border-gray-300 py-4">
        <p className="text-center text-sm text-gray-600">XL Container (max-w-[90rem])</p>
      </Container>
      <Container size="full" className="border-2 border-dashed border-gray-300 py-4">
        <p className="text-center text-sm text-gray-600">Full Width Container</p>
      </Container>
    </div>
  ),
}

export const BasicHeader: Story = {
  render: () => (
    <Header>
      <HeaderLogo href="/">
        <div className="h-8 w-8 rounded bg-[#03564c]" />
        Sprint Radar
      </HeaderLogo>
      <HeaderNav>
        <a href="#" className="text-gray-600 hover:text-gray-900">Dashboard</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Reports</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Teams</a>
        <a href="#" className="text-gray-600 hover:text-gray-900">Settings</a>
      </HeaderNav>
      <HeaderActions>
        <Button variant="outline" size="sm">Export</Button>
        <Button size="sm">Generate Report</Button>
      </HeaderActions>
    </Header>
  ),
}

export const StickyHeader: Story = {
  render: () => (
    <div className="h-[200vh]">
      <Header sticky>
        <HeaderLogo>
          <div className="h-8 w-8 rounded bg-[#03564c]" />
          Sprint Radar
        </HeaderLogo>
        <HeaderNav>
          <a href="#" className="text-gray-600 hover:text-gray-900">Dashboard</a>
          <a href="#" className="text-gray-600 hover:text-gray-900">Reports</a>
          <a href="#" className="text-gray-600 hover:text-gray-900">Teams</a>
        </HeaderNav>
        <HeaderActions>
          <Button size="sm">Sign In</Button>
        </HeaderActions>
      </Header>
      <Container className="py-8">
        <p className="text-gray-600">Scroll down to see the sticky header in action...</p>
        <div className="mt-96">
          <p className="text-gray-600">Keep scrolling...</p>
        </div>
      </Container>
    </div>
  ),
}

export const BasicFooter: Story = {
  render: () => (
    <Footer>
      <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
        <FooterSection title="Product">
          <a href="#" className="block hover:text-gray-900">Features</a>
          <a href="#" className="block hover:text-gray-900">Pricing</a>
          <a href="#" className="block hover:text-gray-900">Documentation</a>
          <a href="#" className="block hover:text-gray-900">API Reference</a>
        </FooterSection>
        <FooterSection title="Company">
          <a href="#" className="block hover:text-gray-900">About</a>
          <a href="#" className="block hover:text-gray-900">Blog</a>
          <a href="#" className="block hover:text-gray-900">Careers</a>
          <a href="#" className="block hover:text-gray-900">Contact</a>
        </FooterSection>
        <FooterSection title="Resources">
          <a href="#" className="block hover:text-gray-900">Guides</a>
          <a href="#" className="block hover:text-gray-900">Webinars</a>
          <a href="#" className="block hover:text-gray-900">Case Studies</a>
          <a href="#" className="block hover:text-gray-900">Community</a>
        </FooterSection>
        <FooterSection title="Legal">
          <a href="#" className="block hover:text-gray-900">Privacy</a>
          <a href="#" className="block hover:text-gray-900">Terms</a>
          <a href="#" className="block hover:text-gray-900">Security</a>
          <a href="#" className="block hover:text-gray-900">Compliance</a>
        </FooterSection>
      </div>
      <div className="mt-8 border-t border-gray-200 pt-8 text-center text-sm text-gray-600">
        © 2025 Sprint Radar. All rights reserved.
      </div>
    </Footer>
  ),
}

export const FullPageLayout: Story = {
  render: () => (
    <PageLayout>
      <Header>
        <HeaderLogo>
          <div className="h-8 w-8 rounded bg-[#03564c]" />
          Sprint Radar
        </HeaderLogo>
        <HeaderNav>
          <a href="#" className="text-gray-600 hover:text-gray-900">Dashboard</a>
          <a href="#" className="text-gray-600 hover:text-gray-900">Reports</a>
          <a href="#" className="text-gray-600 hover:text-gray-900">Teams</a>
        </HeaderNav>
        <HeaderActions>
          <Button size="sm">Generate Report</Button>
        </HeaderActions>
      </Header>

      <Main>
        <Section spacing="lg">
          <Container>
            <h1 className="mb-4 text-3xl font-bold">Sprint Analytics Dashboard</h1>
            <p className="text-gray-600">
              Track your team's performance, velocity, and project forecasts with data-driven insights.
            </p>
          </Container>
        </Section>

        <Section spacing="md" className="bg-gray-50">
          <Container>
            <Grid cols={3} gap="lg">
              <Card>
                <CardHeader>
                  <CardTitle>Sprint Velocity</CardTitle>
                  <CardDescription>Last 6 sprints average</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">42.5</p>
                  <p className="text-sm text-gray-600">story points</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Completion Rate</CardTitle>
                  <CardDescription>Current sprint progress</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">93.3%</p>
                  <p className="text-sm text-gray-600">42 of 45 points</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Forecast</CardTitle>
                  <CardDescription>85% confidence date</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold">Apr 12</p>
                  <p className="text-sm text-gray-600">10 sprints remaining</p>
                </CardContent>
              </Card>
            </Grid>
          </Container>
        </Section>
      </Main>

      <Footer>
        <div className="text-center text-sm text-gray-600">
          Sprint Radar © 2025 - Enterprise Agile Analytics
        </div>
      </Footer>
    </PageLayout>
  ),
}

export const GridLayouts: Story = {
  render: () => (
    <Container className="py-8">
      <div className="space-y-8">
        <div>
          <h3 className="mb-4 text-lg font-semibold">2 Column Grid</h3>
          <Grid cols={2} gap="md">
            <div className="rounded-lg bg-gray-100 p-4">Column 1</div>
            <div className="rounded-lg bg-gray-100 p-4">Column 2</div>
          </Grid>
        </div>

        <div>
          <h3 className="mb-4 text-lg font-semibold">3 Column Grid</h3>
          <Grid cols={3} gap="md">
            <div className="rounded-lg bg-gray-100 p-4">Column 1</div>
            <div className="rounded-lg bg-gray-100 p-4">Column 2</div>
            <div className="rounded-lg bg-gray-100 p-4">Column 3</div>
          </Grid>
        </div>

        <div>
          <h3 className="mb-4 text-lg font-semibold">4 Column Grid</h3>
          <Grid cols={4} gap="md">
            <div className="rounded-lg bg-gray-100 p-4">Col 1</div>
            <div className="rounded-lg bg-gray-100 p-4">Col 2</div>
            <div className="rounded-lg bg-gray-100 p-4">Col 3</div>
            <div className="rounded-lg bg-gray-100 p-4">Col 4</div>
          </Grid>
        </div>

        <div>
          <h3 className="mb-4 text-lg font-semibold">Mixed Content Grid</h3>
          <Grid cols={3} gap="lg">
            <Card>
              <CardHeader>
                <CardTitle>Metric 1</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">123</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Metric 2</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">456</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Metric 3</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-2xl font-bold">789</p>
              </CardContent>
            </Card>
          </Grid>
        </div>
      </div>
    </Container>
  ),
}

export const ReportLayout: Story = {
  render: () => (
    <PageLayout>
      <Header>
        <HeaderLogo>Sprint Radar Report</HeaderLogo>
        <HeaderActions>
          <Button variant="outline" size="sm">Download PDF</Button>
          <Button variant="outline" size="sm">Share</Button>
        </HeaderActions>
      </Header>

      <Main>
        <Section spacing="sm">
          <Container size="md">
            <div className="text-center">
              <h1 className="text-3xl font-bold">Sprint 42 Performance Report</h1>
              <p className="mt-2 text-gray-600">Generated on January 31, 2025</p>
            </div>
          </Container>
        </Section>

        <Section spacing="md">
          <Container size="md">
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Executive Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p>
                    Sprint 42 achieved a 93.3% completion rate with 42 out of 45 committed story points delivered.
                    The team maintained a consistent velocity aligned with the 6-sprint average of 42.5 points.
                  </p>
                  <Grid cols={2} gap="md">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Key Achievements</p>
                      <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                        <li>Delivered all critical features on schedule</li>
                        <li>Maintained sub-3-day cycle time average</li>
                        <li>Zero critical bugs in production</li>
                      </ul>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-600">Areas for Improvement</p>
                      <ul className="mt-2 list-inside list-disc space-y-1 text-sm">
                        <li>3 story points carried over to next sprint</li>
                        <li>Increased code review cycle time</li>
                        <li>Testing bottleneck on day 8</li>
                      </ul>
                    </div>
                  </Grid>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Team Performance Metrics</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-64 rounded bg-gray-50" />
                  <p className="mt-4 text-center text-sm text-gray-600">
                    [Chart: Team velocity and performance metrics]
                  </p>
                </CardContent>
              </Card>
            </div>
          </Container>
        </Section>
      </Main>

      <Footer>
        <div className="text-center text-xs text-gray-500">
          Confidential - For internal use only
        </div>
      </Footer>
    </PageLayout>
  ),
}