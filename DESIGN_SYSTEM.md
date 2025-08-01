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