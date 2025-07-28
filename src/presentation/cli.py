import logging
from pathlib import Path
from typing import Dict, List, Optional

import click
import polars as pl
from rich.console import Console
from rich.table import Table

from ..application.csv_analysis import AnalyzeCSVStructureUseCase
from ..application.forecasting_use_cases import GenerateForecastUseCase
from ..application.import_data import AnalyzeDataSourceUseCase, ImportDataUseCase
from ..application.multi_project_import import ProcessMultipleDataSourcesUseCase
from ..application.style_service import StyleService
from ..application.use_cases import (
    AnalyzeHistoricalDataUseCase,
    CalculateRemainingWorkUseCase,
    CalculateVelocityUseCase,
    RunMonteCarloSimulationUseCase,
)
from ..domain.analysis import CSVAnalysisResult
from ..domain.data_sources import DataSourceType
from ..domain.entities import SimulationConfig
from ..domain.forecasting import ModelType, MonteCarloConfiguration
from ..domain.value_objects import FieldMapping
from ..infrastructure.data_source_factory import DefaultDataSourceFactory
from ..infrastructure.forecasting_model_factory import DefaultModelFactory
from ..infrastructure.repositories import FileConfigRepository, InMemoryIssueRepository, InMemorySprintRepository
from .multi_report_generator import MultiProjectReportGenerator
from .report_generator import HTMLReportGenerator

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--csv-file",
    "-f",
    "csv_files",
    multiple=True,
    type=click.Path(exists=True),
    help="Path to CSV export (can be specified multiple times)",
)
@click.option(
    "--format",
    "-F",
    "data_format",
    type=click.Choice(["auto", "jira", "linear"]),
    default="auto",
    help="Data source format (default: auto-detect)",
)
@click.option("--num-simulations", "-n", default=10000, help="Number of Monte Carlo simulations")
@click.option(
    "--output", "-o", default="test-report.html", help="Output HTML report filename (default: test-report.html)"
)
# Field mapping options
@click.option("--key-field", default="Issue key", help="CSV column for issue key (default: Issue key)")
@click.option("--summary-field", default="Summary", help="CSV column for issue summary (default: Summary)")
@click.option("--status-field", default="Status", help="CSV column for issue status (default: Status)")
@click.option("--created-field", default="Created", help="CSV column for created date (default: Created)")
@click.option("--resolved-field", default="Resolved", help="CSV column for resolved date (default: Resolved)")
@click.option("--story-points-field", help="CSV column for story points (default: varies by format)")
@click.option("--sprint-field", default="Sprint", help="CSV column for sprint (default: Sprint)")
# Status mapping options
@click.option(
    "--done-statuses",
    default="Done,Released,Awaiting Release,Closed,Resolved",
    help="Comma-separated list of done statuses (default: Done,Released,Awaiting Release,Closed,Resolved)",
)
@click.option(
    "--in-progress-statuses",
    default="In Progress,Analysis,Ready for QA,In Development,In Review",
    help=(
        "Comma-separated list of in-progress statuses "
        "(default: In Progress,Analysis,Ready for QA,In Development,In Review)"
    ),
)
@click.option(
    "--todo-statuses",
    default="To Do,Open,Backlog,Ready",
    help="Comma-separated list of todo statuses (default: To Do,Open,Backlog,Ready)",
)
# Analysis options
@click.option(
    "--velocity-field",
    type=click.Choice(["story_points", "time_estimate", "count"]),
    default="story_points",
    help="Velocity metric to use",
)
@click.option("--lookback-sprints", type=int, default=6, help="Number of sprints to analyze for velocity")
@click.option("--analyze-only", is_flag=True, help="Only run CSV analysis without simulation")
@click.option(
    "--max-velocity-age", type=int, default=240, help="Maximum age of velocity data in days (default: 240 = 8 months)"
)
@click.option("--outlier-std-devs", type=float, default=2.0, help="Standard deviations for outlier detection")
@click.option("--min-velocity", type=float, default=10.0, help="Minimum velocity threshold (default: 10.0)")
@click.option(
    "--theme",
    type=click.Choice(["opreto", "generic"]),
    default="opreto",
    help="Visual theme for reports (default: opreto)",
)
@click.option(
    "--model",
    type=click.Choice(["monte_carlo"]),
    default="monte_carlo",
    help="Forecasting model to use (default: monte_carlo)",
)
def main(
    csv_files: tuple,
    num_simulations: int,
    output: str,
    theme: str,
    data_format: str,
    key_field: str,
    summary_field: str,
    status_field: str,
    created_field: str,
    resolved_field: str,
    story_points_field: str,
    sprint_field: str,
    done_statuses: str,
    in_progress_statuses: str,
    todo_statuses: str,
    velocity_field: str,
    lookback_sprints: int,
    analyze_only: bool,
    max_velocity_age: int,
    outlier_std_devs: float,
    min_velocity: float,
    model: str,
):
    console.print("[bold blue]Statistical Forecasting Tool[/bold blue]")

    # Initialize repositories
    config_repo = FileConfigRepository()
    issue_repo = InMemoryIssueRepository()
    sprint_repo = InMemorySprintRepository()

    # Get CSV files
    if not csv_files:
        console.print("[red]Error: At least one CSV file path is required. Use --csv-file option.[/red]")
        return

    csv_paths = [Path(csv_file) for csv_file in csv_files]

    # Initialize data source factory
    data_source_factory = DefaultDataSourceFactory()

    # Convert format string to enum
    source_type = None
    if data_format != "auto":
        source_type = DataSourceType.JIRA_CSV if data_format == "jira" else DataSourceType.LINEAR_CSV

    # Configure field mappings - only if explicitly provided
    field_mapping = None
    if any(
        [
            key_field != "Issue key",
            summary_field != "Summary",
            status_field != "Status",
            created_field != "Created",
            resolved_field != "Resolved",
            story_points_field is not None,
            sprint_field != "Sprint",
        ]
    ):
        # User provided custom field mapping
        field_mapping = FieldMapping(
            key_field=key_field,
            summary_field=summary_field,
            issue_type_field="Issue Type",  # Default
            status_field=status_field,
            created_field=created_field,
            updated_field="Updated",  # Default
            resolved_field=resolved_field,
            story_points_field=story_points_field or "Custom field (Story point estimate)",
            time_estimate_field="Original estimate",  # Default
            time_spent_field="Time Spent",  # Default
            assignee_field="Assignee",  # Default
            reporter_field="Reporter",  # Default
            labels_field="Labels",  # Default
            sprint_field=sprint_field,
        )
    # Save for future use only if field mapping was provided
    if field_mapping:
        config_repo.save_field_mapping(field_mapping)

    # Configure status mappings
    # Use CLI-provided status mapping
    status_mapping = {
        "done": done_statuses.split(",") if done_statuses else ["Done", "Closed", "Resolved"],
        "in_progress": in_progress_statuses.split(",") if in_progress_statuses else ["In Progress"],
        "todo": todo_statuses.split(",") if todo_statuses else ["To Do", "Open"],
    }
    # Clean up whitespace
    for key in status_mapping:
        status_mapping[key] = [s.strip() for s in status_mapping[key]]
    # Save for future use
    config_repo.save_status_mapping(status_mapping)

    # Check if we have multiple files
    if len(csv_paths) > 1:
        console.print(f"\n[cyan]Processing {len(csv_paths)} CSV files...[/cyan]")
        # Use multi-project processing
        process_multiple_csvs(
            csv_paths,
            field_mapping,
            status_mapping,
            num_simulations,
            output,
            velocity_field,
            lookback_sprints,
            max_velocity_age,
            outlier_std_devs,
            min_velocity,
            theme,
            data_format,
            data_source_factory,
        )
        return

    # Single file processing using new data source abstraction
    csv_path = csv_paths[0]

    # Import data using the new abstraction
    import_use_case = ImportDataUseCase(
        data_source_factory=data_source_factory, issue_repo=issue_repo, sprint_repo=sprint_repo, config_repo=config_repo
    )

    try:
        console.print("\n[yellow]Importing data...[/yellow]")
        issues, sprints = import_use_case.execute(
            file_path=csv_path, source_type=source_type, field_mapping=field_mapping
        )
        console.print(f"[green]✓ Loaded {len(issues)} issues and {len(sprints)} sprints[/green]")

    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return

    if analyze_only:
        # Run analysis on the data source
        analyze_use_case = AnalyzeDataSourceUseCase(data_source_factory)
        analysis_result = analyze_use_case.execute(csv_path, source_type)
        display_analysis_results(analysis_result)
        return

    # Velocity analysis will be done by the use cases using the imported sprint data
    velocity_analysis = None  # Initialize for later use

    # Show issue status distribution
    show_status_distribution(issues)

    # Simulation parameters are always provided via CLI now

    # Calculate velocity
    console.print("\n[yellow]Calculating historical velocity...[/yellow]")
    velocity_use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
    velocity_metrics = velocity_use_case.execute(lookback_sprints, velocity_field)

    # Show velocity metrics
    show_velocity_metrics(velocity_metrics)

    # Calculate remaining work
    remaining_use_case = CalculateRemainingWorkUseCase(issue_repo)
    remaining_work = remaining_use_case.execute(status_mapping.get("todo", []), velocity_field)
    
    # Get story size breakdown
    story_size_breakdown = remaining_use_case.get_story_size_breakdown(status_mapping.get("todo", []))

    console.print(f"\n[cyan]Remaining work: {remaining_work:.1f} {velocity_field}[/cyan]")

    # Get model type from string
    model_type = ModelType.MONTE_CARLO  # Default
    if model == "monte_carlo":
        model_type = ModelType.MONTE_CARLO
    # Add more model types as they become available

    # Create forecasting model factory
    model_factory = DefaultModelFactory()

    # Run simulation
    model_info = model_factory.create(model_type).get_model_info()
    console.print(f"\n[yellow]Running {model_info.name} forecast...[/yellow]")

    # Get sprint duration from actual sprint data if available
    sprint_duration = 14  # Default to 2 weeks
    if sprints:
        # Calculate average sprint duration from actual data
        durations = []
        for sprint in sprints:
            if hasattr(sprint, "duration_days"):
                duration = sprint.duration_days
                if duration > 0:
                    durations.append(duration)
        if durations:
            avg_duration = sum(durations) / len(durations)
            # Round to nearest week
            sprint_duration = int(round(avg_duration / 7) * 7)
            console.print(f"[cyan]Detected sprint duration: {sprint_duration} days[/cyan]")

    # Check if we're using the new model abstraction or legacy path
    if model_type == ModelType.MONTE_CARLO:
        # Use legacy path for backward compatibility
        config = SimulationConfig(
            num_simulations=num_simulations,
            velocity_field=velocity_field,
            done_statuses=status_mapping.get("done", []),
            in_progress_statuses=status_mapping.get("in_progress", []),
            todo_statuses=status_mapping.get("todo", []),
            sprint_duration_days=sprint_duration,
        )

        simulation_use_case = RunMonteCarloSimulationUseCase(issue_repo)
        results = simulation_use_case.execute(remaining_work, velocity_metrics, config)
    else:
        # Use new model abstraction for other models
        forecasting_model = model_factory.create(model_type)
        model_config = model_factory.get_default_config(model_type)

        # Override config with CLI parameters
        if isinstance(model_config, MonteCarloConfiguration):
            model_config.num_simulations = num_simulations
            model_config.sprint_duration_days = sprint_duration

        forecast_use_case = GenerateForecastUseCase(forecasting_model, issue_repo)
        forecast_result = forecast_use_case.execute(remaining_work, velocity_metrics, model_config)

        # Convert to legacy SimulationResult format for report compatibility
        import statistics
        from datetime import datetime, timedelta

        from ..domain.entities import SimulationResult

        # Convert prediction intervals to percentiles
        percentiles = {}
        confidence_intervals = {}
        for interval in forecast_result.prediction_intervals:
            percentiles[interval.confidence_level] = interval.predicted_value
            confidence_intervals[interval.confidence_level] = (interval.lower_bound, interval.upper_bound)

        # Generate sample completion dates
        today = datetime.now()
        completion_dates = [
            today + timedelta(days=int(s * sprint_duration)) for s in forecast_result.sample_predictions[:100]
        ]

        # Create legacy result
        results = SimulationResult(
            percentiles=percentiles,
            mean_completion_date=forecast_result.expected_completion_date,
            std_dev_days=statistics.stdev(forecast_result.sample_predictions)
            if len(forecast_result.sample_predictions) > 1
            else 0.0,
            probability_distribution=[],  # Simplified for now
            completion_dates=completion_dates,
            confidence_intervals=confidence_intervals,
            completion_sprints=forecast_result.sample_predictions[:1000],
        )

    # Analyze historical data
    historical_use_case = AnalyzeHistoricalDataUseCase(issue_repo)
    historical_data = historical_use_case.execute()

    # If we have sprints with dates, create better historical data
    if sprints:
        # Extract velocity and date data directly from sprints
        sprint_velocities = []
        sprint_dates = []
        sprint_names = []
        
        # Natural sort function for sprint names
        import re
        
        def natural_sort_key(sprint):
            name = getattr(sprint, 'name', '')
            parts = []
            for part in re.split(r'(\d+)', name):
                if part.isdigit():
                    parts.append(int(part))
                else:
                    parts.append(part)
            return parts
        
        # Sort sprints by name using natural sort
        sorted_sprints = sorted(sprints, key=natural_sort_key)
        
        for sprint in sorted_sprints:
            if hasattr(sprint, "completed_points") and sprint.completed_points > 0:
                sprint_velocities.append(sprint.completed_points)
                sprint_names.append(getattr(sprint, 'name', 'Unknown'))
                # Keep dates for backwards compatibility
                if hasattr(sprint, "end_date") and sprint.end_date:
                    sprint_dates.append(sprint.end_date)
                else:
                    # Use a dummy date if no date available
                    sprint_dates.append(datetime.now())
        
        if sprint_velocities:
            from ..domain.value_objects import HistoricalData

            historical_data = HistoricalData(
                velocities=sprint_velocities,
                cycle_times=historical_data.cycle_times,  # Keep original cycle times
                throughput=historical_data.throughput,  # Keep original throughput
                dates=sprint_dates,
                sprint_names=sprint_names,
            )

    # Generate report
    console.print("\n[yellow]Generating HTML report...[/yellow]")
    style_service = StyleService()
    report_generator = HTMLReportGenerator(style_service, theme)
    # Extract project name from CSV filename
    project_name = Path(csv_path).stem

    report_path = report_generator.generate(
        simulation_results=results,
        velocity_metrics=velocity_metrics,
        historical_data=historical_data,
        remaining_work=remaining_work,
        config=config,
        output_path=Path(output),
        project_name=project_name,
        model_info=model_info,
        story_size_breakdown=story_size_breakdown,
    )

    console.print(f"\n[green]✓ Report generated: {report_path}[/green]")

    # Show summary
    show_simulation_summary(results)


def process_multiple_csvs(
    csv_paths: List[Path],
    field_mapping: Optional[FieldMapping],
    status_mapping: Dict[str, List[str]],
    num_simulations: int,
    output: str,
    velocity_field: str,
    lookback_sprints: int,
    max_velocity_age: int,
    outlier_std_devs: float,
    min_velocity: float,
    theme: str,
    data_format: str,
    data_source_factory,
):
    """Process multiple CSV files and generate multi-project report"""

    # Create simulation config
    config = SimulationConfig(
        num_simulations=num_simulations,
        velocity_field=velocity_field,
        done_statuses=status_mapping.get("done", []),
        in_progress_statuses=status_mapping.get("in_progress", []),
        todo_statuses=status_mapping.get("todo", []),
        confidence_levels=[0.5, 0.7, 0.85, 0.95],
        sprint_duration_days=14,  # Will be detected per project
    )

    # Create velocity config
    velocity_config = {
        "lookback_sprints": lookback_sprints,
        "velocity_field": velocity_field,
        "max_velocity_age": max_velocity_age,
        "outlier_std_devs": outlier_std_devs,
        "min_velocity": min_velocity,
    }

    # Convert format string to enum
    source_type = None
    if data_format != "auto":
        source_type = DataSourceType.JIRA_CSV if data_format == "jira" else DataSourceType.LINEAR_CSV

    # Process all data files using new abstraction
    use_case = ProcessMultipleDataSourcesUseCase(
        data_source_factory=data_source_factory,
        issue_repo_factory=InMemoryIssueRepository,
        sprint_repo_factory=InMemorySprintRepository,
        config_repo_factory=FileConfigRepository,
    )

    multi_report = use_case.execute(
        file_paths=csv_paths,
        source_type=source_type,
        field_mapping=field_mapping,
        status_mapping=status_mapping,
        simulation_config=config,
        velocity_config=velocity_config,
    )

    # Get model info for the default Monte Carlo model
    from ..domain.forecasting import ModelType
    from ..infrastructure.forecasting_model_factory import DefaultModelFactory
    model_factory = DefaultModelFactory()
    model = model_factory.create(ModelType.MONTE_CARLO)
    model_info = model.get_model_info()
    
    # Generate multi-project report
    console.print("\n[yellow]Generating multi-project HTML report...[/yellow]")
    style_service = StyleService()
    report_generator = MultiProjectReportGenerator(style_service, theme)
    report_path = report_generator.generate(
        multi_report=multi_report,
        output_dir=Path(output).parent,
        output_filename=Path(output).name,
        model_info=model_info,
    )

    console.print(f"\n[green]✓ Multi-project report generated: {report_path}[/green]")

    # Show summary
    show_multi_project_summary(multi_report)


def show_multi_project_summary(multi_report):
    """Display summary of multi-project simulation results"""

    # Overall summary table
    summary_table = Table(title="Multi-Project Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta")

    metrics = multi_report.aggregated_metrics
    summary_table.add_row("Total Projects", str(metrics.total_projects))
    summary_table.add_row("Total Issues", str(metrics.total_issues))
    summary_table.add_row("Completion %", f"{metrics.overall_completion_percentage:.1f}%")
    summary_table.add_row("Remaining Work", f"{metrics.total_remaining_work:.1f}")
    summary_table.add_row("Combined Velocity", f"{metrics.combined_velocity:.1f}")

    console.print(summary_table)

    # Individual project table
    project_table = Table(title="Individual Project Results")
    project_table.add_column("Project", style="cyan")
    project_table.add_column("Issues", style="green")
    project_table.add_column("Done %", style="green")
    project_table.add_column("Remaining", style="yellow")
    project_table.add_column("Velocity", style="magenta")
    project_table.add_column("85% Confidence", style="blue")

    for project in multi_report.projects:
        if project.simulation_result and project.velocity_metrics:
            confidence_85 = project.simulation_result.percentiles.get(0.85, 0)
            project_table.add_row(
                project.name,
                str(project.total_issues),
                f"{project.completion_percentage:.1f}%",
                f"{project.remaining_work:.1f}",
                f"{project.velocity_metrics.average:.1f}",
                f"{confidence_85} sprints",
            )

    console.print(project_table)


def show_status_distribution(issues: List):
    status_counts = {}
    for issue in issues:
        status_counts[issue.status] = status_counts.get(issue.status, 0) + 1

    table = Table(title="Issue Status Distribution")
    table.add_column("Status", style="cyan")
    table.add_column("Count", style="magenta")
    table.add_column("Percentage", style="green")

    total = len(issues)
    for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        table.add_row(status, str(count), f"{percentage:.1f}%")

    console.print(table)


def show_velocity_metrics(metrics):
    table = Table(title="Velocity Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Average", f"{metrics.average:.1f}")
    table.add_row("Median", f"{metrics.median:.1f}")
    table.add_row("Std Dev", f"{metrics.std_dev:.1f}")
    table.add_row("Min", f"{metrics.min_value:.1f}")
    table.add_row("Max", f"{metrics.max_value:.1f}")
    table.add_row("Trend", f"{metrics.trend:+.2f}")

    console.print(table)


def show_simulation_summary(results):
    table = Table(title="Simulation Results Summary")
    table.add_column("Confidence Level", style="cyan")
    table.add_column("Sprints to Complete", style="magenta")
    table.add_column("Completion Date", style="green")

    # Need sprint duration to calculate dates, use default if not available
    sprint_duration = 14  # Default 2 weeks

    # Deduplicate by keeping only the lowest confidence for each sprint count
    seen_sprints = {}
    for confidence, sprints in sorted(results.percentiles.items()):
        sprint_count = int(sprints)
        if sprint_count not in seen_sprints:
            seen_sprints[sprint_count] = (confidence, sprints)

    # Display in confidence order
    for confidence, sprints in sorted(seen_sprints.values()):
        # Calculate date based on sprints
        from datetime import datetime, timedelta

        days = int(sprints * sprint_duration)
        date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        table.add_row(f"{confidence*100:.0f}%", f"{sprints:.0f}", date)

    console.print(table)


def analyze_csv_structure(csv_path: Path) -> CSVAnalysisResult:
    """Analyze CSV structure to detect columns and patterns"""
    # Read CSV headers and sample rows
    df = pl.read_csv(csv_path, n_rows=1000)  # Read first 1000 rows for analysis
    headers = df.columns
    rows = df.to_numpy().tolist()

    # Run analysis
    analyzer = AnalyzeCSVStructureUseCase(sample_size=100)
    return analyzer.execute(headers, rows)


def display_analysis_results(analysis):
    """Display data source analysis results"""
    console.print("\n[bold green]Data Source Analysis Results[/bold green]")

    # Handle both CSVAnalysisResult objects and dictionaries
    if hasattr(analysis, "__dict__"):
        # Convert object to dict
        analysis_dict = {
            "total_rows": getattr(analysis, "total_rows", 0),
            "total_columns": getattr(analysis, "total_columns", 0),
            "column_groups": getattr(analysis, "column_groups", {}),
            "status_values": getattr(analysis, "status_values", []),
            "sprint_values": getattr(analysis, "sprint_values", []),
            "field_mapping_suggestions": getattr(analysis, "field_mapping_suggestions", {}),
            "numeric_field_candidates": getattr(analysis, "numeric_field_candidates", []),
        }
    else:
        analysis_dict = analysis

    # Basic info
    table = Table(title="Data Structure")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Rows", str(analysis_dict.get("total_rows", "N/A")))
    table.add_row("Total Columns", str(analysis_dict.get("total_columns", "N/A")))

    # Additional info based on source type
    if "has_estimates" in analysis_dict:
        table.add_row("Has Estimates", "Yes" if analysis_dict["has_estimates"] else "No")
    if "has_cycles" in analysis_dict:
        table.add_row("Has Cycles/Sprints", "Yes" if analysis_dict["has_cycles"] else "No")

    console.print(table)

    # Column info
    if "columns" in analysis_dict:
        console.print(f"\n[bold]Columns ({len(analysis_dict['columns'])}):[/bold]")
        for col in analysis_dict["columns"][:20]:  # Show first 20
            console.print(f"  - {col}")

    # Status values
    if "status_values" in analysis_dict and analysis_dict["status_values"]:
        console.print(f"\n[bold]Status Values ({len(analysis_dict['status_values'])}):[/bold]")
        for status in analysis_dict["status_values"][:10]:  # Show first 10
            console.print(f"  - {status}")

    # Sprint/Cycle values
    cycle_key = "cycle_values" if "cycle_values" in analysis_dict else "sprint_values"
    if cycle_key in analysis_dict and analysis_dict[cycle_key]:
        label = "Cycle" if cycle_key == "cycle_values" else "Sprint"
        console.print(f"\n[bold]{label} Values ({len(analysis_dict[cycle_key])}):[/bold]")
        for value in analysis_dict[cycle_key][:10]:  # Show first 10
            console.print(f"  - {value}")

    # Error handling
    if "error" in analysis_dict:
        console.print(f"\n[red]Error: {analysis_dict['error']}[/red]")


if __name__ == "__main__":
    main()
