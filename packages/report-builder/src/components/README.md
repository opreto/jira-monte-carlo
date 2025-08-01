# Sprint Radar Design System

This design system provides a consistent set of components and patterns for building Sprint Radar analytics reports. It follows Opreto brand guidelines and analytics best practices.

## Design Principles

1. **Clarity First**: All components prioritize clear communication of complex data
2. **Progressive Disclosure**: Use tooltips and expandable sections for detailed information
3. **Visual Hierarchy**: Employ typography, color, and spacing to guide attention
4. **Accessibility**: All components meet WCAG 2.1 AA standards
5. **Consistency**: Standardized patterns across all report types

## Typography

The design system uses a two-font system:

- **Display Font (Sublima)**: Used for main headings and report titles. Falls back to Georgia serif.
- **Body Font (Inter)**: Used for all other text content. Provides excellent readability at all sizes.

```tsx
// Display heading
<h1 className="font-display">Sprint Radar Analytics</h1>

// Body text
<p className="font-sans">Report content here...</p>
```

## Color Palette

### Primary Colors (Teal)
- Used for primary actions, links, and brand elements
- Range from `teal-50` (lightest) to `teal-900` (darkest)

### Status Colors
- **Success** (#00A86B): Positive metrics, healthy scores
- **Warning** (#FFA500): Caution states, moderate scores  
- **Error** (#DC143C): Critical issues, poor scores
- **Info** (#0E5473): Neutral information, conservative estimates

## Icons

The design system includes Font Awesome v7 style icons implemented as inline SVGs:

- `mlInsight`: Sparkle icon for ML-powered insights
- `info`: Information/help indicator
- `trendUp/trendDown`: Trend indicators
- `chart`: Data visualization
- `calendar`: Time-based information
- `sprint`: Sprint/agile cycles
- `health`: Process health
- `forecast`: Predictions and forecasts
- `settings`: Configuration

## Core Components

### Cards
Basic container component with optional elevation:

```tsx
<Card elevated>
  <CardHeader>
    <CardTitle>Section Title</CardTitle>
  </CardHeader>
  <CardContent>
    Content goes here...
  </CardContent>
</Card>
```

### Tables
Professional data tables with hover states:

```tsx
<Table>
  <TableHeader>
    <TableRow>
      <TableHead>Column 1</TableHead>
      <TableHead>Column 2</TableHead>
    </TableRow>
  </TableHeader>
  <TableBody>
    <TableRow>
      <TableCell>Data 1</TableCell>
      <TableCell>Data 2</TableCell>
    </TableRow>
  </TableBody>
</Table>
```

### Tooltips

#### ML Tooltip
For machine learning insights with clear ML indicator:

```tsx
<MLTooltip content="ML-powered insight explanation">
  <span>Metric with ML analysis</span>
</MLTooltip>
```

#### Info Tooltip
For general help and context:

```tsx
<InfoTooltip content="Additional context">
  Metric Name
</InfoTooltip>
```

### Metric Cards
Compact cards for key metrics:

```tsx
<MetricCard
  title="Average Velocity"
  value="42.5"
  unit="points/sprint"
  tooltip="Explanation of metric"
  trend="up"
  highlight={true}
  size="sm"
/>
```

### Charts
Wrapper component for Plotly charts with consistent styling:

```tsx
<Chart
  data={chartData}
  layout={chartLayout}
  description="What the chart shows"
  importance="Why it matters"
  lookFor="Key insights to notice"
/>
```

### Header
Full-width header with circuit board pattern:

```tsx
<Header>
  <div className="max-w-7xl mx-auto px-4 py-10">
    <h1 className="text-4xl font-display text-white">
      Report Title
    </h1>
  </div>
</Header>
```

## Chart Descriptions
Provides context for data visualizations:

```tsx
<ChartDescription
  title="Chart Title"
  description="What it shows"
  importance="Why it matters"
  lookFor="What to look for"
/>
```

## Usage Guidelines

### Spacing
- Use consistent spacing scale: 1, 2, 4, 6, 8, 10, 12, 16
- Sections: `mb-10`
- Cards: `mb-4` 
- Inline elements: `ml-2`, `mr-2`

### Responsive Design
- All components use responsive utilities
- Mobile-first approach
- Key breakpoints: `sm` (640px), `md` (768px), `lg` (1024px)

### Hover States
- Cards: Shadow increases on hover
- Tables: Row highlight on hover
- Tooltips: Appear on hover with smooth transitions

### Loading States
- Use skeleton screens for charts
- Show progress indicators for data loading
- Maintain layout stability during updates

## Accessibility

- All interactive elements have focus states
- Color is never the only indicator (icons/text supplement)
- Proper ARIA labels on complex components
- Keyboard navigation support throughout
- Screen reader friendly markup

## Best Practices

1. **Progressive Enhancement**: Start with essential information, add details through interaction
2. **Consistent Patterns**: Use the same component for the same type of data
3. **Clear Hierarchy**: Use typography and spacing to establish visual hierarchy
4. **Meaningful Colors**: Reserve status colors for their intended purpose
5. **Helpful Tooltips**: Provide context without overwhelming the user
6. **ML Transparency**: Always indicate when insights are ML-powered

## Development

Run Storybook to see all components:

```bash
npm run storybook
```

Import components from the design system:

```tsx
import { Card, MLTooltip, MetricCard } from '../components/DesignSystem'
```