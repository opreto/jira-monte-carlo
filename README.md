# Monte Carlo Simulation for Agile Projects

A high-performance Monte Carlo simulation tool for agile project forecasting. This tool analyzes historical velocity data from various sources (Jira, Linear, etc.) and uses Monte Carlo simulations to predict project completion dates with confidence intervals.

## Features

- **High Performance**: Uses Polars for efficient CSV parsing and batch processing
- **Multi-Source Support**: Import data from Jira CSV, Linear CSV, with extensible architecture for more formats
- **Auto-Detection**: Automatically detects the data source format
- **Smart Column Aggregation**: Automatically handles Jira's duplicate Sprint columns (Sprint, Sprint.1, Sprint.2, etc.)
- **Sprint-Based Forecasting**: Predictions in sprints rather than days for clearer planning
- **Velocity Outlier Detection**: Filters outliers using z-score and time-based analysis
- **Configurable Field Mapping**: Command-line options with sensible defaults to map customizable fields
- **Extensible Forecasting Models**: Pluggable architecture for different statistical models (Monte Carlo, PERT, Linear Regression, etc.)
- **Monte Carlo Simulations**: Run thousands of simulations to predict project completion dates
- **Beautiful HTML Reports**: Visual charts showing probability distributions, velocity trends, and forecasts
- **Sprint Name X-Axis**: Historical velocity charts use sprint names on X-axis for clarity when dates are unavailable
- **Clean Architecture**: Follows Domain-Driven Design principles for maintainability
- **Sprint Duration Detection**: Automatically detects sprint length from data
- **Multiple Status Support**: Handles custom workflows with configurable status mappings
- **Multi-Project Support**: Process multiple CSV files to generate a combined dashboard with drill-down to individual reports
- **Themeable Reports**: Built-in themes (Opreto and generic) with clean architecture for styling

## Supported Data Sources

- **Jira CSV**: Export from Jira with all issue fields and sprint data
- **Linear CSV**: Export from Linear with cycle and estimate data
- **Extensible**: Clean architecture allows adding new data sources easily

## Installation

### Prerequisites

- Python 3.9 or higher
- UV (for fast dependency management)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd jira-monte-carlo
```

2. Install UV if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create virtual environment and install dependencies:
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Usage

### Basic Usage

Run the Monte Carlo simulation on your project data:

```bash
# Simplest usage - auto-detects format
jira-monte-carlo -f export.csv

# Specify format explicitly
jira-monte-carlo -f linear-export.csv --format linear
jira-monte-carlo -f jira-export.csv --format jira

# Process multiple files (can be different formats)
jira-monte-carlo -f jira-export.csv -f linear-export.csv
```

### Command Line Options

```
Basic Options:
  -f, --csv-file PATH            Path to CSV export (can be specified multiple times) [required]
  -F, --format TEXT              Data source format: auto, jira, or linear (default: auto)
  -n, --num-simulations INT      Number of Monte Carlo simulations (default: 10000)
  -o, --output TEXT              Output HTML report filename (default: test-report.html)
  --theme TEXT                   Visual theme for reports: opreto or generic (default: opreto)
  --analyze-only                 Only run CSV analysis without simulation
  --help                         Show help message and exit

Field Mapping Options (with sensible defaults):
  --key-field TEXT               CSV column for issue key (default: Issue key)
  --summary-field TEXT           CSV column for issue summary (default: Summary)
  --status-field TEXT            CSV column for issue status (default: Status)
  --created-field TEXT           CSV column for created date (default: Created)
  --resolved-field TEXT          CSV column for resolved date (default: Resolved)
  --story-points-field TEXT      CSV column for story points (default: Custom field (Story point estimate))
  --sprint-field TEXT            CSV column for sprint (default: Sprint)

Status Mapping Options:
  --done-statuses TEXT           Comma-separated done statuses (default: Done,Released,Awaiting Release,Closed,Resolved)
  --in-progress-statuses TEXT    Comma-separated in-progress statuses (default: In Progress,Analysis,Ready for QA,In Development,In Review)
  --todo-statuses TEXT           Comma-separated todo statuses (default: To Do,Open,Backlog,Ready)

Analysis Options:
  --velocity-field TEXT          Velocity metric: story_points, time_estimate, or count (default: story_points)
  --lookback-sprints INT         Number of sprints to analyze for velocity (default: 6)
  --max-velocity-age INT         Maximum age of velocity data in days (default: 240)
  --outlier-std-devs FLOAT       Standard deviations for outlier detection (default: 2.0)
  --min-velocity FLOAT           Minimum velocity threshold (default: 10.0)
```

### Multi-Project Analysis

Process multiple CSV files (e.g., different epics or teams) to get a combined view:

```bash
# Process multiple CSV files
uv run python -m src.presentation.cli \
  -f epic1_export.csv \
  -f epic2_export.csv \
  -f epic3_export.csv \
  -o combined_report.html
```

This generates:
- `combined_report.html` - Dashboard with aggregated metrics and comparisons
- `epic1_export_report.html` - Individual report for epic 1
- `epic2_export_report.html` - Individual report for epic 2
- `epic3_export_report.html` - Individual report for epic 3

The dashboard includes:
- Total remaining work across all projects
- Combined team velocity
- Project comparison charts
- Velocity distribution analysis
- Timeline comparisons
- Workload distribution pie chart
- Links to drill down into individual project reports

### Example

```bash
# Simple usage with all defaults (recommended)
uv run python -m src.presentation.cli --csv-file "All Work with Sprints (JIRA).csv"

# Use generic theme instead of default Opreto theme
uv run python -m src.presentation.cli --csv-file data.csv --theme generic

# Override specific options while using other defaults
uv run python -m src.presentation.cli \
  --csv-file data/sprint-data.csv \
  --lookback-sprints 12 \
  --num-simulations 20000

# Custom field mapping for non-standard Jira setup
uv run python -m src.presentation.cli \
  --csv-file jira-export.csv \
  --story-points-field "Story Points" \
  --sprint-field "Sprint Name" \
  --done-statuses "Complete,Deployed"

# Analyze CSV structure only
uv run python -m src.presentation.cli \
  --csv-file jira-export.csv \
  --analyze-only

```

## Architecture

The project follows Clean Architecture principles:

```
src/
├── domain/          # Business logic and entities
│   ├── entities.py      # Core domain models (Issue, Sprint, Team, SimulationResult)
│   ├── value_objects.py # Immutable value objects (FieldMapping, VelocityMetrics)
│   ├── repositories.py  # Repository interfaces
│   ├── analysis.py      # CSV analysis domain models
│   ├── multi_project.py # Multi-project domain models (ProjectData, AggregatedMetrics)
│   ├── styles.py        # Theme and styling domain models
│   ├── forecasting.py   # Statistical model abstraction (ForecastingModel, ForecastResult)
│   └── data_sources.py  # Data source abstraction interfaces
├── application/     # Use cases and business rules
│   ├── use_cases.py     # Core application services
│   ├── csv_analysis.py  # CSV structure analysis and velocity filtering
│   ├── multi_project_use_cases.py  # Multi-CSV processing orchestration
│   ├── style_service.py # Theme and styling management service
│   ├── forecasting_use_cases.py  # Forecasting model orchestration
│   └── import_data.py   # Data import orchestration
├── infrastructure/  # External interfaces
│   ├── csv_parser.py    # High-performance Jira CSV parsing
│   ├── csv_analyzer.py  # Smart column aggregation and sprint extraction
│   ├── repositories.py  # Repository implementations
│   ├── theme_repository.py  # Theme storage and retrieval
│   ├── monte_carlo_model.py  # Monte Carlo forecasting implementation
│   ├── forecasting_model_factory.py  # Model factory and registration
│   ├── jira_data_source.py  # Jira CSV data source implementation
│   ├── linear_data_source.py  # Linear CSV data source implementation
│   └── data_source_factory.py  # Data source factory
└── presentation/    # UI and presentation logic
    ├── cli.py           # Command-line interface with rich output
    ├── report_generator.py  # HTML report generation with Plotly charts
    ├── multi_report_generator.py  # Multi-project dashboard and report generation
    ├── style_generator.py  # CSS generation from themes
    └── templates.py     # HTML templates with clean separation
```

### Key Components

- **Domain Layer**: Contains pure business logic with no external dependencies
- **Application Layer**: Orchestrates domain objects to perform use cases
- **Infrastructure Layer**: Handles external concerns (file I/O, parsing)
- **Presentation Layer**: User interface and report generation

## Performance Optimizations

1. **Polars DataFrame**: Uses Polars instead of Pandas for 10x faster CSV parsing
2. **Smart Column Aggregation**: Handles Jira's duplicate columns (Sprint, Sprint.1, Sprint.2...Sprint.15)
3. **Lazy Evaluation**: Processes large CSV files with minimal memory usage
4. **Batch Processing**: Configurable batch sizes for processing millions of rows
5. **Efficient Data Structures**: In-memory repositories with indexed lookups
6. **Outlier Filtering**: Removes velocity outliers to improve prediction accuracy

## Testing

Run the test suite:

```bash
# Run all tests with coverage
pytest

# Run specific test file
pytest tests/unit/test_entities.py

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov-report=html
```

## Output Report

The generated HTML report includes:

1. **Summary Metrics**:
   - Remaining work (in story points)
   - Average velocity per sprint
   - Sprint-based predictions (50%, 70%, 85%, 95% confidence)
   - Automatic duplicate confidence level handling

2. **Interactive Charts**:
   - Sprint-based probability distribution
   - Historical velocity trend with regression line
   - Forecast timeline with confidence markers
   - Confidence intervals by sprint count

3. **Detailed Analysis**:
   - Completion predictions in sprints (not days)
   - Velocity outlier detection and filtering
   - Sprint duration auto-detection
   - Issue status distribution

## Styling and Themes

The tool supports customizable themes for HTML reports:

### Available Themes
- **opreto** (default): Professional theme following Opreto's brand guidelines
  - Teal primary colors (#03564c, #022d2c)
  - Sublima font for headings, Inter for body text
  - Hero archetype design elements
  - Dynamic hover effects and transitions
  - BI best practice chart colors:
    - Green (#00A86B) for high confidence/positive outcomes
    - Orange (#FFA500) for medium confidence/caution
    - Red (#DC143C) for low confidence/risk
    - Colorblind-friendly data visualization palette
- **generic**: Clean, modern theme with purple accents
  - Purple/teal color scheme
  - System fonts
  - Traditional chart colors

### Using Themes
```bash
# Use Opreto theme (default)
uv run python -m src.presentation.cli -f data.csv

# Use generic theme
uv run python -m src.presentation.cli -f data.csv --theme generic
```

### Theme Architecture
The styling system follows clean architecture principles:
- **Domain Layer**: Theme entities and value objects
- **Application Layer**: StyleService for theme management
- **Infrastructure Layer**: FileThemeRepository for theme persistence
- **Presentation Layer**: StyleGenerator for CSS generation

Themes are stored in `~/.jira-monte-carlo/themes.json` and can be customized.

## Extensibility

### Adding New Forecasting Models

The system supports pluggable forecasting models. To add a new model:

1. Implement the `ForecastingModel` interface:
```python
from domain.forecasting import ForecastingModel, ForecastResult, ModelInfo

class MyCustomModel(ForecastingModel):
    def forecast(self, remaining_work, velocity_metrics, config):
        # Your forecasting logic here
        return ForecastResult(...)
    
    def get_model_info(self):
        return ModelInfo(
            model_type=ModelType.CUSTOM,
            name="My Custom Model",
            description="Description of your model"
        )
```

2. Register your model in the factory:
```python
factory.register_model(ModelType.CUSTOM, MyCustomModel)
```

### Adding New Data Sources

To support new data formats:

1. Implement the `DataSource` interface
2. Register in `DefaultDataSourceFactory`
3. Add auto-detection logic if desired

## Configuration Files

Configuration is stored in `~/.jira-monte-carlo/`:
- `field_mapping.json`: Jira field mappings
- `status_mapping.json`: Status categorization
- `themes.json`: Visual themes for reports

## Architectural Decisions

Major architectural decisions are documented in the `docs/architecture/` directory using Lightweight Architecture Decision Records (LADRs). Key decisions include:

- **0001-data-source-abstraction.md**: Abstraction layer for supporting multiple data sources
- **0002-statistical-model-abstraction.md**: Pluggable forecasting model architecture

## Development

### Code Style

The project uses:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- mypy for type checking

Run code quality checks:

```bash
black src tests
isort src tests
flake8 src tests
mypy src
```

### Adding New Features

1. Start with domain entities and value objects
2. Define repository interfaces
3. Implement use cases in the application layer
4. Add infrastructure implementations
5. Update the CLI and report generator
6. Write comprehensive tests

## Troubleshooting

### Common Issues

1. **CSV Parse Errors**: Ensure your CSV is properly formatted and not corrupted
2. **Memory Issues**: Reduce batch size in `csv_parser.py` for very large files
3. **Date Parse Errors**: The tool handles multiple date formats automatically
4. **Duplicate Sprint Columns**: Automatically handled by column aggregation
5. **Missing Created Date**: Uses default date (1 year ago) when missing
6. **Zero Velocity**: Check that issues have story points and correct status mappings

### Debug Mode

Set logging level to DEBUG for detailed output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Roadmap

### Recently Completed
- ✅ Monte Carlo simulation engine
- ✅ Multi-source data import (Jira, Linear)
- ✅ Sprint velocity analysis
- ✅ Beautiful HTML reports with charts
- ✅ Multi-project dashboard
- ✅ Sprint names on X-axis for velocity charts
- ✅ Story size breakdown chart for remaining work

### In Progress
- 🚧 Additional analytics for scrum masters

### Planned Features

#### Analytics & Metrics
- **Sprint Health Metrics**
  - Sprint burndown charts
  - Sprint completion rate tracking
  - Sprint predictability metrics (variance/std dev)
  - Commitment vs delivery analysis

- **Flow Metrics**  
  - Cycle time distribution histogram
  - Lead time analysis
  - Work In Progress (WIP) visualization
  - Throughput trends (items/week)
  - Flow efficiency calculations

- **Team Performance**
  - Velocity by team member (if assignee data available)
  - Estimation accuracy tracking
  - Sprint commitment reliability
  - Rework rate analysis

- **Risk & Blockers**
  - Aging work items report
  - Blocked items tracking with duration
  - Bug vs feature ratio
  - Technical debt tracking (if labeled)
  - Items without estimates

- **Forecasting Enhancements**
  - Best/worst case scenario visualization
  - Release burnup charts
  - Feature/epic completion forecasts
  - Scope change impact analysis
  - What-if scenario modeling

- **Portfolio/Program Level**
  - Cross-team dependency visualization
  - Program Increment (PI) progress (SAFe)
  - Epic progress rollups
  - Resource allocation insights
  - Portfolio health dashboard

#### Technical Improvements
- **Performance Optimizations**
  - Parallel CSV processing
  - Caching for large datasets
  - Incremental updates

- **Data Source Expansion**
  - Azure DevOps integration
  - GitHub Issues integration
  - Trello integration
  - Monday.com integration

- **Export Capabilities**
  - PDF report generation
  - Excel export with raw data
  - PowerPoint presentation mode
  - Slack/Teams integration

- **Advanced Modeling**
  - PERT estimation model
  - Bayesian forecasting
  - Machine learning predictions
  - Seasonal adjustment models

#### User Experience
- **Interactive Dashboards**
  - Real-time filtering
  - Drill-down capabilities
  - Custom date ranges
  - Saved view configurations

- **Customization**
  - Custom metrics definition
  - Configurable workflows
  - Theme builder
  - Report templates

### Future Vision
- SaaS offering with team collaboration
- Real-time Jira webhook integration
- AI-powered insights and recommendations
- Mobile app for on-the-go analytics

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details
