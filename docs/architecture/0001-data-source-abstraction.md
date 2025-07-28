# LADR-0001: Data Source Abstraction

Date: 2025-07-27
Status: ACCEPTED

## Context

The Monte Carlo simulation tool was initially built specifically for Jira CSV exports. As the tool gained adoption, users requested support for other project management tools like Linear, Azure DevOps, and GitHub Projects. Each tool has its own export format with different field names, data structures, and concepts (e.g., Jira has "Sprints" while Linear has "Cycles").

## Decision

We will implement a data source abstraction layer that:

1. Defines a common `DataSource` interface that all data sources must implement
2. Uses a factory pattern to create appropriate data source instances
3. Provides auto-detection of file formats based on CSV headers
4. Maps tool-specific concepts to our domain model (Issues and Sprints)

### Architecture

```
Domain Layer:
├── DataSource (interface)
├── DataSourceFactory (interface)
├── DataSourceType (enum)
└── FieldMapping (value object)

Infrastructure Layer:
├── JiraCSVDataSource
├── LinearCSVDataSource
├── DefaultDataSourceFactory
└── [Future: AzureDevOpsDataSource, etc.]

Application Layer:
├── ImportDataUseCase
└── AnalyzeDataSourceUseCase
```

## Consequences

### Positive

- **Extensibility**: New data sources can be added without modifying existing code
- **Auto-detection**: Users don't need to specify the format explicitly
- **Consistent interface**: All data sources provide the same domain entities (Issues, Sprints)
- **Format-specific handling**: Each data source can handle its unique aspects (e.g., Linear's T-shirt sizing)
- **Multi-format support**: Can process files from different tools in the same session

### Negative

- **Increased complexity**: Additional abstraction layer to maintain
- **Mapping overhead**: Each data source needs to map its fields to our domain model
- **Testing burden**: Each new data source requires comprehensive tests

### Neutral

- **Synthetic data creation**: When tools don't provide sprint/cycle data, we create synthetic monthly sprints
- **Field mapping flexibility**: Users can override default field mappings if needed

## Implementation Notes

1. **Linear CSV Support**: First implementation maps Linear's cycles to sprints, handles T-shirt size estimates, and creates synthetic monthly sprints when no cycle data exists

2. **Auto-detection**: Analyzes CSV headers for tool-specific indicators (e.g., "Issue key" for Jira, "ID" + "Cycle" for Linear)

3. **Backward compatibility**: Existing Jira CSV processing continues to work unchanged

## Future Considerations

- API integrations could implement the same `DataSource` interface
- Support for Excel files with similar abstraction
- Plugin architecture for community-contributed data sources