## Project Overview

This is a high-performance agile project analytics tool for enterprise forecasting and agile development health assessments. It analyzes historical velocity data from various data sources (Linear and Linear CSVs, Jira REST API, etc) and provides several analytical charts, as well as monte carlo simulations for completion estimates.


## Default Behavior
- By default, when asked to generate a report, assume the request is to report against the Jira API using the `-f jira-api://` flag unless a specific source CSV file is specified


## Architectural Documentation

- Any architectural change to the system should be documented in a LADR document in the `docs/architecture` directory of the project. The LADR status should be "ACCEPTED", and it should be simple to understand, and designed for the entire `docs/architecture` directory to provide a historical record of major architectural decisions and their rationale.

## Development Workflow

- Your workflow for each development task should be: plan -> design failing tests -> implement -> flesh out tests -> lint -> ensure the entire test suit passes -> update documentation as appropriate -> commit/push.
- When starting work on a new feature, refactor, architectural change, etc, do your work in a new, short-lived branch. As soon as that work completes, merge that branch into the main branch (we follow Trunk Based Development).

## React Component SSR Guidelines

CRITICAL: All React components MUST use `React.forwardRef` pattern for SSR compatibility:

```typescript
// ALWAYS use this pattern for components
import * as React from 'react'

const ComponentName = React.forwardRef<HTMLDivElement, ComponentProps>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn('base-styles', className)} {...props} />
  }
)
ComponentName.displayName = 'ComponentName'

export { ComponentName }
```

NEVER use `React.FC` as it causes tree-shaking issues with tsup build tool.

## CLI Guidelines

- When generating reports from the CLI, ensure they always get saved in the `reports` directory.
- Any report you generate should go in the reports/ directory. Documentation should go in the docs/ directory. Keep the top level directory of the project well organized and clean.

## Project Guidelines

- When planning new work, ensure you understand the documentation in the ./README.md and ARCHITECTURE.md so you don't deviate from our mission or architectural guidelines.

## Dependency Management

- Whenever installing new dependencies in the supply chain, ensure you properly .gitignore any artifacts that don't belong in the repo, like `node_modules`, etc.