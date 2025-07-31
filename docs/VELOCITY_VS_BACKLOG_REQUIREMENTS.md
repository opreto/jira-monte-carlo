# Velocity vs Backlog Data Requirements

## Problem Statement

When using Sprint Radar with Jira API, we often need to:
1. Calculate velocity from ALL historical completed work (to get accurate team velocity)
2. Forecast only a SUBSET of work (e.g., items with specific labels like "mvp")

Currently, the system uses a single JQL query for both purposes, which causes issues when:
- The filtered backlog (e.g., "mvp" labeled items) has no completed work yet
- We want to use overall team velocity to forecast specific initiatives

## Current Behavior

The system uses the JQL filter from `JIRA_JQL_FILTER` environment variable for both:
- Fetching historical data for velocity calculation
- Fetching backlog items to forecast

This leads to zero velocity errors when the filtered set has no completed items.

## Proposed Solution

### Option 1: Dual JQL Query Support (Recommended)

Introduce two separate JQL queries:
- `JIRA_JQL_FILTER` or `--jql-filter`: For backlog items to forecast
- `JIRA_VELOCITY_JQL` or `--velocity-jql`: For historical velocity calculation

If velocity JQL is not specified, default to using all completed project work.

### Option 2: Automatic Velocity Expansion

When the primary JQL returns no completed work:
1. Automatically expand to search for completed work in the project
2. Use that expanded set for velocity calculation
3. Still use the filtered set for backlog forecasting

### Option 3: Command Line Override

Add a flag like `--use-project-velocity` that forces velocity calculation from all project work regardless of the JQL filter.

## Implementation Considerations

1. **Backwards Compatibility**: Ensure existing workflows continue to work
2. **Caching**: Need separate cache keys for velocity vs backlog data
3. **UI Clarity**: Make it clear which data is used for what purpose
4. **Performance**: Two API calls vs one (minimal impact with caching)

## Example Usage

```bash
# Use project velocity to forecast mvp work
export JIRA_JQL_FILTER="labels = mvp AND statusCategory != Done"
export JIRA_VELOCITY_JQL="project = PARA AND statusCategory = Done"
sprint-radar -f jira-api:// -o reports/mvp-forecast.html

# Or via command line
sprint-radar -f jira-api:// \
  --jql-filter "labels = mvp AND statusCategory != Done" \
  --velocity-jql "project = PARA AND statusCategory = Done" \
  -o reports/mvp-forecast.html
```

## Temporary Workaround

Until this is implemented, users can:
1. Remove label filters to get all project data
2. Manually filter in post-processing
3. Use CSV exports with proper filtering