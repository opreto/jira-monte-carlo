# Sprint Radar

A high-performance agile project analytics and forecasting platform. Sprint Radar analyzes historical velocity data from various sources (Jira, Linear, etc.) and uses Monte Carlo simulations to predict project completion dates with confidence intervals.

## Features

- **High Performance**: Uses Polars for efficient CSV parsing and batch processing
- **Multi-Source Support**: Import data from Jira CSV, Linear CSV, and Jira API with extensible architecture
- **Jira API Integration**: Direct connection to Jira REST API with automatic pagination for all issues
- **Intelligent Caching**: API responses cached for 1 hour to minimize server load during report iterations
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
- **Process Health Metrics**: Analyzes aging work items, WIP limits, sprint health, lead time, and blocked items
- **Enhanced Reporting**: Charts include explanatory descriptions, expandable details for items, and interactive elements
- **Lead Time Analysis**: Tracks cycle time, flow efficiency, and defect rates for quality insights
- **Plugin Architecture**: Extensible plugin system for custom report enhancements
- **Clickable Issue Links**: Direct links to Jira issues in HTML reports
- **Health Score Visualization**: Gauge charts and breakdowns with 0-100% bounded scores
- **ML-Enhanced Heuristics**: Privacy-preserving machine learning optimizes lookback periods and forecasts based on your team's patterns
- **React-Based Reports**: Modern React components with smooth chart animations for better user experience
- **Velocity Scenario Modeling**: Model team changes and velocity adjustments with smooth animated transitions between scenarios

## Getting Started (Quick Setup for Jira API)

The most common use case is connecting directly to your Jira instance. Here's how to get up and running in 5 minutes:

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/opreto/sprint-radar.git
cd sprint-radar

# Install UV (fast package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### 2. Configure Jira Access

Copy the example configuration and fill in your details:

```bash
cp .env.example .env
```

Edit `.env` with your Jira credentials:
```
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
ATLASSIAN_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ

# Optional: Custom JQL query (defaults to all issues in project)
# JIRA_JQL_FILTER=project = PROJ AND type != Epic AND status != Closed
```

To get your Atlassian API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name and copy the token

### 3. Run Your First Forecast

```bash
# Generate forecast for your project
sprint-radar -f jira-api:// -o reports/forecast.html

# Open the report in your browser
open reports/forecast.html  # On Windows: start reports/forecast.html
```

That's it! You now have a comprehensive Monte Carlo forecast for your project.

### Common Next Steps

```bash
# Analyze a specific project (overrides .env)
sprint-radar -f jira-api://MYPROJECT -o reports/myproject.html

# Model vacation impact
sprint-radar -f jira-api:// \
  --velocity-change "sprint:10,factor:0.7,reason:team vacation week"

# Use React reports with smooth animations
sprint-radar -f jira-api:// -o reports/forecast.html --use-react

# Model team changes with animated transitions
sprint-radar -f jira-api:// --use-react \
  --team-change "sprint:5,change:+2,ramp:3" \
  --velocity-change "sprint:8+,factor:1.2,reason:team expansion"

# Include process health metrics
sprint-radar -f jira-api:// --include-process-health

# Clear cache to fetch fresh data
sprint-radar --clear-cache
```

## Supported Data Sources

- **Jira CSV**: Export from Jira with all issue fields and sprint data
- **Jira API**: Direct connection to Jira Cloud/Server via REST API with automatic pagination
- **Jira XML**: Import from Jira XML exports (useful for offline analysis)
- **Linear CSV**: Export from Linear with cycle and estimate data
- **Extensible**: Clean architecture allows adding new data sources easily through the DataSource interface

## Installation

### Prerequisites

- Python 3.9 or higher
- UV (for fast dependency management)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd sprint-radar
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

**Option 1: Connect directly to Jira API (Recommended)**
```bash
# Set up .env file with your Jira credentials (see Jira API Integration section)

# Analyze your project in real-time
sprint-radar -f jira-api://MYPROJECT -o forecast.html

# Add velocity adjustments for vacation planning
sprint-radar -f jira-api://MYPROJECT \
  --velocity-change "sprint:10,factor:0.7,reason:team vacation"
```

**Option 2: Use exported CSV/XML files**
```bash
# Simplest usage - auto-detects format
sprint-radar -f export.csv

# Specify format explicitly
sprint-radar -f linear-export.csv --format linear
sprint-radar -f jira-export.csv --format jira
sprint-radar -f jira-export.xml --format jira-xml

# Process multiple files (can be different formats)
sprint-radar -f jira-export.csv -f linear-export.csv -f jira-backup.xml
```

### Jira API Integration

Connect directly to Jira without needing to export CSV files:

```bash
# Set up your Jira credentials in .env file
cat > .env << EOF
JIRA_URL=https://yourcompany.atlassian.net
JIRA_USERNAME=your.email@company.com
ATLASSIAN_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ

# Optional: Dual JQL for separate velocity calculation and forecasting
# FORECAST_JQL filters backlog items to forecast (e.g., specific labels/epics)
FORECAST_JQL="statusCategory != Done AND labels = mvp"
# HISTORY_JQL filters completed work for velocity calculation
HISTORY_JQL="project = PROJ AND statusCategory = Done AND resolved >= -52w"
EOF

# Generate report from Jira API (uses JIRA_PROJECT_KEY from .env)
sprint-radar -f jira-api:// -o reports/forecast.html

# Use a specific project (overrides .env)
sprint-radar -f jira-api://PROJECT-KEY -o reports/forecast.html

# Multiple projects in one dashboard
sprint-radar -f jira-api://PROJ1 -f jira-api://PROJ2 -o dashboard.html

# Clear cache to fetch fresh data
sprint-radar --clear-cache

# View cache information
sprint-radar --cache-info
```

To get an Atlassian API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a descriptive name
4. Copy the token to your .env file

#### Dual JQL Support (Advanced)

Sprint Radar supports using separate JQL queries for velocity calculation and forecasting. This is useful when you want to:
- Forecast only specific items (e.g., MVP features, specific epic)
- Use broader historical data for more accurate velocity calculations
- Exclude certain types of work from forecasts while including them in velocity

Example:
```bash
# In .env file:
# Forecast only MVP-labeled items
FORECAST_JQL="statusCategory != Done AND labels = mvp"
# Calculate velocity from all completed work in the last year
HISTORY_JQL="project = PROJ AND statusCategory = Done AND resolved >= -52w"
```

When both queries are configured:
- **Forecast Query**: Filters the backlog items to be predicted
- **History Query**: Filters completed work for velocity calculation
- Both queries are displayed in the generated report for transparency

If only FORECAST_JQL is set, it's used for both purposes (backward compatible).

### Smart Lookback Period Auto-Detection

Sprint Radar now intelligently determines the optimal number of historical sprints to analyze by default. The `--lookback-sprints` option defaults to "auto", which:

- Uses all data when you have ≤6 sprints
- Selects 6 sprints for teams with 7-12 sprints (standard retrospective period)
- Uses 8-10 sprints for teams with 13-24 sprints (2-3 months of data)
- Analyzes 12 sprints for teams with 25-52 sprints (one quarter)

### ML-Enhanced Lookback Optimization

For even better accuracy, enable machine learning optimization with `--enable-ml`:

```bash
# Enable ML optimization for velocity and sprint health lookback periods
sprint-radar -f jira-api:// -o forecast.html --enable-ml
```

This feature:
- Learns your team's specific patterns over time
- Optimizes lookback periods separately for velocity and sprint health metrics
- Provides visual indicators (🧠) showing when ML made decisions
- Includes explanations in tooltips for transparency
- Stores models locally with complete project isolation for privacy
- Caps at 16-20 sprints for very mature teams (maintains relevance)

You can override this by specifying a number: `--lookback-sprints 10`

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
  --lookback-sprints TEXT        Number of sprints to analyze for velocity (default: auto)
  --max-velocity-age INT         Maximum age of velocity data in days (default: 240)
  --outlier-std-devs FLOAT       Standard deviations for outlier detection (default: 2.0)
  --min-velocity FLOAT           Minimum velocity threshold (default: 10.0)
  --include-process-health       Include process health metrics in the report (deprecated)
  --exclude-process-health       Exclude process health section from the report
  --enable-ml                    Enable ML optimization for lookback periods
  --use-react                    Use React-based report generator with smooth animations (experimental)

Velocity Change Prediction (What-If Analysis):
  --velocity-change TEXT         Model velocity changes (format: "sprint:N[-M],factor:F[,reason:R]")
  --team-change TEXT             Model team size changes (format: "sprint:N,change:±C[,ramp:R]")
  
  Sprint ranges: Use N for single sprint, N-M for range, N+ for sprint N onwards (forever)
  Team changes: C can be fractional (0.5 for part-time), R (ramp) is number of sprints (can be float)
  Multiple changes: Repeat flags for multiple adjustments

Cache Management:
  --clear-cache                  Clear the API cache before running
  --cache-info                   Show cache information and exit
```

### Process Health Analysis

Include comprehensive process health metrics in your report:

```bash
# Enable process health analysis
sprint-radar -f jira-api:// --include-process-health

# Set custom WIP limits
sprint-radar -f data.csv --include-process-health --wip-limit "in_progress:10" --wip-limit "review:5"
```

Process health includes:
- **Overall Health Score**: 0-100% score with breakdown by component
- **Aging Work Items**: Identifies stale and abandoned items with expandable details
- **Work In Progress (WIP)**: Smart limits based on team size with violation tracking  
- **Sprint Health**: Completion rates, scope changes with trend analysis
- **Lead Time & Quality**: Cycle time, flow efficiency, and defect rate metrics
- **Blocked Items**: Severity-based analysis of impediments

The health score uses intelligent heuristics:
- WIP limits adjust based on team size (small/medium/large)
- Lead time scoring follows industry benchmarks (excellent <7 days, good <14 days)
- Flow efficiency bonus for teams with minimal wait times
- Scores are bounded 0-100% and cannot go negative

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

### Velocity Change Predictions (What-If Analysis)

Model the impact of team changes, vacations, and scaling on your forecasts. This feature works with CSV files and **especially well with the Jira API** for real-time forecasting:

**Using with Jira API (Recommended):**
```bash
# Model vacation impact on live Jira data
sprint-radar -f jira-api://DM \
  --velocity-change "sprint:17,factor:0.74,reason:vacations (1 engineer 3 days + 1 full sprint)"

# Complex scenario with team scaling
sprint-radar -f jira-api://MYPROJECT \
  --velocity-change "sprint:26,factor:0.8,reason:holidays" \
  --team-change "sprint:27,change:+2,ramp:4" \
  --velocity-change "sprint:27+,factor:1.2,reason:team scaled up"

# Analyze impact on multiple projects
sprint-radar -f jira-api://PROJ1 -f jira-api://PROJ2 \
  --velocity-change "sprint:10-12,factor:0.7,reason:summer vacation period"
```

**Using with CSV files:**
```bash
# One person on vacation for sprint 3 (50% capacity reduction for small team)
sprint-radar -f data.csv \
  --velocity-change "sprint:3,factor:0.5,reason:vacation"

# Summer vacation period affecting sprints 5-7 with 30% reduced capacity
sprint-radar -f data.csv \
  --velocity-change "sprint:5-7,factor:0.7,reason:summer-holidays"

# Adding one developer starting sprint 4 with 3-sprint ramp-up
sprint-radar -f data.csv \
  --team-change "sprint:4,change:+1,ramp:3"

# Scaling up by 2 developers permanently starting sprint 6
sprint-radar -f data.csv \
  --team-change "sprint:6,change:+2,ramp:4" \
  --velocity-change "sprint:6+,factor:1.25,reason:team-scaled"

# Team reduction - 2 developers leaving after sprint 8
sprint-radar -f data.csv \
  --team-change "sprint:8,change:-2" \
  --velocity-change "sprint:8+,factor:0.75,reason:team-reduced"

# Complex scenario: vacation, then new hire, then permanent productivity boost
sprint-radar -f data.csv \
  --velocity-change "sprint:2-3,factor:0.8,reason:key-dev-vacation" \
  --team-change "sprint:4,change:+1,ramp:3" \
  --velocity-change "sprint:7+,factor:1.1,reason:process-improvements"

# Model partial capacity (e.g., someone working 50% on another project)
sprint-radar -f data.csv \
  --velocity-change "sprint:3+,factor:0.9,reason:shared-resource"
```

**Velocity Change Syntax:**
- `sprint:N` - Affects only sprint N
- `sprint:N-M` - Affects sprints N through M (inclusive)
- `sprint:N+` - Affects sprint N and all future sprints (forever)
- `factor:F` - Velocity multiplier (0.5 = 50% capacity, 1.5 = 150% capacity)
- `reason:R` - Optional description for the change (appears in report)

**Team Change Syntax:**
- `change:+N` - Add N team members
- `change:-N` - Remove N team members
- `ramp:R` - Ramp-up period in sprints (default: 3)
  - New members start at 25% productivity, reaching 100% after ramp period
  - Ramp-up is linear by default

The predictions will show:
- Adjusted velocity projections
- Updated completion date confidence intervals
- Comparison between baseline and adjusted scenarios
- Visual timeline showing when changes take effect

**Report Generation:**
When velocity changes are specified, the tool generates a single combined report with both baseline and adjusted forecasts. The report includes:
- Interactive toggle to switch between baseline and adjusted views
- Real-time chart updates when switching scenarios
- Side-by-side comparison of key metrics
- Clear visualization of the impact of velocity changes

The combined report provides:
- Instant switching between scenarios without page reload
- Synchronized chart updates across all visualizations
- Highlighted differences between baseline and adjusted forecasts
- Single file for easy sharing and distribution

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
sprint-radar -f data.csv

# Use generic theme
sprint-radar -f data.csv --theme generic
```

### Theme Architecture
The styling system follows clean architecture principles:
- **Domain Layer**: Theme entities and value objects
- **Application Layer**: StyleService for theme management
- **Infrastructure Layer**: FileThemeRepository for theme persistence
- **Presentation Layer**: StyleGenerator for CSS generation

Themes are stored in `~/.sprint-radar/themes.json` and can be customized.

## Documentation

### Technical Documentation
- [Architecture Overview](docs/ARCHITECTURE.md) - System design and principles
- [Heuristics Guide](docs/HEURISTICS.md) - Detailed explanation of all algorithms and thresholds
- [Adding Data Sources](docs/ADDING_DATA_SOURCES.md) - Guide for implementing new data sources
- [Field Requirements](docs/FIELD_REQUIREMENTS.md) - Required fields for different data formats

### Understanding the Analytics
The system uses various heuristics and algorithms for predictions and health assessments. See the [Heuristics Guide](docs/HEURISTICS.md) for detailed information on:
- Monte Carlo simulation parameters
- Process health scoring algorithms
- Aging and WIP thresholds
- Lead time analysis
- Confidence level calculations

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

Configuration is stored in `~/.sprint-radar/`:
- `field_mapping.json`: Jira field mappings
- `status_mapping.json`: Status categorization
- `themes.json`: Visual themes for reports

## Architectural Decisions

Major architectural decisions are documented in the `docs/architecture/` directory using Lightweight Architecture Decision Records (LADRs). Key decisions include:

- **0001-data-source-abstraction.md**: Abstraction layer for supporting multiple data sources
- **0002-statistical-model-abstraction.md**: Pluggable forecasting model architecture
- **0003-clean-architecture-refactoring.md**: Ongoing refactoring to clean architecture principles
- **0004-velocity-change-predictions.md**: Modeling team capacity changes and their impact on forecasts

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

See [ROADMAP.md](ROADMAP.md) for the complete development roadmap, including recently completed features, work in progress, and planned enhancements.

## Contributing

1. Create a feature branch in this repository
2. Write tests for new functionality
3. Ensure all tests pass
4. Submit a pull request for review

For architectural changes, please document your decisions in a LADR (Lightweight Architecture Decision Record) in the `docs/architecture` directory.

## License

This software is proprietary and confidential. Copyright (c) 2024 Opreto. All rights reserved.

This codebase is for internal Opreto use only and may not be copied, distributed, or used outside of Opreto without explicit written permission.
