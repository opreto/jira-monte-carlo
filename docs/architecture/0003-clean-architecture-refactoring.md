# Clean Architecture Refactoring

Date: 2025-07-27
Last Updated: 2025-07-29
Status: IN_PROGRESS

## Context

During architectural review, several violations of Clean Architecture principles and SOLID principles were identified in the codebase. The main issues are:

1. Application layer directly imports from infrastructure and presentation layers
2. Missing abstractions (interfaces) for CSV processing and style generation
3. Direct instantiation of infrastructure components in application services
4. Some modules have too many responsibilities (SRP violation)

## Current State (as of 2025-07-29)

### Progress Made

1. **Domain Interfaces Created**:
   - Repository interfaces (`IssueRepository`, `SprintRepository`, `ConfigRepository`)
   - CSV processing interfaces (`CSVParser`, `CSVAnalyzer`, `SprintExtractor`)
   - Forecasting interfaces (`ForecastingModel`, `ForecastingModelFactory`)
   - Data source abstraction (`DataSource`, `DataSourceFactory`)
   - Style generation interface (`StyleGenerator`)

2. **New Domain Concepts Added**:
   - Process health domain models
   - Reporting capabilities system
   - Multi-project support

3. **Factory Pattern Implemented**:
   - `DefaultDataSourceFactory` for data source management
   - `DefaultModelFactory` for forecasting models

### Remaining Violations

#### Dependency Rule Violations

- `src/application/multi_project_use_cases.py` still imports:
  - `..infrastructure.csv_parser.JiraCSVParser`
  - `..infrastructure.csv_analyzer.SmartCSVParser`
  - `..infrastructure.repositories.EnhancedSprintExtractor`
- `src/application/style_service.py` imports:
  - `..infrastructure.theme_repository.FileThemeRepository`
- `src/application/use_cases.py` imports:
  - `..infrastructure.monte_carlo_model.MonteCarloModel`
- `src/application/multi_project_import.py` imports:
  - `..infrastructure.repositories.InMemoryIssueRepository`

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

1. ✅ Create new interfaces (MOSTLY COMPLETE)
2. 🔄 Create clean versions of services (IN PROGRESS)
3. ✅ Update infrastructure to implement interfaces (MOSTLY COMPLETE)
4. 🔄 Gradually migrate from old to new services (IN PROGRESS)
5. ⏳ Remove old implementations (PENDING)

## Future Architecture Considerations

### Mobile-Friendly Output
- Need responsive chart generation abstraction
- Consider server-side rendering for complex visualizations
- Separate mobile vs desktop template strategies
- Chart library abstraction to support mobile-optimized renderers

### Git Repository Analysis
- New domain concept: `RepositoryAnalyzer` interface
- Infrastructure: Git client abstraction (support multiple providers)
- Domain models for commit data, branch metrics, code ownership
- Integration with existing work type classification

### Opreto-Specific Reporting
- Work type classification system (feature/debt/maintenance/research/DevEx/infra/process)
- LADR tracking and compliance metrics
- Team composition and onboarding analytics
- Definition of Done compliance tracking

### Proposed Domain Extensions

```python
# src/domain/repository_analysis.py
class RepositoryAnalyzer(ABC):
    """Interface for analyzing git repositories"""
    @abstractmethod
    def analyze_commit_patterns(self, repo_path: str) -> CommitAnalysis:
        pass
    
    @abstractmethod
    def calculate_code_ownership(self, repo_path: str) -> OwnershipMap:
        pass

# src/domain/work_classification.py
class WorkClassifier(ABC):
    """Interface for classifying work items by type"""
    @abstractmethod
    def classify(self, issue: Issue) -> WorkType:
        pass

# src/domain/responsive_output.py
class ResponsiveRenderer(ABC):
    """Interface for device-adaptive rendering"""
    @abstractmethod
    def render(self, chart_data: ChartData, device_type: DeviceType) -> str:
        pass
```

## Consequences

### Positive

- Proper separation of concerns
- Better testability
- Easier to add new data sources or output formats
- Follows industry best practices
- Clear extension points for future features

### Negative

- Initial refactoring effort
- Need to update existing code
- Slightly more complex initialization
- Some technical debt from partial implementation

## Next Steps

1. **Immediate (Sprint 1)**:
   - Complete migration of remaining application layer violations
   - Create factory for CSV processing components
   - Update CLI to use dependency injection consistently

2. **Short-term (Sprint 2-3)**:
   - Add responsive rendering abstraction for mobile support
   - Design repository analysis domain model
   - Implement work classification system

3. **Medium-term (Sprint 4-5)**:
   - Full git integration architecture
   - Advanced reporting plugin system
   - Performance optimization for large datasets

## Architecture Principles Going Forward

1. **Plugin Architecture**: All new features should be pluggable
2. **Mobile-First**: Consider responsive design in all new components
3. **Analytics-Ready**: Domain models should support future ML/AI insights
4. **Opreto-Aligned**: Architecture should reflect Opreto's engineering practices

## Status

IN_PROGRESS - Core interfaces created, migration ongoing
