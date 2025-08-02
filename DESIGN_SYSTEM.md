# Sprint Radar Design System

This document describes the modern design system implementation for Sprint Radar.

## Architecture Overview

The project now uses a monorepo structure with the following packages:

```
sprint-radar/
├── apps/
│   ├── web/          # Next.js 14 application
│   └── storybook/    # Storybook documentation
├── packages/
│   ├── design-tokens/  # Design tokens (colors, spacing, etc.)
│   ├── ui/            # React component library
│   └── charts/        # Chart components (coming soon)
└── src/               # Python backend (existing)
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm 10+
- Python 3.11+ (for backend)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Build the packages:
```bash
npm run build
```

3. Start development:
```bash
# Start all services
npm run dev

# Or start individually:
# Frontend only
cd apps/web && npm run dev

# Storybook only
cd apps/storybook && npm run storybook
```

## Design Tokens

The design system uses a comprehensive token system defined in `packages/design-tokens/tokens.json`:

- **Colors**: Base palette and semantic colors with light/dark mode support
- **Spacing**: Consistent spacing scale from 0 to 32
- **Typography**: Font families, sizes, and weights
- **Shadows**: Elevation system
- **Breakpoints**: Responsive design breakpoints

### Using Design Tokens

```tsx
// In React components
import { colors, spacing } from '@sprint-radar/design-tokens'

// In Tailwind classes
<div className="bg-primary-500 p-4" />
```

## Component Library

The UI package (`packages/ui`) contains reusable React components built with:

- TypeScript for type safety
- Tailwind CSS for styling
- Radix UI for accessible primitives
- CVA for variant management

### Available Components

#### Primitives
- `Button` - Interactive button with multiple variants and sizes

More components coming in Phase 2:
- Input, Select, Checkbox, Radio
- Card, Dialog, Dropdown
- Table, Tabs, Toast

### Using Components

```tsx
import { Button } from '@sprint-radar/ui'

export function MyComponent() {
  return (
    <Button variant="primary" size="lg">
      Click me
    </Button>
  )
}
```

## Storybook Documentation

View all components and their variants in Storybook:

```bash
npm run storybook
```

Visit http://localhost:6006 to see the component documentation.

## Migration Strategy

The migration from Jinja2 templates to React is being done in phases:

### Phase 1: Foundation ✅
- [x] Monorepo structure
- [x] Design tokens package
- [x] UI component library setup
- [x] Next.js application
- [x] Storybook documentation

### Phase 2: Core Components (Next)
- [ ] Complete primitive components
- [ ] Chart component wrappers
- [ ] Layout components

### Phase 3: API Integration
- [ ] Python backend API client
- [ ] Authentication flow
- [ ] Data fetching hooks

### Phase 4: Report Migration
- [ ] Migrate first report to Next.js
- [ ] Implement SSR for PDF export
- [ ] Progressive migration of other reports

### Phase 5: Completion
- [ ] Deprecate Jinja2 templates
- [ ] Full cutover to React
- [ ] Performance optimization

## Development Workflow

### Adding a New Component

1. Create component in `packages/ui/src/primitives/ComponentName/`
2. Export from `packages/ui/src/index.tsx`
3. Add Storybook story
4. Document usage

### Working with Design Tokens

1. Edit `packages/design-tokens/tokens.json`
2. Run `npm run build` in design-tokens package
3. Tokens are automatically available in Tailwind

### PDF Export

The Next.js app supports server-side PDF generation:

```tsx
// app/api/export/pdf/route.ts
const response = await fetch('/api/export/pdf', {
  method: 'POST',
  body: JSON.stringify({ reportId }),
})
```

## Tech Stack

- **Frontend Framework**: React 18 + Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + CSS Variables
- **Component Primitives**: Radix UI
- **Build System**: Turborepo
- **Documentation**: Storybook 7
- **Backend**: Python + FastAPI (existing)

## Next Steps

To continue development:

1. Install dependencies: `npm install`
2. Start the development server: `npm run dev`
3. Visit http://localhost:3000 for the Next.js app
4. Visit http://localhost:6006 for Storybook

The Python backend remains unchanged and can be run separately.

## Design System Philosophy

For detailed design system philosophy, brand guidelines, and visual patterns, see [packages/design-tokens/DESIGN_SYSTEM.md](packages/design-tokens/DESIGN_SYSTEM.md).

## SSR Best Practices

### Component Export Pattern

All components MUST use `React.forwardRef` to ensure proper bundling and SSR compatibility:

```typescript
// ✅ CORRECT - This pattern ensures components are included in the bundle
const MyComponent = React.forwardRef<HTMLDivElement, MyComponentProps>(
  ({ className, ...props }, ref) => {
    return (
      <div ref={ref} className={cn('base-styles', className)} {...props}>
        {/* Component content */}
      </div>
    )
  }
)
MyComponent.displayName = 'MyComponent'

export { MyComponent }
```

```typescript
// ❌ INCORRECT - This pattern may cause components to be tree-shaken
export const MyComponent: React.FC<MyComponentProps> = ({ ...props }) => {
  return <div {...props} />
}
```

### Key Requirements for SSR

1. **Use `React.forwardRef`**: This ensures proper ref forwarding and prevents tree-shaking issues during build
2. **Set `displayName`**: Required for debugging and React DevTools
3. **Export with destructuring**: Use `export { ComponentName }` pattern
4. **Extend HTML attributes**: Components should extend appropriate HTML element attributes
5. **Use proper imports**: Import React as `import * as React from 'react'`

### SSR Rendering Pipeline

The report builder uses `renderToStaticMarkup` from React DOM Server. Components must:

1. Be pure and deterministic (no side effects during render)
2. Not rely on browser-specific APIs during initial render
3. Use CSS classes that work server-side (Tailwind CSS)
4. Properly handle hydration without mismatches

### Testing SSR Compatibility

To verify a component works with SSR:

1. Build the UI library: `npm run build`
2. Check that the component appears in `dist/index.js`
3. Verify TypeScript definitions are in `dist/index.d.ts`
4. Test that the component renders correctly in SSR context
5. Ensure no hydration errors in the browser console

### Common SSR Issues and Solutions

1. **Component not in bundle**: Convert from `React.FC` to `React.forwardRef`
2. **Hydration mismatches**: Ensure deterministic rendering, avoid random values
3. **Missing styles**: Verify Tailwind classes are included in CSS output
4. **Runtime errors**: Check for browser API usage (window, document) during SSR

### Build Configuration

The UI library uses tsup with the following configuration:
- Entry: `src/index.tsx`
- Formats: CommonJS and ESM
- External dependencies: React and React DOM
- TypeScript declarations: Generated automatically
- Clean build: Removes previous dist before building