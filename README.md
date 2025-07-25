# Jira Monte Carlo Simulation

A high-performance Monte Carlo simulation tool for Jira project forecasting. This tool analyzes historical velocity data from Jira CSV exports and uses Monte Carlo simulations to predict project completion dates with confidence intervals.

## Features

- **High Performance**: Uses Polars for efficient CSV parsing and batch processing
- **Smart Column Aggregation**: Automatically handles Jira's duplicate Sprint columns (Sprint, Sprint.1, Sprint.2, etc.)
- **Sprint-Based Forecasting**: Predictions in sprints rather than days for clearer planning
- **Velocity Outlier Detection**: Filters outliers using z-score and time-based analysis
- **Configurable Field Mapping**: Interactive CLI or command-line options to map Jira's customizable fields
- **Monte Carlo Simulations**: Run thousands of simulations to predict project completion dates
- **Beautiful HTML Reports**: Visual charts showing probability distributions, velocity trends, and forecasts
- **Clean Architecture**: Follows Domain-Driven Design principles for maintainability
- **Sprint Duration Detection**: Automatically detects sprint length from data
- **Multiple Status Support**: Handles custom Jira workflows with configurable status mappings

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

Run the Monte Carlo simulation on a Jira CSV export:

```bash
# Simplest usage with defaults for standard Jira exports
uv run python -m src.presentation.cli --csv-file jira-export.csv

# Or if installed as package
jira-monte-carlo -f jira-export.csv
```

### Command Line Options

```
Basic Options:
  -f, --csv-file PATH            Path to Jira CSV export [required]
  -n, --num-simulations INT      Number of Monte Carlo simulations (default: 10000)
  -o, --output TEXT              Output HTML report filename (default: test-report.html)
  -c, --configure                Configure field mappings interactively
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

### Interactive Configuration

On first run, the tool will guide you through configuring:

1. **Field Mappings**: Map your Jira fields to the tool's expected fields
   - Issue key, summary, status fields
   - Date fields (created, resolved)
   - Velocity metrics (story points, time estimates)
   - Sprint information

2. **Status Categories**: Define which statuses represent:
   - Done (completed work)
   - In Progress (work in flight)
   - To Do (remaining work)

3. **Simulation Parameters**:
   - Velocity metric to use (story points, time estimate, or count)
   - Number of historical sprints to analyze
   - Number of simulations to run

### Example

```bash
# Simple usage with all defaults (recommended)
uv run python -m src.presentation.cli --csv-file "All Work with Sprints (JIRA).csv"

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

# Interactive configuration
uv run python -m src.presentation.cli \
  --csv-file jira-export.csv \
  --configure
```

## Architecture

The project follows Clean Architecture principles:

```
src/
├── domain/          # Business logic and entities
│   ├── entities.py      # Core domain models (Issue, Sprint, Team, SimulationResult)
│   ├── value_objects.py # Immutable value objects (FieldMapping, VelocityMetrics)
│   ├── repositories.py  # Repository interfaces
│   └── analysis.py      # CSV analysis domain models
├── application/     # Use cases and business rules
│   ├── use_cases.py     # Core application services
│   └── csv_analysis.py  # CSV structure analysis and velocity filtering
├── infrastructure/  # External interfaces
│   ├── csv_parser.py    # High-performance Jira CSV parsing
│   ├── csv_analyzer.py  # Smart column aggregation and sprint extraction
│   └── repositories.py  # Repository implementations
└── presentation/    # UI and presentation logic
    ├── cli.py           # Command-line interface with rich output
    └── report_generator.py  # HTML report generation with Plotly charts
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

## Configuration Files

Configuration is stored in `~/.jira-monte-carlo/`:
- `field_mapping.json`: Jira field mappings
- `status_mapping.json`: Status categorization

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details