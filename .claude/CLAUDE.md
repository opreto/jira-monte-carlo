# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a high-performance agile project analytics tool for enterprise forecasting and agile development health assessments. It analyzes historical velocity data from various data sources (Linear and Linear CSVs, Jira REST API, etc) and provides several analytical charts, as well as monte carlo simulations for completion estimates.

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

## Architectural Documentation

- Any architectural change to the system should be documented in a LADR document in the `docs/architecture` directory of the project. The LADR status should be "ACCEPTED", and it should be simple to understand, and designed for the entire `docs/architecture` directory to provide a historical record of major architectural decisions and their rationale.

## Development Workflow

- Your workflow should be: plan -> design failing tests -> implement -> flesh out tests -> update documentation as appropriate -> commit/push.

## CLI Guidelines

- When generating reports from the CLI, ensure they always get saved in the `reports` directory.
- Any report you generate should go in the reports/ directory. Documentation should go in the docs/ directory. Keep the top level directory of the project well organized and clean.