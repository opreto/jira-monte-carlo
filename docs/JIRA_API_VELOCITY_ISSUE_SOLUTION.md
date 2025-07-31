# Jira API Velocity Issue - Solution Guide

## Problem Summary

When running `sprint-radar -f jira-api://`, you're getting:
```
ValueError: Invalid inputs for forecasting: Average velocity must be positive
```

### Root Cause
- Your JQL filter (`statusCategory != Done AND labels = mvp`) returns only incomplete "mvp" items
- There are NO completed items with the "mvp" label
- The system can't calculate velocity because it has no historical completed work
- However, your project (PARA) has plenty of completed work without the "mvp" label

## Immediate Solutions

### Solution 1: Use Project-Wide Data (Quickest)
```bash
# Temporarily use all project data
export JIRA_JQL_FILTER="project = PARA"
sprint-radar -f jira-api:// -o reports/forecast.html
```

This will:
- Calculate velocity from ALL completed project work
- Forecast ALL remaining project work (not just mvp items)

### Solution 2: Use Workaround Script
```bash
# This script temporarily modifies the JQL for you
python scripts/jira_velocity_workaround.py -o reports/forecast.html
```

### Solution 3: Advanced Dual-JQL Script
```bash
# This script implements proper dual-query logic
python scripts/dual_jql_forecast.py \
  --backlog-jql "statusCategory != Done AND labels = mvp" \
  --velocity-project PARA \
  -o forecast.json
```

## Understanding the Issue

The current Sprint Radar implementation uses a single JQL query for both:
1. **Velocity Calculation**: Needs completed work to calculate historical velocity
2. **Backlog Forecasting**: The work you want to forecast

Your scenario requires:
- Velocity from ALL completed project work (37 story points across 14 issues)
- Forecasting only the "mvp" labeled items (40 issues, 158 story points)

## Long-term Solution

We need to implement dual JQL support in Sprint Radar:
```bash
# Future implementation
sprint-radar -f jira-api:// \
  --jql-filter "labels = mvp AND statusCategory != Done" \
  --velocity-jql "project = PARA AND statusCategory = Done" \
  -o reports/mvp-forecast.html
```

## Installation Issue (Separate)

If you're getting `ModuleNotFoundError: No module named 'src'`:
```bash
cd ~/projects/opreto/internal/jira-monte-carlo
source .venv/bin/activate
pip install -e .
```

## Next Steps

1. Use one of the workaround solutions above for immediate needs
2. The dual JQL feature will be implemented in the main codebase
3. For now, the workaround scripts provide the functionality you need