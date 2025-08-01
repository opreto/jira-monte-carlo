import * as React from 'react'
import { cn } from '../../lib/utils'
import {
  PageLayout,
  Header,
  HeaderLogo,
  HeaderActions,
  Main,
  Footer,
  Container,
  Section,
  Grid,
} from '../../components/Layout'
import { Button } from '../../primitives/Button'

// Report Template Props
export interface ReportTemplateProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string
  subtitle?: string
  date?: string | Date
  logo?: React.ReactNode
  headerActions?: React.ReactNode
  footerContent?: React.ReactNode
  printable?: boolean
}

// Main Report Template
const ReportTemplate = React.forwardRef<HTMLDivElement, ReportTemplateProps>(
  (
    {
      className,
      title,
      subtitle,
      date,
      logo,
      headerActions,
      footerContent,
      printable = true,
      children,
      ...props
    },
    ref
  ) => {
    const formattedDate = date
      ? date instanceof Date
        ? date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
          })
        : date
      : new Date().toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        })

    return (
      <PageLayout
        ref={ref}
        className={cn(
          'bg-white',
          printable && 'print:text-black',
          className
        )}
        {...props}
      >
        <Header className="print:hidden">
          <HeaderLogo>{logo || 'Sprint Radar'}</HeaderLogo>
          <HeaderActions>
            {headerActions || (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => window.print()}
                >
                  Print
                </Button>
                <Button variant="outline" size="sm">
                  Export PDF
                </Button>
              </>
            )}
          </HeaderActions>
        </Header>

        <Main>
          <Section spacing="md">
            <Container size="lg">
              <div className="text-center">
                <h1 className="text-3xl font-bold text-gray-900 sm:text-4xl">
                  {title}
                </h1>
                {subtitle && (
                  <p className="mt-2 text-lg text-gray-600">{subtitle}</p>
                )}
                <p className="mt-4 text-sm text-gray-500">
                  Generated on {formattedDate}
                </p>
              </div>
            </Container>
          </Section>

          {children}
        </Main>

        <Footer className="print:hidden">
          {footerContent || (
            <div className="text-center text-sm text-gray-500">
              © {new Date().getFullYear()} Sprint Radar - Enterprise Agile Analytics
            </div>
          )}
        </Footer>
      </PageLayout>
    )
  }
)
ReportTemplate.displayName = 'ReportTemplate'

// Report Section Component
export interface ReportSectionProps extends React.HTMLAttributes<HTMLElement> {
  title?: string
  description?: string
  spacing?: 'sm' | 'md' | 'lg'
}

const ReportSection = React.forwardRef<HTMLElement, ReportSectionProps>(
  ({ className, title, description, spacing = 'md', children, ...props }, ref) => {
    return (
      <Section ref={ref} spacing={spacing} className={className} {...props}>
        <Container size="lg">
          {(title || description) && (
            <div className="mb-6">
              {title && (
                <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
              )}
              {description && (
                <p className="mt-2 text-gray-600">{description}</p>
              )}
            </div>
          )}
          {children}
        </Container>
      </Section>
    )
  }
)
ReportSection.displayName = 'ReportSection'

// Executive Summary Component
export interface ExecutiveSummaryProps extends React.HTMLAttributes<HTMLDivElement> {
  highlights?: Array<{
    label: string
    value: string | number
    unit?: string
  }>
}

const ExecutiveSummary = React.forwardRef<HTMLDivElement, ExecutiveSummaryProps>(
  ({ className, highlights, children, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          'rounded-lg border border-gray-200 bg-gray-50 p-6',
          className
        )}
        {...props}
      >
        {highlights && highlights.length > 0 && (
          <Grid cols={highlights.length > 3 ? 4 : highlights.length as any} gap="md" className="mb-6">
            {highlights.map((highlight, index) => (
              <div key={index} className="text-center">
                <p className="text-sm font-medium text-gray-600">
                  {highlight.label}
                </p>
                <p className="mt-1 text-2xl font-bold text-gray-900">
                  {highlight.value}
                  {highlight.unit && (
                    <span className="ml-1 text-lg font-normal text-gray-600">
                      {highlight.unit}
                    </span>
                  )}
                </p>
              </div>
            ))}
          </Grid>
        )}
        <div className="prose prose-sm max-w-none text-gray-700">{children}</div>
      </div>
    )
  }
)
ExecutiveSummary.displayName = 'ExecutiveSummary'

// Metric Summary Component
export interface MetricSummaryProps extends React.HTMLAttributes<HTMLDivElement> {
  metrics: Array<{
    label: string
    value: string | number
    change?: string | number
    trend?: 'up' | 'down' | 'neutral'
  }>
  columns?: 2 | 3 | 4
}

const MetricSummary = React.forwardRef<HTMLDivElement, MetricSummaryProps>(
  ({ className, metrics, columns = 3, ...props }, ref) => {
    return (
      <Grid ref={ref} cols={columns} gap="md" className={className} {...props}>
        {metrics.map((metric, index) => (
          <div
            key={index}
            className="rounded-lg border border-gray-200 bg-white p-4"
          >
            <p className="text-sm font-medium text-gray-600">{metric.label}</p>
            <p className="mt-1 text-xl font-bold text-gray-900">
              {metric.value}
            </p>
            {metric.change !== undefined && (
              <p
                className={cn('mt-1 text-sm', {
                  'text-green-600': metric.trend === 'up',
                  'text-red-600': metric.trend === 'down',
                  'text-gray-600': metric.trend === 'neutral',
                })}
              >
                {metric.trend === 'up' && '↑'}
                {metric.trend === 'down' && '↓'}
                {metric.trend === 'neutral' && '→'} {metric.change}
                {typeof metric.change === 'number' && '%'}
              </p>
            )}
          </div>
        ))}
      </Grid>
    )
  }
)
MetricSummary.displayName = 'MetricSummary'

// Print styles component
export const PrintStyles = () => (
  <style dangerouslySetInnerHTML={{ __html: `
    @media print {
      @page {
        size: A4;
        margin: 20mm;
      }

      body {
        print-color-adjust: exact;
        -webkit-print-color-adjust: exact;
      }

      .print\\:hidden {
        display: none !important;
      }

      .no-page-break {
        page-break-inside: avoid;
      }

      h1,
      h2,
      h3,
      h4,
      h5,
      h6 {
        page-break-after: avoid;
      }

      table {
        page-break-inside: avoid;
      }

      img,
      svg {
        max-width: 100% !important;
        page-break-inside: avoid;
      }
    }
  `}} />
)

export {
  ReportTemplate,
  ReportSection,
  ExecutiveSummary,
  MetricSummary,
}