# Monte Carlo Simulation for Agile Projects

A high-performance Monte Carlo simulation tool for agile project forecasting. This tool analyzes historical velocity data from various sources (Jira, Linear, etc.) and uses Monte Carlo simulations to predict project completion dates with confidence intervals.

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

## Getting Started (Quick Setup for Jira API)

The most common use case is connecting directly to your Jira instance. Here's how to get up and running in 5 minutes:

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/opreto/jira-monte-carlo.git
cd jira-monte-carlo

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
jira-monte-carlo -f jira-api:// -o reports/forecast.html

# Open the report in your browser
open reports/forecast.html  # On Windows: start reports/forecast.html
```

That's it! You now have a comprehensive Monte Carlo forecast for your project.

### Common Next Steps

```bash
# Analyze a specific project (overrides .env)
jira-monte-carlo -f jira-api://MYPROJECT -o reports/myproject.html

# Model vacation impact
jira-monte-carlo -f jira-api:// \
  --velocity-change "sprint:10,factor:0.7,reason:team vacation week"

# Include process health metrics
jira-monte-carlo -f jira-api:// --include-process-health

# Clear cache to fetch fresh data
jira-monte-carlo --clear-cache
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

**Option 1: Connect directly to Jira API (Recommended)**
```bash
# Set up .env file with your Jira credentials (see Jira API Integration section)

# Analyze your project in real-time
jira-monte-carlo -f jira-api://MYPROJECT -o forecast.html

# Add velocity adjustments for vacation planning
jira-monte-carlo -f jira-api://MYPROJECT \
  --velocity-change "sprint:10,factor:0.7,reason:team vacation"
```

**Option 2: Use exported CSV/XML files**
```bash
# Simplest usage - auto-detects format
jira-monte-carlo -f export.csv

# Specify format explicitly
jira-monte-carlo -f linear-export.csv --format linear
jira-monte-carlo -f jira-export.csv --format jira
jira-monte-carlo -f jira-export.xml --format jira-xml

# Process multiple files (can be different formats)
jira-monte-carlo -f jira-export.csv -f linear-export.csv -f jira-backup.xml
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
EOF

# Generate report from Jira API (uses JIRA_PROJECT_KEY from .env)
jira-monte-carlo -f jira-api:// -o reports/forecast.html

# Use a specific project (overrides .env)
jira-monte-carlo -f jira-api://PROJECT-KEY -o reports/forecast.html

# Multiple projects in one dashboard
jira-monte-carlo -f jira-api://PROJ1 -f jira-api://PROJ2 -o dashboard.html

# Clear cache to fetch fresh data
jira-monte-carlo --clear-cache

# View cache information
jira-monte-carlo --cache-info
```

To get an Atlassian API token:
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a descriptive name
4. Copy the token to your .env file

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
  --include-process-health       Include process health metrics in the report

Velocity Change Prediction (What-If Analysis):
  --velocity-change TEXT         Model velocity changes (format: "sprint:N[-M],factor:F[,reason:R]")
  --team-change TEXT             Model team size changes (format: "sprint:N,change:±C[,ramp:R]")
  
  Sprint ranges: Use N for single sprint, N-M for range, N+ for sprint N onwards (forever)
  Multiple changes: Repeat flags for multiple adjustments

Cache Management:
  --clear-cache                  Clear the API cache before running
  --cache-info                   Show cache information and exit
```

### Process Health Analysis

Include comprehensive process health metrics in your report:

```bash
# Enable process health analysis
jira-monte-carlo -f jira-api:// --include-process-health

# Set custom WIP limits
jira-monte-carlo -f data.csv --include-process-health --wip-limit "in_progress:10" --wip-limit "review:5"
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
jira-monte-carlo -f jira-api://DM \
  --velocity-change "sprint:17,factor:0.74,reason:vacations (1 engineer 3 days + 1 full sprint)"

# Complex scenario with team scaling
jira-monte-carlo -f jira-api://MYPROJECT \
  --velocity-change "sprint:26,factor:0.8,reason:holidays" \
  --team-change "sprint:27,change:+2,ramp:4" \
  --velocity-change "sprint:27+,factor:1.2,reason:team scaled up"

# Analyze impact on multiple projects
jira-monte-carlo -f jira-api://PROJ1 -f jira-api://PROJ2 \
  --velocity-change "sprint:10-12,factor:0.7,reason:summer vacation period"
```

**Using with CSV files:**
```bash
# One person on vacation for sprint 3 (50% capacity reduction for small team)
jira-monte-carlo -f data.csv \
  --velocity-change "sprint:3,factor:0.5,reason:vacation"

# Summer vacation period affecting sprints 5-7 with 30% reduced capacity
jira-monte-carlo -f data.csv \
  --velocity-change "sprint:5-7,factor:0.7,reason:summer-holidays"

# Adding one developer starting sprint 4 with 3-sprint ramp-up
jira-monte-carlo -f data.csv \
  --team-change "sprint:4,change:+1,ramp:3"

# Scaling up by 2 developers permanently starting sprint 6
jira-monte-carlo -f data.csv \
  --team-change "sprint:6,change:+2,ramp:4" \
  --velocity-change "sprint:6+,factor:1.25,reason:team-scaled"

# Team reduction - 2 developers leaving after sprint 8
jira-monte-carlo -f data.csv \
  --team-change "sprint:8,change:-2" \
  --velocity-change "sprint:8+,factor:0.75,reason:team-reduced"

# Complex scenario: vacation, then new hire, then permanent productivity boost
jira-monte-carlo -f data.csv \
  --velocity-change "sprint:2-3,factor:0.8,reason:key-dev-vacation" \
  --team-change "sprint:4,change:+1,ramp:3" \
  --velocity-change "sprint:7+,factor:1.1,reason:process-improvements"

# Model partial capacity (e.g., someone working 50% on another project)
jira-monte-carlo -f data.csv \
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
When velocity changes are specified, the tool generates two linked reports:
1. `forecast-baseline.html` - Standard forecast without adjustments
2. `forecast-adjusted.html` - Forecast with velocity changes applied

Each report includes:
- Clear banner at the top describing any adjustments
- Links to toggle between baseline and adjusted views
- Disclaimers on affected charts (e.g., "Note: Velocity adjusted by 70% for sprints 5-7")
- Summary table comparing key metrics between scenarios

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

### Recently Completed
- ✅ Monte Carlo simulation engine
- ✅ Multi-source data import (Jira, Linear, Jira XML)
- ✅ Jira API direct integration with caching
- ✅ Sprint velocity analysis with outlier detection
- ✅ Beautiful HTML reports with interactive Plotly charts
- ✅ Multi-project dashboard with drill-down reports
- ✅ Sprint names on X-axis for velocity charts
- ✅ Story size breakdown chart for remaining work
- ✅ Process health metrics (aging, WIP, sprint health, blocked items, lead time)
- ✅ Data source abstraction layer (LADR-0001)
- ✅ Forecasting model abstraction (LADR-0002)
- ✅ Clean architecture refactoring (LADR-0003)
- ✅ Velocity change prediction system (LADR-0004)
- ✅ Plugin architecture with registry
- ✅ Themeable reports (Opreto and generic themes)
- ✅ Clickable issue links in reports
- ✅ Health score visualization with gauges

### In Progress
- 🚧 Additional analytics for scrum masters
- 🚧 Mobile-responsive report design

### Planned Features

#### Phase 1: Mobile Experience (Priority 1)
- **Responsive Design**
  - Implement responsive chart rendering
  - Create mobile-optimized templates
  - Add server-side rendering for complex visualizations
  - Support touch gestures for chart interaction
  - Optimize data transfer for mobile networks
  - Progressive web app (PWA) capabilities

#### Phase 2: Architecture Improvements (Priority 2)
- **Performance Optimizations**
  - Parallel CSV processing for multi-file imports
  - Caching for large datasets beyond API responses
  - Incremental report updates
- **Dependency Injection Refinement**
  - Complete DI container implementation
  - Remove remaining static dependencies
  - Improve testability with better mocking

#### Phase 3: Work Classification System (Priority 3)
- **Opreto Work Type Methodology**
  - Implement 7-type classification:
    - New Functionality (50-60% target)
    - Technical Debt (15-20% target)
    - Maintenance & Support (~10% target)
    - Research & Spikes (5-10% target)
    - Experience Work (5-10% target)
    - Platform/Infrastructure (5-10% target)
    - Process & Quality (flexible)
  - Work type distribution reports
  - Alerts for allocation imbalances
  - Historical trend analysis by work type

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

- **Team Health Metrics**
  - Team-level estimation accuracy
  - Sprint commitment reliability (team aggregate)
  - Quality metrics (bug vs feature ratio)
  - Technical debt trends

- **Process Health Indicators**
  - Aging work items report (team level)
  - Blocked items tracking with duration
  - Unestimated items in backlog
  - Sprint scope changes
  - Dependency bottlenecks

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
  - Team capacity planning
  - Portfolio health dashboard

#### Git Repository Integration
- **Code-Level Insights**
  - Repository analyzer interface design
  - Git client abstraction (GitHub, GitLab, Bitbucket)
  - Commit frequency and size metrics
  - Branch lifetime analysis
  - Code ownership mapping
  - PR review engagement
  - Test coverage trends
  - Integration with issue tracking

#### Opreto-Specific Features
- **Architect Dashboard**
  - Weekly architect overview
  - Definition of Done compliance
  - Team velocity by member
  - Blockers requiring escalation
  - Time tracking anomalies
  - Executive sprint summaries
  - Technical maturity scoring
  - LADR compliance tracking

- **Team Intelligence**
  - Onboarding effectiveness metrics
  - 30/60/90 day velocity curves
  - Pairing frequency analysis
  - Team composition optimization
  - Skills gap identification

#### Technical Improvements

- **Performance & Scalability**
  - Streaming processing for very large files
  - Distributed simulation runs
  - Real-time progress updates

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
- Native mobile apps for iOS/Android
- ML-powered velocity predictions
- Technical debt accumulation forecasting
- Risk prediction based on patterns
- Client value demonstration tools

## Contributing

1. Create a feature branch in this repository
2. Write tests for new functionality
3. Ensure all tests pass
4. Submit a pull request for review

For architectural changes, please document your decisions in a LADR (Lightweight Architecture Decision Record) in the `docs/architecture` directory.

## License

This software is proprietary and confidential. Copyright (c) 2024 Opreto. All rights reserved.

This codebase is for internal Opreto use only and may not be copied, distributed, or used outside of Opreto without explicit written permission.
