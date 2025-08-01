# Modern Design System Architecture

**Status:** PROPOSED  
**Date:** 2025-01-08  
**Decision Makers:** Development Team

## Context

The current presentation layer uses Python + Jinja2 templates with custom CSS. While functional, this approach lacks:
- Component reusability
- Type safety
- Modern developer experience
- Consistent design tokens
- Component documentation

## Decision

Implement a modern design system using React + Next.js with the following architecture:

### Tech Stack

1. **Frontend Framework:** React 18 + Next.js 14 (App Router)
2. **Language:** TypeScript
3. **Styling:** Tailwind CSS v3 + CSS Variables
4. **Component Library:** Radix UI (headless components)
5. **Design Tokens:** Style Dictionary
6. **Documentation:** Storybook 7
7. **Testing:** Playwright + React Testing Library
8. **Build System:** Turborepo (monorepo)
9. **PDF Export:** Puppeteer (server-side)

### Architecture Overview

```
sprint-radar/
├── apps/
│   ├── web/                    # Next.js application
│   │   ├── app/               # App router pages
│   │   ├── components/        # App-specific components
│   │   └── lib/              # Utilities
│   └── storybook/            # Storybook documentation
├── packages/
│   ├── design-tokens/        # Design tokens package
│   │   ├── tokens/          # JSON token definitions
│   │   ├── build/           # Generated outputs
│   │   └── config.js        # Style Dictionary config
│   ├── ui/                  # Component library
│   │   ├── primitives/      # Atoms (Button, Input, etc.)
│   │   ├── components/      # Molecules (Card, Chart, etc.)
│   │   ├── patterns/        # Organisms (Dashboard, Report)
│   │   └── index.ts         # Exports
│   └── charts/              # Data visualization components
└── services/
    └── api/                 # Python backend (existing)
```

### Design Tokens Structure

```json
{
  "color": {
    "base": {
      "gray": {
        "50": { "value": "#f9fafb" },
        "900": { "value": "#111827" }
      }
    },
    "semantic": {
      "background": {
        "light": { "value": "{color.base.white}" },
        "dark": { "value": "{color.base.gray.900}" }
      },
      "text": {
        "primary": {
          "light": { "value": "{color.base.gray.900}" },
          "dark": { "value": "{color.base.gray.50}" }
        }
      }
    }
  },
  "spacing": {
    "xs": { "value": "0.5rem" },
    "sm": { "value": "1rem" },
    "md": { "value": "1.5rem" },
    "lg": { "value": "2rem" },
    "xl": { "value": "3rem" }
  },
  "typography": {
    "fontFamily": {
      "sans": { "value": "Inter, system-ui, sans-serif" },
      "mono": { "value": "JetBrains Mono, monospace" }
    },
    "fontSize": {
      "xs": { "value": "0.75rem" },
      "sm": { "value": "0.875rem" },
      "base": { "value": "1rem" },
      "lg": { "value": "1.125rem" },
      "xl": { "value": "1.25rem" }
    }
  }
}
```

### Component Architecture

```typescript
// packages/ui/primitives/Button/Button.tsx
import { forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-primary text-primary-foreground hover:bg-primary/90',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground'
      },
      size: {
        sm: 'h-9 px-3 text-sm',
        md: 'h-10 px-4',
        lg: 'h-11 px-8'
      }
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md'
    }
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
```

### PDF Export Strategy

1. **Server-Side Rendering**: Next.js renders reports as static HTML
2. **PDF Generation API**: 
   ```typescript
   // app/api/export/pdf/route.ts
   export async function POST(request: Request) {
     const { reportId } = await request.json()
     
     const browser = await puppeteer.launch()
     const page = await browser.newPage()
     
     // Navigate to SSR report page
     await page.goto(`${process.env.NEXT_PUBLIC_URL}/reports/${reportId}?print=true`)
     
     // Generate PDF with print CSS
     const pdf = await page.pdf({
       format: 'A4',
       printBackground: true,
       margin: { top: '1cm', bottom: '1cm', left: '1cm', right: '1cm' }
     })
     
     await browser.close()
     
     return new Response(pdf, {
       headers: {
         'Content-Type': 'application/pdf',
         'Content-Disposition': `attachment; filename="report-${reportId}.pdf"`
       }
     })
   }
   ```

3. **Print Styles**: Dedicated print CSS in design system
   ```css
   @media print {
     .no-print { display: none !important; }
     .chart-container { page-break-inside: avoid; }
     body { font-size: 10pt; }
   }
   ```

### Migration Strategy

#### Phase 1: Foundation (Week 1-2)
- Set up monorepo structure
- Create design tokens package
- Configure Tailwind with tokens
- Set up Storybook

#### Phase 2: Core Components (Week 3-4)
- Build primitive components
- Document in Storybook
- Create chart components wrapper

#### Phase 3: API Integration (Week 5-6)
- Set up Next.js app
- Create API client for Python backend
- Implement authentication

#### Phase 4: First Report (Week 7-8)
- Migrate one report type to Next.js
- Implement SSR
- Test PDF export

#### Phase 5: Gradual Migration (Ongoing)
- Port remaining reports
- Deprecate Jinja templates
- Full cutover

## Benefits

1. **Developer Experience**
   - Type safety with TypeScript
   - Hot module replacement
   - Component isolation in Storybook
   - Modern tooling

2. **Consistency**
   - Design tokens ensure uniform styling
   - Reusable components prevent drift
   - Single source of truth

3. **Performance**
   - Smaller bundle sizes with tree-shaking
   - Optimized images with Next.js
   - Lazy loading components

4. **Maintainability**
   - Clear component boundaries
   - Automated testing
   - Documentation in code

5. **PDF Export**
   - Server-side rendering enables reliable PDF generation
   - Print styles integrated in design system
   - Consistent output across formats

## Risks & Mitigations

1. **Risk:** Learning curve for team
   - **Mitigation:** Gradual migration, training sessions

2. **Risk:** Python/React integration complexity
   - **Mitigation:** Clear API contracts, GraphQL consideration

3. **Risk:** PDF rendering differences
   - **Mitigation:** Extensive testing, visual regression tests

## Implementation Example

Here's a sample report component:

```typescript
// app/reports/[id]/page.tsx
import { Suspense } from 'react'
import { getReport } from '@/lib/api'
import { 
  ReportHeader, 
  MetricsGrid, 
  ChartGrid, 
  InsightsPanel 
} from '@sprint-radar/ui'

export default async function ReportPage({ 
  params,
  searchParams 
}: {
  params: { id: string }
  searchParams: { print?: string }
}) {
  const report = await getReport(params.id)
  const isPrint = searchParams.print === 'true'
  
  return (
    <div className={cn(
      'min-h-screen bg-background',
      isPrint && 'print:bg-white'
    )}>
      <ReportHeader 
        title={report.title}
        date={report.date}
        className="no-print"
      />
      
      <main className="container mx-auto px-4 py-8 print:px-0">
        <MetricsGrid metrics={report.metrics} />
        
        <Suspense fallback={<ChartSkeleton />}>
          <ChartGrid charts={report.charts} />
        </Suspense>
        
        <InsightsPanel insights={report.insights} />
      </main>
    </div>
  )
}
```

## Decision

Proceed with React + Next.js design system implementation following the phased approach outlined above.