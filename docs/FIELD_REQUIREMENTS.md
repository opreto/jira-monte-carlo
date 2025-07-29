# Field Requirements Documentation

This document outlines the required and optional fields for each data source to enable various reports and visualizations in the Monte Carlo forecasting tool.

## Table of Contents
- [Core Fields](#core-fields)
- [Report Requirements](#report-requirements)
- [Data Source Field Mappings](#data-source-field-mappings)
- [Adding New Data Sources](#adding-new-data-sources)

## Core Fields

These are the fundamental fields used across the application:

| Field | Description | Example | Used For |
|-------|-------------|---------|----------|
| **key** | Unique identifier for the issue | PROJ-123 | Issue tracking, deduplication |
| **summary** | Brief description of the issue | "Fix login bug" | Display, reporting |
| **status** | Current state of the issue | "In Progress" | Workflow analysis, WIP tracking |
| **issue_type** | Category of work item | "Story", "Bug", "Task" | Filtering, categorization |
| **created** | When the issue was created | 2024-01-15 | Aging analysis, cycle time |
| **updated** | Last modification date | 2024-02-20 | Staleness detection |
| **resolved** | When the issue was completed | 2024-02-25 | Cycle time, throughput |
| **story_points** | Estimated effort | 5 | Velocity calculation, forecasting |
| **assignee** | Person responsible | "john.doe" | WIP by person, workload |
| **labels** | Tags or markers | ["blocked", "backend"] | Blocked item detection |
| **sprint** | Sprint/iteration assignment | "Sprint 23" | Sprint health, velocity |
| **time_estimate** | Original time estimate | 8h | Estimation accuracy |
| **time_spent** | Actual time spent | 12h | Estimation accuracy |

## Report Requirements

### 1. Monte Carlo Forecast
**Required:**
- `status` - To determine done vs remaining work
- `story_points` OR `time_estimate` OR issue count - For velocity calculation
- Historical completed work (done items with `sprint` or `resolved` date)

**Optional:**
- `sprint` - For sprint-based velocity
- `resolved` - For date-based velocity

### 2. Velocity Trend
**Required:**
- Same as Monte Carlo Forecast
- Either `sprint` with completed dates OR `resolved` dates

### 3. Work In Progress (WIP)
**Required:**
- `status` - To categorize work states
- `created` - To calculate item age

**Optional:**
- `assignee` - For WIP by person
- `story_points` - For weighted WIP

### 4. Aging Work Items
**Required:**
- `status` - To filter non-done items
- `created` - To calculate age

**Optional:**
- `updated` - For staleness detection
- `assignee` - For assignment analysis
- `story_points` - For weighted aging

### 5. Sprint Health Metrics
**Required:**
- `sprint` - Sprint assignment
- `status` - Completion tracking
- Sprint data with start/end dates

**Optional:**
- `story_points` - For velocity metrics
- `created` - For scope change detection

### 6. Blocked Items
**Required:**
- `status` - To identify blocked states
- `labels` OR blocked-indicating status

**Optional:**
- `created` or `updated` - For blocked duration
- `assignee` - For assignment tracking

### 7. Cycle Time Distribution
**Required:**
- `created` - Start time
- `resolved` - End time
- `status` - To filter completed items

**Degraded Mode (if missing `resolved`):**
- Uses `created` to `updated` for in-progress items

### 8. Throughput Trend
**Required:**
- `resolved` - Completion dates
- `status` - To identify done items

### 9. Cumulative Flow Diagram
**Required:**
- `created` - Entry into system
- `updated` - State changes
- `status` - Current state

### 10. Sprint Predictability
**Required:**
- `sprint` - Sprint assignment
- Sprint data with commitments
- `story_points` OR issue count

### 11. Estimation Accuracy
**Required:**
- `time_estimate` - Original estimate
- `time_spent` - Actual time
- `status` - To filter completed work

## Data Source Field Mappings

### JIRA CSV Export

Default field mappings:
```python
{
    "key": "Issue key",
    "summary": "Summary",
    "status": "Status",
    "issue_type": "Issue Type",
    "created": "Created",
    "updated": "Updated",
    "resolved": "Resolved",
    "story_points": "Story Points" | "Story point estimate" | "Custom field (Story Points)",
    "assignee": "Assignee",
    "labels": "Labels",
    "sprint": "Sprint",
    "time_estimate": "Original Estimate",
    "time_spent": "Time Spent"
}
```

### Linear CSV Export

Default field mappings:
```python
{
    "key": "ID",
    "summary": "Title",
    "status": "Status",
    "issue_type": "Type" | "Labels",  # Linear uses labels for types
    "created": "Created",
    "updated": "Updated",
    "resolved": "Completed" | "Done",  # Varies by export
    "story_points": "Estimate",
    "assignee": "Assignee",
    "labels": "Labels",
    "sprint": "Cycle Name",
    "time_estimate": None,  # Not typically available
    "time_spent": None      # Not typically available
}
```

### Custom CSV

Users can map fields using CLI options:
```bash
python -m src.presentation.cli \
    --key-field "Ticket ID" \
    --summary-field "Description" \
    --status-field "State" \
    --story-points-field "Points" \
    ...
```

## Adding New Data Sources

When adding support for a new data source:

1. **Create a data source class** in `src/infrastructure/`:
   ```python
   class NewSourceDataSource(DataSource):
       def get_field_mapping(self) -> Dict[str, str]:
           return {
               "key": "new_source_id_field",
               "summary": "new_source_title_field",
               # ... map all available fields
           }
   ```

2. **Update this documentation** with:
   - Default field mappings for the new source
   - Any source-specific considerations
   - Example CLI usage

3. **Test capability detection** to ensure reports gracefully handle missing fields

4. **Add integration tests** verifying which reports work with typical exports from that source

## Field Availability Matrix

| Data Source | Key | Summary | Status | Created | Updated | Resolved | Points | Assignee | Labels | Sprint |
|-------------|-----|---------|--------|---------|---------|----------|--------|----------|--------|--------|
| JIRA CSV | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ | ✓ |
| Linear CSV | ✓ | ✓ | ✓ | ✓ | ✓ | ✓* | ✓ | ✓ | ✓ | ✓** |
| GitHub Issues | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✗ |
| Trello | ✓ | ✓ | ✓*** | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✗ |

\* May be missing for in-progress items  
\** Called "Cycle" in Linear  
\*** Via list names

## Best Practices

1. **Always export all available fields** when generating CSV exports
2. **Include historical data** (at least 3-6 months) for accurate velocity calculations
3. **Ensure consistent status names** across your workflow
4. **Use standard date formats** (ISO 8601 preferred)
5. **Include sprint/cycle information** when available for better velocity tracking

## Troubleshooting

### "Report X is NOT available"
Check the capability analyzer output to see which fields are missing:
```
Report Aging Work Items is NOT available. Missing fields: {<DataRequirement.CREATED_DATE: 'created_date'>}
```

### Velocity showing as 0
- Ensure you have completed items with either:
  - `sprint` field and done status
  - `resolved` dates for done items
- Check that `story_points` field is properly mapped

### Linear CSV has no sprints/cycles
Linear exports may not include cycle data. Workarounds:
1. **Create synthetic velocity data**: Group completed items by month using the `Completed` date
2. **Use the Linear data source directly**: It will create monthly "sprints" from completed work
3. **Add sprint data manually**: Enhance the CSV with sprint assignments before import

Example script to add synthetic sprint data:
```python
# Group completed items by month and assign sprint names
df["Sprint"] = pd.to_datetime(df["Completed"]).dt.to_period("M").astype(str)
# Convert T-shirt size estimates to story points
size_map = {"XS": 1, "S": 2, "M": 3, "L": 5, "XL": 8, "XXL": 13}
df["Story Points"] = df["Estimate"].map(size_map).fillna(3)
```

### Process Health Score is low
Review the health score breakdown in the report for specific issues:
- Missing date fields disable aging analysis
- No sprint data disables sprint health metrics
- Missing labels prevents blocked item detection