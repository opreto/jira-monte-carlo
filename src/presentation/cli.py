import click
import questionary
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import track
import logging
from typing import Dict, List, Optional

from ..domain.entities import SimulationConfig
from ..domain.value_objects import FieldMapping
from ..domain.analysis import VelocityAnalysisConfig, CSVAnalysisResult
from ..infrastructure.csv_parser import JiraCSVParser, CSVFieldAnalyzer
from ..infrastructure.csv_analyzer import SmartCSVParser, EnhancedSprintExtractor, VelocityExtractor
from ..infrastructure.repositories import (
    InMemoryIssueRepository, 
    InMemorySprintRepository,
    FileConfigRepository,
    SprintExtractor
)
from ..application.use_cases import (
    CalculateVelocityUseCase,
    RunMonteCarloSimulationUseCase,
    AnalyzeHistoricalDataUseCase,
    CalculateRemainingWorkUseCase
)
from ..application.csv_analysis import AnalyzeCSVStructureUseCase, AnalyzeVelocityUseCase
from .report_generator import HTMLReportGenerator
import polars as pl

console = Console()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@click.command()
@click.option('--csv-file', '-f', type=click.Path(exists=True), help='Path to Jira CSV export')
@click.option('--num-simulations', '-n', default=10000, help='Number of Monte Carlo simulations')
@click.option('--output', '-o', default='test-report.html', help='Output HTML report filename (default: test-report.html)')
@click.option('--configure', '-c', is_flag=True, help='Configure field mappings interactively')
# Field mapping options
@click.option('--key-field', default='Issue key', help='CSV column for issue key (default: Issue key)')
@click.option('--summary-field', default='Summary', help='CSV column for issue summary (default: Summary)')
@click.option('--status-field', default='Status', help='CSV column for issue status (default: Status)')
@click.option('--created-field', default='Created', help='CSV column for created date (default: Created)')
@click.option('--resolved-field', default='Resolved', help='CSV column for resolved date (default: Resolved)')
@click.option('--story-points-field', default='Custom field (Story point estimate)', help='CSV column for story points (default: Custom field (Story point estimate))')
@click.option('--sprint-field', default='Sprint', help='CSV column for sprint (default: Sprint)')
# Status mapping options
@click.option('--done-statuses', default='Done,Released,Awaiting Release,Closed,Resolved', help='Comma-separated list of done statuses (default: Done,Released,Awaiting Release,Closed,Resolved)')
@click.option('--in-progress-statuses', default='In Progress,Analysis,Ready for QA,In Development,In Review', help='Comma-separated list of in-progress statuses (default: In Progress,Analysis,Ready for QA,In Development,In Review)')
@click.option('--todo-statuses', default='To Do,Open,Backlog,Ready', help='Comma-separated list of todo statuses (default: To Do,Open,Backlog,Ready)')
# Analysis options
@click.option('--velocity-field', type=click.Choice(['story_points', 'time_estimate', 'count']), 
              default='story_points', help='Velocity metric to use')
@click.option('--lookback-sprints', type=int, default=6, help='Number of sprints to analyze for velocity')
@click.option('--analyze-only', is_flag=True, help='Only run CSV analysis without simulation')
@click.option('--max-velocity-age', type=int, default=240, help='Maximum age of velocity data in days (default: 240 = 8 months)')
@click.option('--outlier-std-devs', type=float, default=2.0, help='Standard deviations for outlier detection')
@click.option('--min-velocity', type=float, default=10.0, help='Minimum velocity threshold (default: 10.0)')
def main(csv_file: str, num_simulations: int, output: str, configure: bool,
         key_field: str, summary_field: str, status_field: str, created_field: str,
         resolved_field: str, story_points_field: str, sprint_field: str,
         done_statuses: str, in_progress_statuses: str, todo_statuses: str,
         velocity_field: str, lookback_sprints: int, analyze_only: bool,
         max_velocity_age: int, outlier_std_devs: float, min_velocity: float):
    console.print("[bold blue]Jira Monte Carlo Simulation[/bold blue]")
    
    # Initialize repositories
    config_repo = FileConfigRepository()
    issue_repo = InMemoryIssueRepository()
    sprint_repo = InMemorySprintRepository()
    
    # Get CSV file
    if not csv_file:
        csv_file = questionary.path("Enter path to Jira CSV file:").ask()
    
    csv_path = Path(csv_file)
    
    # Run CSV analysis first
    console.print("\n[yellow]Analyzing CSV structure...[/yellow]")
    analysis_result = analyze_csv_structure(csv_path)
    
    if analyze_only:
        display_analysis_results(analysis_result)
        return
    
    # With defaults, we always have CLI mappings now
    # Only check if configure flag is set
    has_cli_field_mapping = not configure
    has_cli_status_mapping = not configure
    
    # Configure field mappings
    if has_cli_field_mapping:
        # Use CLI-provided field mapping (with defaults)
        field_mapping = FieldMapping(
            key_field=key_field,
            summary_field=summary_field,
            issue_type_field="Issue Type",  # Default
            status_field=status_field,
            created_field=created_field,
            updated_field="Updated",  # Default
            resolved_field=resolved_field,
            story_points_field=story_points_field,
            time_estimate_field="Original estimate",  # Default
            time_spent_field="Time Spent",  # Default
            assignee_field="Assignee",  # Default
            reporter_field="Reporter",  # Default
            labels_field="Labels",  # Default
            sprint_field=sprint_field
        )
        # Save for future use
        config_repo.save_field_mapping(field_mapping)
    else:
        # Use interactive configuration
        field_mapping = configure_field_mapping(csv_path, config_repo, force_configure=configure)
    
    # Configure status mappings
    if has_cli_status_mapping:
        # Use CLI-provided status mapping
        status_mapping = {
            "done": done_statuses.split(",") if done_statuses else ["Done", "Closed", "Resolved"],
            "in_progress": in_progress_statuses.split(",") if in_progress_statuses else ["In Progress"],
            "todo": todo_statuses.split(",") if todo_statuses else ["To Do", "Open"]
        }
        # Clean up whitespace
        for key in status_mapping:
            status_mapping[key] = [s.strip() for s in status_mapping[key]]
        # Save for future use
        config_repo.save_status_mapping(status_mapping)
    else:
        # Use interactive configuration
        status_mapping = configure_status_mapping(config_repo, force_configure=configure)
    
    # Parse CSV with smart parser if we have analysis results
    console.print("\n[yellow]Parsing CSV file...[/yellow]")
    
    # Use smart parser with column aggregation
    from ..infrastructure.csv_analyzer import SmartCSVParser
    
    smart_parser = SmartCSVParser(field_mapping, analysis_result.column_groups)
    df = smart_parser.parse_file(csv_path)
    
    # Convert DataFrame to issues using regular parser
    parser = JiraCSVParser(field_mapping)
    issues = parser.parse_dataframe(df)
    issue_repo.add_issues(issues)
    
    console.print(f"[green]✓ Loaded {len(issues)} issues[/green]")
    
    # Extract sprints using enhanced extractor that supports aggregated columns
    velocity_analysis = None  # Initialize for later use
    if field_mapping.sprint_field:
        from ..infrastructure.csv_analyzer import EnhancedSprintExtractor, VelocityExtractor
        from ..domain.analysis import VelocityAnalysisConfig
        
        sprint_velocities = EnhancedSprintExtractor.extract_from_dataframe(
            df,
            field_mapping.sprint_field,
            field_mapping.status_field,
            status_mapping.get("done", []),
            field_mapping.story_points_field or "Story Points"
        )
        
        # Extract velocity data points with dates for filtering
        velocity_data = VelocityExtractor.extract_velocity_data(
            df,
            sprint_velocities,
            field_mapping.resolved_field or "Resolved"
        )
        
        # Apply velocity analysis with outlier filtering
        velocity_config = VelocityAnalysisConfig(
            lookback_sprints=lookback_sprints,
            outlier_std_devs=outlier_std_devs,
            max_age_days=max_velocity_age,
            min_velocity=min_velocity,
            max_velocity=200.0
        )
        
        velocity_analyzer = AnalyzeVelocityUseCase()
        velocity_analysis = velocity_analyzer.execute(velocity_data, velocity_config)
        
        console.print(f"[green]✓ Extracted {len(sprint_velocities)} sprints[/green]")
        console.print(f"[yellow]  - Filtered to {len(velocity_analysis.filtered_velocities)} sprints after outlier removal[/yellow]")
        console.print(f"[yellow]  - Removed {len(velocity_analysis.outliers_removed)} outliers[/yellow]")
        
        # Convert filtered velocities to Sprint entities
        from ..domain.entities import Sprint
        sprints = []
        for vdp in velocity_analysis.filtered_velocities:
            sprint = Sprint(
                name=vdp.sprint_name,
                completed_points=vdp.completed_points,
                start_date=vdp.sprint_date,
                end_date=vdp.sprint_date  # Use same date for both
            )
            sprints.append(sprint)
        
        sprint_repo.add_sprints(sprints)
    
    # Show issue status distribution
    show_status_distribution(issues)
    
    # Configure simulation parameters if not provided via CLI
    if not has_cli_field_mapping and not has_cli_status_mapping:
        velocity_field = questionary.select(
            "Select velocity metric:",
            choices=["story_points", "time_estimate", "count"]
        ).ask()
        
        lookback_sprints_str = questionary.text(
            "Number of sprints to analyze for velocity (default: 6):",
            default="6"
        ).ask()
        lookback_sprints = int(lookback_sprints_str)
    
    # Calculate velocity
    console.print("\n[yellow]Calculating historical velocity...[/yellow]")
    velocity_use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
    velocity_metrics = velocity_use_case.execute(lookback_sprints, velocity_field)
    
    # Show velocity metrics
    show_velocity_metrics(velocity_metrics)
    
    # Calculate remaining work
    remaining_use_case = CalculateRemainingWorkUseCase(issue_repo)
    remaining_work = remaining_use_case.execute(
        status_mapping.get("todo", []),
        velocity_field
    )
    
    console.print(f"\n[cyan]Remaining work: {remaining_work:.1f} {velocity_field}[/cyan]")
    
    # Run simulation
    console.print(f"\n[yellow]Running {num_simulations:,} Monte Carlo simulations...[/yellow]")
    
    # Get sprint duration from velocity analysis if available
    sprint_duration = 14  # Default
    if velocity_analysis and hasattr(velocity_analysis, 'sprint_duration_days'):
        sprint_duration = velocity_analysis.sprint_duration_days
        console.print(f"[cyan]Detected sprint duration: {sprint_duration} days ({sprint_duration // 7} weeks)[/cyan]")
    
    config = SimulationConfig(
        num_simulations=num_simulations,
        velocity_field=velocity_field,
        done_statuses=status_mapping.get("done", []),
        in_progress_statuses=status_mapping.get("in_progress", []),
        todo_statuses=status_mapping.get("todo", []),
        sprint_duration_days=sprint_duration
    )
    
    simulation_use_case = RunMonteCarloSimulationUseCase(issue_repo)
    results = simulation_use_case.execute(remaining_work, velocity_metrics, config)
    
    # Analyze historical data
    historical_use_case = AnalyzeHistoricalDataUseCase(issue_repo)
    historical_data = historical_use_case.execute()
    
    # If historical data is empty, create it from sprint data
    if not historical_data.velocities and velocity_analysis and velocity_analysis.filtered_velocities:
        # Create historical data from velocity analysis
        sprint_velocities = [v.completed_points for v in velocity_analysis.filtered_velocities]
        sprint_dates = [v.sprint_date for v in velocity_analysis.filtered_velocities]
        
        from ..domain.value_objects import HistoricalData
        historical_data = HistoricalData(
            velocities=sprint_velocities,
            cycle_times=[],  # We don't have cycle time data
            throughput=[],   # We don't have throughput data
            dates=sprint_dates
        )
    
    # Generate report
    console.print("\n[yellow]Generating HTML report...[/yellow]")
    report_generator = HTMLReportGenerator()
    report_path = report_generator.generate(
        simulation_results=results,
        velocity_metrics=velocity_metrics,
        historical_data=historical_data,
        remaining_work=remaining_work,
        config=config,
        output_path=Path(output)
    )
    
    console.print(f"\n[green]✓ Report generated: {report_path}[/green]")
    
    # Show summary
    show_simulation_summary(results)


def configure_field_mapping(csv_path: Path, 
                          config_repo: FileConfigRepository,
                          force_configure: bool = False) -> FieldMapping:
    # Try to load existing mapping
    if not force_configure:
        existing_mapping = config_repo.load_field_mapping()
        if existing_mapping:
            use_existing = questionary.confirm(
                "Found existing field mapping. Use it?"
            ).ask()
            if use_existing:
                return existing_mapping
    
    console.print("\n[yellow]Analyzing CSV headers...[/yellow]")
    categorized = CSVFieldAnalyzer.analyze_headers(csv_path)
    
    # Interactive field selection
    console.print("\n[bold]Configure field mappings:[/bold]")
    
    mapping_dict = {}
    
    # Key field
    mapping_dict["key_field"] = questionary.select(
        "Select issue key field:",
        choices=categorized["key_candidates"] + ["[Skip]"]
    ).ask()
    
    # Summary field
    mapping_dict["summary_field"] = questionary.select(
        "Select summary field:",
        choices=categorized["summary_candidates"] + ["[Skip]"]
    ).ask()
    
    # Status field
    mapping_dict["status_field"] = questionary.select(
        "Select status field:",
        choices=categorized["status_candidates"] + ["[Skip]"]
    ).ask()
    
    # Date fields
    mapping_dict["created_field"] = questionary.select(
        "Select created date field:",
        choices=categorized["date_candidates"] + ["[Skip]"]
    ).ask()
    
    mapping_dict["resolved_field"] = questionary.select(
        "Select resolved date field:",
        choices=categorized["date_candidates"] + ["[Skip]"]
    ).ask()
    
    # Velocity field
    mapping_dict["story_points_field"] = questionary.select(
        "Select story points field:",
        choices=categorized["numeric_candidates"] + categorized["custom_fields"] + ["[Skip]"]
    ).ask()
    
    # Sprint field
    mapping_dict["sprint_field"] = questionary.select(
        "Select sprint field:",
        choices=categorized["sprint_candidates"] + categorized["custom_fields"] + ["[Skip]"]
    ).ask()
    
    # Clean up [Skip] values
    for key, value in list(mapping_dict.items()):
        if value == "[Skip]":
            mapping_dict[key] = None
    
    field_mapping = FieldMapping(**mapping_dict)
    config_repo.save_field_mapping(field_mapping)
    
    return field_mapping


def configure_status_mapping(config_repo: FileConfigRepository,
                           force_configure: bool = False) -> Dict[str, List[str]]:
    # Try to load existing mapping
    if not force_configure:
        existing_mapping = config_repo.load_status_mapping()
        if existing_mapping:
            use_existing = questionary.confirm(
                "Found existing status mapping. Use it?"
            ).ask()
            if use_existing:
                return existing_mapping
    
    console.print("\n[bold]Configure status categories:[/bold]")
    
    # Get common status values
    default_done = ["Done", "Closed", "Resolved", "Complete"]
    default_in_progress = ["In Progress", "In Development", "In Review"]
    default_todo = ["To Do", "Open", "Backlog", "Ready"]
    
    status_mapping = {}
    
    # Done statuses
    done_input = questionary.text(
        "Enter 'Done' statuses (comma-separated):",
        default=", ".join(default_done)
    ).ask()
    status_mapping["done"] = [s.strip() for s in done_input.split(",")]
    
    # In Progress statuses
    progress_input = questionary.text(
        "Enter 'In Progress' statuses (comma-separated):",
        default=", ".join(default_in_progress)
    ).ask()
    status_mapping["in_progress"] = [s.strip() for s in progress_input.split(",")]
    
    # Todo statuses
    todo_input = questionary.text(
        "Enter 'To Do' statuses (comma-separated):",
        default=", ".join(default_todo)
    ).ask()
    status_mapping["todo"] = [s.strip() for s in todo_input.split(",")]
    
    config_repo.save_status_mapping(status_mapping)
    
    return status_mapping


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


def display_analysis_results(analysis: CSVAnalysisResult):
    """Display CSV analysis results"""
    console.print("\n[bold green]CSV Analysis Results[/bold green]")
    
    # Basic info
    table = Table(title="CSV Structure")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    
    table.add_row("Total Rows", str(analysis.total_rows))
    table.add_row("Total Columns", str(analysis.total_columns))
    table.add_row("Column Groups", str(len(analysis.column_groups)))
    
    console.print(table)
    
    # Column groups
    if analysis.column_groups:
        console.print("\n[bold]Column Groups Detected:[/bold]")
        for name, group in analysis.column_groups.items():
            if len(group.columns) > 1:
                console.print(f"  {name}: {len(group.columns)} columns (strategy: {group.aggregation_strategy.value})")
                for col in group.columns[:3]:  # Show first 3
                    console.print(f"    - {col.name} (index {col.index})")
    
    # Field mapping suggestions
    if analysis.field_mapping_suggestions:
        console.print("\n[bold]Suggested Field Mappings:[/bold]")
        for field, column in analysis.field_mapping_suggestions.items():
            console.print(f"  {field}: {column}")
    
    # Status values
    if analysis.status_values:
        console.print(f"\n[bold]Status Values ({len(analysis.status_values)}):[/bold]")
        for status in analysis.status_values[:10]:  # Show first 10
            console.print(f"  - {status}")
    
    # Sprint values
    if analysis.sprint_values:
        console.print(f"\n[bold]Sprint Values ({len(analysis.sprint_values)}):[/bold]")
        for sprint in analysis.sprint_values[:10]:  # Show first 10
            console.print(f"  - {sprint}")
    
    # Numeric fields
    if analysis.numeric_field_candidates:
        console.print("\n[bold]Numeric Field Candidates:[/bold]")
        for field in analysis.numeric_field_candidates[:10]:
            console.print(f"  - {field}")


if __name__ == "__main__":
    main()