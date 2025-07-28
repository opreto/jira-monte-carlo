# Clean Architecture Refactoring

Date: 2025-07-27
Status: PROPOSED

## Context

During architectural review, several violations of Clean Architecture principles and SOLID principles were identified in the codebase. The main issues are:

1. Application layer directly imports from infrastructure and presentation layers
2. Missing abstractions (interfaces) for CSV processing and style generation
3. Direct instantiation of infrastructure components in application services
4. Some modules have too many responsibilities (SRP violation)

## Current Violations

### Dependency Rule Violations

- `src/application/multi_project_use_cases.py` imports:
  - `..infrastructure.csv_parser.JiraCSVParser`
  - `..infrastructure.csv_analyzer.SmartCSVParser`
- `src/application/style_service.py` imports:
  - `..infrastructure.theme_repository.FileThemeRepository`
  - `..presentation.style_generator.StyleGenerator`
- `src/application/use_cases.py` imports:
  - `..infrastructure.monte_carlo_model.MonteCarloModel`

### SOLID Violations

- **DIP**: Application depends on concrete implementations instead of abstractions
- **SRP**: `csv_analysis.py` (516 lines) handles analysis, extraction, and validation
- **OCP**: Adding new CSV formats requires modifying existing code

## Decision

Refactor the codebase to follow Clean Architecture principles:

1. **Create domain interfaces** for all external dependencies
2. **Use dependency injection** instead of direct instantiation
3. **Move all infrastructure imports** out of application layer
4. **Split large modules** into focused, single-responsibility components

## Implementation

### 1. New Domain Interfaces

```python
# src/domain/csv_processing.py
class CSVParser(ABC):
    """Interface for parsing CSV files"""
    
class CSVAnalyzer(ABC):
    """Interface for analyzing CSV structure"""
    
class SprintExtractor(ABC):
    """Interface for extracting sprint data"""

# src/domain/style_generation.py
class StyleGenerator(ABC):
    """Interface for generating styles from themes"""
```

### 2. Application Layer Factories

```python
# src/application/factories.py
class CSVProcessingFactory:
    """Factory for creating CSV processing components"""
    
class StyleServiceFactory:
    """Factory for creating style service dependencies"""
```

### 3. Refactored Services

```python
# src/application/style_service_clean.py
class CleanStyleService:
    def __init__(self, 
                 theme_repository: ThemeRepository,  # Interface
                 style_generator: StyleGenerator):    # Interface
        # No infrastructure imports!
```

### 4. Dependency Injection in CLI

```python
# Initialize infrastructure
csv_factory = CSVProcessingFactory()
csv_factory.register_parser("jira", JiraCSVParser)
csv_factory.register_analyzer("smart", SmartCSVParser)

# Inject into application layer
parser = csv_factory.create_parser("jira")
use_case = ProcessCSVUseCase(parser)  # Uses interface
```

## Benefits

1. **Testability**: Can mock interfaces for unit testing
2. **Flexibility**: Easy to swap implementations
3. **Maintainability**: Clear separation of concerns
4. **Extensibility**: New formats/implementations without changing core logic

## Migration Plan

1. Create new interfaces (DONE)
2. Create clean versions of services
3. Update infrastructure to implement interfaces
4. Gradually migrate from old to new services
5. Remove old implementations

## Consequences

### Positive

- Proper separation of concerns
- Better testability
- Easier to add new data sources or output formats
- Follows industry best practices

### Negative

- Initial refactoring effort
- Need to update existing code
- Slightly more complex initialization

## Status

PROPOSED - Ready for implementation
