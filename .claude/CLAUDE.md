# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a high-performance Monte Carlo simulation tool for Jira project forecasting. It analyzes historical velocity data from Jira CSV exports and predicts project completion dates with confidence intervals.

## Architecture

The project follows Clean Architecture principles:
- `src/domain/` - Business entities and interfaces (no external dependencies)
- `src/application/` - Use cases and business logic
- `src/infrastructure/` - External interfaces (CSV parsing, repositories)
- `src/presentation/` - CLI and report generation

## Development Commands

```bash
# Install dependencies with UV (10-100x faster than pip)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run the CLI application
jira-monte-carlo -f jira-sample.csv

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Code formatting and linting
black src tests
isort src tests
flake8 src tests
mypy src
```

## Key Components

1. **CSV Parser** (`src/infrastructure/csv_parser.py`)
   - Uses Polars for high-performance parsing
   - Handles batch processing for large files
   - Configurable field mapping

2. **Monte Carlo Engine** (`src/application/use_cases.py`)
   - Runs configurable number of simulations
   - Calculates confidence intervals
   - Analyzes historical velocity

3. **Report Generator** (`src/presentation/report_generator.py`)
   - Creates interactive HTML reports with Plotly
   - Multiple chart types for analysis
   - Responsive design

## Testing Approach

- Unit tests focus on behavior, not implementation
- Mock external dependencies
- Test data builders for complex objects
- Coverage target: >80%

## Performance Considerations

- The sample CSV (`jira-sample.csv`) is ~745KB with complex multi-line fields
- Use Polars lazy evaluation for memory efficiency
- Batch processing for large datasets
- In-memory repositories with indexed lookups

## Configuration

User configuration stored in `~/.jira-monte-carlo/`:
- `field_mapping.json` - Maps Jira fields to domain fields
- `status_mapping.json` - Categorizes issue statuses