# Architecture Documentation

## Overview

This project follows **Clean Architecture** principles (also known as Hexagonal Architecture or Ports and Adapters) to create a maintainable, testable, and flexible system for Monte Carlo simulations of Jira project data.

## Clean Architecture Principles

The architecture is organized in concentric layers, with dependencies pointing inward:

```mermaid
%%{init: { 'flowchart': { 'curve': 'basis', 'htmlLabels': false }}}%%
flowchart TB

%% EXTERNAL WORLD
subgraph "External World"
  CLI([CLI Interface])
  CSV[CSV Files]
  HTML[HTML Reports]
  FS[File System]
end

%% PRESENTATION
subgraph "Presentation Layer"
  CLIHandler([CLI Handler])
  ReportGen([Report Generator])
end

%% INFRASTRUCTURE
subgraph "Infrastructure Layer"
  CSVParser([CSV Parser])
  CSVAnalyzer([CSV Analyzer])
  FileRepo([File Repositories])
end

%% APPLICATION
subgraph "Application Layer"
  UC1([Calculate Velocity Use Case])
  UC2([Run Monte Carlo Use Case])
  UC3([Analyze CSV Structure Use Case])
  UC4([Analyze Velocity Use Case])
end

%% DOMAIN
subgraph "Domain Layer"
  E1([Issue Entity])
  E2([Sprint Entity])
  E3([SimulationResult Entity])
  VO1([FieldMapping Value Object])
  VO2([VelocityMetrics Value Object])
  R1([Repository Interfaces])
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

%% LAYER COLOR STYLES (applied directly to nodes for accessibility)
style CLI fill:#ecf2f8,stroke:#2456A3,stroke-width:2px,color:#111
style CSV fill:#ecf2f8,stroke:#2456A3,stroke-width:2px,color:#111
style HTML fill:#ecf2f8,stroke:#2456A3,stroke-width:2px,color:#111
style FS fill:#ecf2f8,stroke:#2456A3,stroke-width:2px,color:#111

style CLIHandler fill:#FFFAD0,stroke:#D1A800,stroke-width:2px,color:#111
style ReportGen fill:#FFFAD0,stroke:#D1A800,stroke-width:2px,color:#111

style CSVParser fill:#B9ECE4,stroke:#33846A,stroke-width:2px,color:#111
style CSVAnalyzer fill:#B9ECE4,stroke:#33846A,stroke-width:2px,color:#111
style FileRepo fill:#CAE6FB,stroke:#2456A3,stroke-width:2px

style UC1 fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
style UC2 fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
style UC3 fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
style UC4 fill:#D7E7FA,stroke:#335CA5,stroke-width:2px

style E1 fill:#FFF,stroke:#222,stroke-width:2px
style E2 fill:#FFF,stroke:#222,stroke-width:2px
style E3 fill:#FFF,stroke:#222,stroke-width:2px
style VO1 fill:#F7EFE3,stroke:#A1793B,stroke-width:2px
style VO2 fill:#F7EFE3,stroke:#A1793B,stroke-width:2px
style R1 fill:#FBE7D4,stroke:#A05121,stroke-width:2px
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
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#fff', 'primaryTextColor': '#111', 'primaryBorderColor': '#222', 'lineColor': '#333', 'secondaryColor': '#f7efe3', 'tertiaryColor': '#fbe7d4', 'background': '#fff' }}}%%
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

    style Issue fill:#FFF,stroke:#222,stroke-width:2px
    style Sprint fill:#FFF,stroke:#222,stroke-width:2px
    style SimulationResult fill:#FFF,stroke:#222,stroke-width:2px
    style VelocityMetrics fill:#F7EFE3,stroke:#A1793B,stroke-width:2px
    style IssueRepository fill:#FBE7D4,stroke:#A05121,stroke-width:2px
    style SprintRepository fill:#FBE7D4,stroke:#A05121,stroke-width:2px
```

**Key Components:**
- **Entities**: Core business objects with identity (Issue, Sprint, Team)
- **Value Objects**: Immutable objects without identity (VelocityMetrics, FieldMapping)
- **Repository Interfaces**: Abstractions for data access

### 2. Application Layer (Use Cases)

Contains application-specific business rules and orchestrates the flow of data.

```mermaid
%%{init: { 'flowchart': { 'curve': 'basis', 'htmlLabels': false }}}%%
flowchart LR
    subgraph UC["Use Cases"]
        CV([CalculateVelocityUseCase])
        MC([RunMonteCarloSimulationUseCase])
        RW([CalculateRemainingWorkUseCase])
        HD([AnalyzeHistoricalDataUseCase])
        CS([AnalyzeCSVStructureUseCase])
        AV([AnalyzeVelocityUseCase])
    end
    
    subgraph Domain
        IR([IssueRepository])
        SR([SprintRepository])
        VM([VelocityMetrics])
        SR2([SimulationResult])
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

    %% Style use cases
    style CV fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
    style MC fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
    style RW fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
    style HD fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
    style CS fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
    style AV fill:#D7E7FA,stroke:#335CA5,stroke-width:2px

    %% Style domain components
    style IR fill:#FBE7D4,stroke:#A05121,stroke-width:2px
    style SR fill:#FBE7D4,stroke:#A05121,stroke-width:2px
    style VM fill:#F7EFE3,stroke:#A1793B,stroke-width:2px
    style SR2 fill:#FFF,stroke:#222,stroke-width:2px
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
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#B9ECE4', 'primaryTextColor': '#111', 'primaryBorderColor': '#33846A', 'lineColor': '#333' }}}%%
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

    style JiraCSVParser fill:#B9ECE4,stroke:#33846A,stroke-width:2px
    style SmartCSVParser fill:#B9ECE4,stroke:#33846A,stroke-width:2px
    style InMemoryIssueRepository fill:#CAE6FB,stroke:#2456A3,stroke-width:2px
    style FileConfigRepository fill:#CAE6FB,stroke:#2456A3,stroke-width:2px
```

**Key Features:**
- **CSV Parsing**: Polars-based high-performance parsing with column aggregation
- **Repository Implementations**: In-memory storage with efficient lookups
- **Configuration Persistence**: JSON-based configuration storage

### 4. Presentation Layer (User Interface)

Handles user interaction and report generation.

```mermaid
%%{init: { 'flowchart': { 'curve': 'basis', 'htmlLabels': false }}}%%
flowchart TB
    subgraph CLIModule["CLI Module"]
        CLI([Click CLI])
        IV([Input Validation])
        OP([Output Formatting])
    end
    
    subgraph ReportGen["Report Generator"]
        RG([HTMLReportGenerator])
        PC([Probability Chart])
        VT([Velocity Trend])
        FT([Forecast Timeline])
        CI([Confidence Intervals])
    end
    
    subgraph AppLayer["Application Layer"]
        UC([Use Cases])
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

    %% Style CLI components
    style CLI fill:#FFFAD0,stroke:#D1A800,stroke-width:2px
    style IV fill:#FFFAD0,stroke:#D1A800,stroke-width:2px
    style OP fill:#FFFAD0,stroke:#D1A800,stroke-width:2px

    %% Style Report components
    style RG fill:#FFFAD0,stroke:#D1A800,stroke-width:2px
    style PC fill:#FFF4B3,stroke:#D1A800,stroke-width:2px
    style VT fill:#FFF4B3,stroke:#D1A800,stroke-width:2px
    style FT fill:#FFF4B3,stroke:#D1A800,stroke-width:2px
    style CI fill:#FFF4B3,stroke:#D1A800,stroke-width:2px

    %% Style Application layer
    style UC fill:#D7E7FA,stroke:#335CA5,stroke-width:2px
```

**Responsibilities:**
- Command-line argument parsing and validation
- Interactive configuration
- Progress display with Rich library
- HTML report generation with Plotly charts

## Data Flow

Here's how data flows through the system during a typical simulation:

```mermaid
%%{init: { 'theme': 'base', 'themeVariables': { 'primaryColor': '#fff', 'primaryTextColor': '#111', 'primaryBorderColor': '#222', 'lineColor': '#333', 'fontFamily': 'Arial', 'fontSize': '14px' }}}%%
sequenceDiagram
    participant User
    participant CLI
    participant UseCase
    participant Repository  
    participant Domain
    participant Infrastructure
    
    User->>CLI: Run simulation command
    activate CLI
    CLI->>CLI: Parse arguments
    CLI->>Infrastructure: Load CSV file
    activate Infrastructure
    Infrastructure->>Domain: Create Issue entities
    activate Domain
    Domain->>Repository: Store issues
    activate Repository
    Repository-->>Domain: Confirm storage
    deactivate Repository
    deactivate Domain
    deactivate Infrastructure
    
    CLI->>UseCase: Calculate velocity
    activate UseCase
    UseCase->>Repository: Get historical data
    activate Repository
    Repository-->>UseCase: Return sprints/issues
    deactivate Repository
    UseCase->>Domain: Calculate metrics
    activate Domain
    Domain-->>UseCase: Return VelocityMetrics
    deactivate Domain
    deactivate UseCase
    
    CLI->>UseCase: Run Monte Carlo
    activate UseCase
    UseCase->>Domain: Simulate with metrics
    activate Domain
    Domain-->>UseCase: Return SimulationResult
    deactivate Domain
    deactivate UseCase
    
    UseCase-->>CLI: Return results
    CLI->>Infrastructure: Generate HTML report
    activate Infrastructure
    Infrastructure-->>CLI: Report generated
    deactivate Infrastructure
    CLI-->>User: Display summary
    deactivate CLI
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
%%{init: { 'flowchart': { 'curve': 'basis', 'htmlLabels': false }}}%%
flowchart TB
    subgraph TestPyramid["Test Pyramid"]
        UT(["Unit Tests<br/>Domain & Use Cases<br/>~70% coverage"])
        IT(["Integration Tests<br/>Infrastructure<br/>~20% coverage"])
        E2E(["End-to-End Tests<br/>CLI & Reports<br/>~10% coverage"])
    end
    
    UT --> IT
    IT --> E2E
    
    %% Style for test levels
    style UT fill:#D4EDDA,stroke:#28A745,stroke-width:2px,color:#155724
    style IT fill:#FFF3CD,stroke:#FFC107,stroke-width:2px,color:#856404
    style E2E fill:#F8D7DA,stroke:#DC3545,stroke-width:2px,color:#721C24
    
    %% Style the container
    style TestPyramid fill:#F8F9FA,stroke:#6C757D,stroke-width:2px,color:#111
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

## Multi-Project Support

The architecture seamlessly supports processing multiple CSV files to generate combined analysis:

### Domain Layer Extensions

```python
@dataclass
class ProjectData:
    """Data from a single CSV file/project"""
    name: str
    source_path: Path
    issues: List[Issue]
    sprints: List[Sprint]
    velocity_metrics: VelocityMetrics
    simulation_result: SimulationResult
    remaining_work: float

@dataclass
class AggregatedMetrics:
    """Aggregated metrics across multiple projects"""
    total_projects: int
    total_issues: int
    total_remaining_work: float
    combined_velocity: float
    confidence_intervals: Dict[float, int]
```

### Application Layer Extensions

The `ProcessMultipleCSVsUseCase` orchestrates:
1. Independent processing of each CSV file
2. Separate repository instances per project
3. Aggregation of metrics across projects
4. Generation of both individual and combined reports

### Presentation Layer Extensions

The `MultiProjectReportGenerator` creates:
- Dashboard with aggregated metrics and comparisons
- Interactive charts for cross-project analysis
- Navigation links to individual project reports
- Workload distribution visualization

This design maintains separation of concerns while enabling powerful multi-project analysis capabilities.

## Styling Architecture

The styling system follows the same clean architecture principles:

### Domain Layer
- **Theme Entity**: Complete theme configuration including colors, typography, spacing
- **Color Value Object**: RGB/hex color representation with conversion methods
- **Typography Value Object**: Font family, size, weight, and spacing
- **ThemeRepository Interface**: Abstraction for theme persistence

### Application Layer
- **StyleService**: Manages theme selection and style generation
- Provides theme management without knowledge of CSS or HTML

### Infrastructure Layer
- **FileThemeRepository**: JSON-based theme storage in `~/.jira-monte-carlo/themes.json`
- Default themes: "default" (purple/modern) and "opreto" (teal/professional)

### Presentation Layer
- **StyleGenerator**: Converts theme objects to CSS
- **Templates**: Clean separation of HTML structure from styling
- Chart color coordination with theme colors

This approach enables:
- Easy addition of new themes
- Consistent styling across all reports
- Theme customization without code changes
- Clean separation of styling concerns

## Future Extensions

The architecture supports these potential enhancements without major refactoring:

- **Different Data Sources**: Add Jira API integration alongside CSV
- **Different Storage**: Replace in-memory with database persistence
- **Different UIs**: Add web interface alongside CLI
- **Different Analytics**: Add new simulation algorithms
- **Different Formats**: Support Excel, JSON, or API inputs
- **Custom Themes**: User-defined themes via configuration
