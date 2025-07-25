# Architecture Documentation

## Overview

This project follows **Clean Architecture** principles (also known as Hexagonal Architecture or Ports and Adapters) to create a maintainable, testable, and flexible system for Monte Carlo simulations of Jira project data.

## Clean Architecture Principles

The architecture is organized in concentric layers, with dependencies pointing inward:

```mermaid
graph TB
    subgraph "External World"
        CLI[CLI Interface]
        CSV[CSV Files]
        HTML[HTML Reports]
        FS[File System]
    end
    
    subgraph "Presentation Layer"
        CLIHandler[CLI Handler]
        ReportGen[Report Generator]
    end
    
    subgraph "Infrastructure Layer"
        CSVParser[CSV Parser]
        CSVAnalyzer[CSV Analyzer]
        FileRepo[File Repositories]
    end
    
    subgraph "Application Layer"
        UC1[Calculate Velocity Use Case]
        UC2[Run Monte Carlo Use Case]
        UC3[Analyze CSV Structure Use Case]
        UC4[Analyze Velocity Use Case]
    end
    
    subgraph "Domain Layer"
        E1[Issue Entity]
        E2[Sprint Entity]
        E3[SimulationResult Entity]
        VO1[FieldMapping Value Object]
        VO2[VelocityMetrics Value Object]
        R1[Repository Interfaces]
    end
    
    CLI --> CLIHandler
    CLIHandler --> UC1
    CLIHandler --> UC2
    CLIHandler --> UC3
    CLIHandler --> UC4
    
    UC1 --> R1
    UC2 --> R1
    UC3 --> E1
    UC4 --> VO2
    
    CSVParser --> E1
    CSVAnalyzer --> E2
    FileRepo -.-> R1
    
    ReportGen --> E3
    HTML --> ReportGen
    CSV --> CSVParser
    FS --> FileRepo
```

### Key Principles

1. **Dependency Rule**: Dependencies only point inward. Inner layers know nothing about outer layers.
2. **Domain Independence**: Business logic doesn't depend on frameworks, databases, or UI.
3. **Testability**: Business rules can be tested without external dependencies.
4. **Flexibility**: External components (UI, database, frameworks) can be swapped without affecting business logic.

## Layer Breakdown

### 1. Domain Layer (Core Business Logic)

The innermost layer contains enterprise business rules and domain models.

```mermaid
classDiagram
    class Issue {
        +key: str
        +summary: str
        +status: str
        +story_points: float
        +cycle_time: float
        +age: float
    }
    
    class Sprint {
        +name: str
        +start_date: datetime
        +end_date: datetime
        +completed_points: float
        +velocity: float
        +duration_days: int
    }
    
    class SimulationResult {
        +percentiles: Dict[float, float]
        +mean_completion_date: datetime
        +completion_sprints: List[int]
        +probability_distribution: List[float]
    }
    
    class VelocityMetrics {
        +average: float
        +median: float
        +std_dev: float
        +min_value: float
        +max_value: float
        +trend: float
    }
    
    class IssueRepository {
        <<interface>>
        +save(issue: Issue)
        +get_by_key(key: str): Issue
        +get_by_status(status: str): List[Issue]
        +get_all(): List[Issue]
    }
    
    class SprintRepository {
        <<interface>>
        +save(sprint: Sprint)
        +get_by_name(name: str): Sprint
        +get_recent(limit: int): List[Sprint]
        +get_all(): List[Sprint]
    }
```

**Key Components:**
- **Entities**: Core business objects with identity (Issue, Sprint, Team)
- **Value Objects**: Immutable objects without identity (VelocityMetrics, FieldMapping)
- **Repository Interfaces**: Abstractions for data access

### 2. Application Layer (Use Cases)

Contains application-specific business rules and orchestrates the flow of data.

```mermaid
graph LR
    subgraph "Use Cases"
        CV[CalculateVelocityUseCase]
        MC[RunMonteCarloSimulationUseCase]
        RW[CalculateRemainingWorkUseCase]
        HD[AnalyzeHistoricalDataUseCase]
        CS[AnalyzeCSVStructureUseCase]
        AV[AnalyzeVelocityUseCase]
    end
    
    subgraph "Domain"
        IR[IssueRepository]
        SR[SprintRepository]
        VM[VelocityMetrics]
        SR2[SimulationResult]
    end
    
    CV --> IR
    CV --> SR
    CV --> VM
    
    MC --> SR2
    MC --> VM
    
    RW --> IR
    
    HD --> IR
    
    CS --> IR
    
    AV --> SR
    AV --> VM
```

**Use Case Examples:**

```python
class CalculateVelocityUseCase:
    """Calculates team velocity from historical sprint data"""
    def execute(self, lookback_sprints: int) -> VelocityMetrics:
        # Orchestrates domain objects to calculate velocity
        # No knowledge of CSV files, databases, or UI

class RunMonteCarloSimulationUseCase:
    """Runs Monte Carlo simulations based on velocity metrics"""
    def execute(self, remaining_work: float, 
                velocity_metrics: VelocityMetrics,
                config: SimulationConfig) -> SimulationResult:
        # Pure business logic for running simulations
```

### 3. Infrastructure Layer (External Interfaces)

Implements the interfaces defined in the domain layer and handles external concerns.

```mermaid
classDiagram
    class JiraCSVParser {
        +parse_file(file_path): List[Issue]
        +parse_dataframe(df): List[Issue]
        -_parse_date(date_str): datetime
        -_parse_sprint_field(value): List[str]
    }
    
    class SmartCSVParser {
        +parse_file(file_path): DataFrame
        -_apply_aggregations(df): DataFrame
        -_aggregate_last(df, columns): Series
        -_aggregate_concat(df, columns): Series
    }
    
    class InMemoryIssueRepository {
        -_issues: Dict[str, Issue]
        +save(issue: Issue)
        +get_by_key(key: str): Issue
        +get_by_status(status: str): List[Issue]
    }
    
    class FileConfigRepository {
        -_config_dir: Path
        +save_field_mapping(mapping: FieldMapping)
        +load_field_mapping(): FieldMapping
        +save_status_mapping(mapping: Dict)
        +load_status_mapping(): Dict
    }
    
    IssueRepository <|.. InMemoryIssueRepository
    ConfigRepository <|.. FileConfigRepository
```

**Key Features:**
- **CSV Parsing**: Polars-based high-performance parsing with column aggregation
- **Repository Implementations**: In-memory storage with efficient lookups
- **Configuration Persistence**: JSON-based configuration storage

### 4. Presentation Layer (User Interface)

Handles user interaction and report generation.

```mermaid
graph TB
    subgraph "CLI Module"
        CLI[Click CLI]
        IV[Input Validation]
        OP[Output Formatting]
    end
    
    subgraph "Report Generator"
        RG[HTMLReportGenerator]
        PC[Probability Chart]
        VT[Velocity Trend]
        FT[Forecast Timeline]
        CI[Confidence Intervals]
    end
    
    subgraph "Application Layer"
        UC[Use Cases]
    end
    
    CLI --> IV
    IV --> UC
    UC --> OP
    OP --> CLI
    
    UC --> RG
    RG --> PC
    RG --> VT
    RG --> FT
    RG --> CI
```

**Responsibilities:**
- Command-line argument parsing and validation
- Interactive configuration
- Progress display with Rich library
- HTML report generation with Plotly charts

## Data Flow

Here's how data flows through the system during a typical simulation:

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant UseCase
    participant Repository
    participant Domain
    participant Infrastructure
    
    User->>CLI: Run simulation command
    CLI->>CLI: Parse arguments
    CLI->>Infrastructure: Load CSV file
    Infrastructure->>Domain: Create Issue entities
    Domain->>Repository: Store issues
    
    CLI->>UseCase: Calculate velocity
    UseCase->>Repository: Get historical data
    Repository->>UseCase: Return sprints/issues
    UseCase->>Domain: Calculate metrics
    Domain->>UseCase: Return VelocityMetrics
    
    CLI->>UseCase: Run Monte Carlo
    UseCase->>Domain: Simulate with metrics
    Domain->>UseCase: Return SimulationResult
    
    UseCase->>CLI: Return results
    CLI->>Infrastructure: Generate HTML report
    CLI->>User: Display summary
```

## Key Design Patterns

### 1. Repository Pattern
Abstracts data access behind interfaces, allowing different implementations without affecting business logic.

### 2. Use Case Pattern
Encapsulates application-specific business rules, keeping them separate from UI and infrastructure.

### 3. Value Object Pattern
Immutable objects that represent concepts without identity, ensuring data integrity.

### 4. Dependency Injection
Dependencies are injected rather than created, improving testability and flexibility.

## Testing Strategy

The Clean Architecture enables comprehensive testing at each layer:

```mermaid
graph TB
    subgraph "Test Pyramid"
        UT[Unit Tests<br/>Domain & Use Cases]
        IT[Integration Tests<br/>Infrastructure]
        E2E[End-to-End Tests<br/>CLI & Reports]
    end
    
    UT --> IT
    IT --> E2E
    
    style UT fill:#90EE90
    style IT fill:#FFD700
    style E2E fill:#FF6B6B
```

### Unit Tests (Domain & Application)
- Test business logic in isolation
- No external dependencies
- Fast and deterministic
- Focus on behavior, not implementation

### Integration Tests (Infrastructure)
- Test CSV parsing with real file structures
- Test repository implementations
- Verify configuration persistence

### End-to-End Tests (Presentation)
- Test CLI commands
- Verify report generation
- Ensure proper error handling

## Benefits of This Architecture

1. **Testability**: Business logic can be tested without CSV files, databases, or UI
2. **Maintainability**: Clear separation of concerns makes changes easier
3. **Flexibility**: Can easily swap implementations (e.g., database instead of in-memory)
4. **Scalability**: Can add new features without affecting existing code
5. **Team Collaboration**: Clear boundaries enable parallel development

## Future Extensions

The architecture supports these potential enhancements without major refactoring:

- **Different Data Sources**: Add Jira API integration alongside CSV
- **Different Storage**: Replace in-memory with database persistence
- **Different UIs**: Add web interface alongside CLI
- **Different Analytics**: Add new simulation algorithms
- **Different Formats**: Support Excel, JSON, or API inputs