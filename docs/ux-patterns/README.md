# UX Patterns Documentation

This directory contains documented UX patterns, workarounds, and implementation details for user interface behaviors in Sprint Radar.

## What Are UX Patterns?

UX patterns document specific solutions to recurring user experience challenges. Unlike architectural decisions (LADRs), these focus on:
- Visual behavior and animations
- Interaction patterns
- UI workarounds for library limitations
- Cross-browser compatibility fixes
- Performance optimizations for perceived speed

## Pattern Format

Each pattern follows this structure:

```markdown
# UX Pattern: [Pattern Name]

**Pattern ID**: UXP-XXX  
**Category**: [Category]  
**Status**: Active|Deprecated|Experimental  
**Created**: YYYY-MM-DD  

## Problem Statement
[Clear description of the UX problem]

## User Impact
- **Severity**: Critical|High|Medium|Low
- **Frequency**: How often users encounter this
- **User Feedback**: Actual quotes or paraphrased feedback

## Solution Pattern
[High-level approach]

## Implementation Details
[Technical implementation with code examples]

## Testing Checklist
[How to verify the pattern works]

## Alternatives Considered
[Other approaches that were evaluated]

## Related Patterns
[Links to related UX patterns]

## Maintenance Notes
[When and how to review/update this pattern]
```

## Pattern Categories

### Data Visualization
Patterns for charts, graphs, and data display
- UXP-001: Chart Transition Smoothing

### Navigation & Routing
Patterns for moving between views and states

### Loading & Performance
Patterns for perceived performance and loading states

### Error Handling
Patterns for error states and recovery

### Responsive Design
Patterns for different screen sizes and devices

### Accessibility
Patterns for keyboard navigation and screen readers

## When to Create a New Pattern

Document a new UX pattern when:
1. You implement a non-obvious solution to a UX problem
2. The solution involves multiple files or components
3. Future developers need to understand why it works this way
4. The pattern might be reused elsewhere
5. There's risk of regression without documentation

## How to Contribute

1. Create a new file: `docs/ux-patterns/XXX-pattern-name.md`
2. Follow the pattern format above
3. Include code examples and visual examples where helpful
4. Add inline code comments referencing the pattern
5. Update this README with the new pattern

## Pattern Status Definitions

- **Active**: Currently in use and maintained
- **Deprecated**: No longer recommended but still in codebase
- **Experimental**: Under evaluation, may change

## Related Documentation

- `/docs/UI_HEURISTICS.md` - Comprehensive list of all UI workarounds
- `/DESIGN_SYSTEM.md` - Design system principles and components
- `/docs/architecture/` - Architectural decisions (LADRs)
- `/packages/ui/` - UI component library

## Quick Reference

| Pattern ID | Name | Category | Status |
|------------|------|----------|---------|
| UXP-001 | Chart Transition Smoothing | Data Visualization | Active |

## Review Schedule

UX patterns should be reviewed:
- When upgrading major dependencies (Plotly, React, etc.)
- When browser capabilities change significantly
- During annual documentation reviews
- When patterns cause maintenance burden