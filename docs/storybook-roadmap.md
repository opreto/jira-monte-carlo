# Storybook Integration Roadmap

## Current Status
- ✅ Storybook builds and runs without errors
- ✅ Fixed import errors in Chart component
- ✅ Configured Tailwind CSS v4 with proper @theme syntax
- ✅ Added CSS variables for design tokens
- ✅ Fixed Plotly chart animation errors in reports

## Outstanding Issues
1. **Component Styling** - Components appear unstyled or don't match report styling
2. **Story Coverage** - Not all design system components have stories
3. **Maintenance Workflow** - No automated process to keep Storybook in sync

## Roadmap

### Phase 1: Component Styling (High Priority)
- [ ] Audit all components to ensure they use design system classes correctly
- [ ] Verify CSS variables are being applied in Storybook context
- [ ] Create a base decorator that applies global styles to all stories
- [ ] Test dark mode switching in Storybook
- [ ] Ensure Plotly charts render correctly in Storybook

### Phase 2: Story Coverage (High Priority)
- [ ] Create stories for all components in packages/ui/src/components:
  - [ ] Basic components (Button, Input, Select, etc.)
  - [ ] Layout components (Card, Header, etc.)
  - [ ] Data display (Table, MetricCard, etc.)
  - [ ] Chart components with Plotly integration
  - [ ] Complex components (MLTooltip, ProcessHealthBreakdown)
- [ ] Add documentation for each component
- [ ] Include all component variants and states
- [ ] Add interaction examples where applicable

### Phase 3: Visual Consistency (Medium Priority)
- [ ] Compare component rendering between Storybook and actual reports
- [ ] Create visual regression tests
- [ ] Document any intentional differences
- [ ] Ensure responsive behavior matches across contexts

### Phase 4: Automated Maintenance (Medium Priority)
- [ ] Create a CI check that ensures all exported components have stories
- [ ] Add automated visual regression testing
- [ ] Create a script to generate story templates for new components
- [ ] Add Storybook build to the main build process
- [ ] Create documentation on maintaining Storybook

## Technical Considerations

### CSS Loading
- Storybook uses its own Tailwind build process
- Design tokens are loaded from @sprint-radar/design-tokens
- Need to ensure both Tailwind utilities and CSS variables are available

### Component Dependencies
- Some components depend on Plotly.js (Chart component)
- Some use Radix UI primitives
- Need to ensure all dependencies are properly loaded in Storybook

### Data Mocking
- Many components expect specific data structures
- Need to create realistic mock data for stories
- Consider using MSW for API mocking if needed

## Success Criteria
1. All design system components have comprehensive stories
2. Components look identical in Storybook and production reports
3. New components automatically get story templates
4. Storybook serves as the primary component documentation
5. Visual regression tests catch styling changes