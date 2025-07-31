"""Refactored CLI entry point using command pattern"""

import logging
import os
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from .cli_new.orchestrators.main_orchestrator import MainOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger(__name__)
console = Console()


@click.command()
@click.argument("csv_paths", nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    "--remaining",
    "-r",
    type=float,
    help="Remaining work (story points). If not provided, will be calculated from data.",
)
@click.option(
    "--velocity-field",
    "-v",
    default="Story Points",
    help="Field name for velocity calculation",
)
@click.option(
    "--simulations",
    "-s",
    default=10000,
    help="Number of Monte Carlo simulations",
)
@click.option(
    "--confidence-levels",
    "-c",
    multiple=True,
    type=int,
    default=[50, 70, 85, 95],
    help="Confidence levels for predictions (can specify multiple)",
)
@click.option(
    "--project-name",
    "-p",
    help="Project name for the report",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output path for the HTML report",
)
@click.option(
    "--lookback-sprints",
    default=6,
    help="Number of sprints to look back for velocity calculation",
)
@click.option(
    "--done-status",
    "-d",
    multiple=True,
    default=["Done", "Closed", "Resolved"],
    help="Status values that indicate completed work",
)
@click.option(
    "--analyze-only",
    is_flag=True,
    help="Only analyze the CSV structure without processing",
)
@click.option(
    "--source",
    type=click.Choice(["jira", "linear", "auto"]),
    default="auto",
    help="Data source type",
)
@click.option(
    "--theme",
    type=click.Choice(["opreto", "generic"]),
    default="opreto",
    help="Report theme",
)
@click.option(
    "--open-browser",
    is_flag=True,
    help="Open the report in browser after generation",
)
@click.option(
    "--no-health",
    is_flag=True,
    help="Skip process health metrics analysis",
)
@click.option(
    "--jira-url",
    help="Base URL for Jira instance (for linking issues)",
)
# Field mapping options
@click.option("--key-field", default="Issue key", help="Field name for issue key")
@click.option("--summary-field", default="Summary", help="Field name for issue summary")
@click.option("--points-field", default="Story Points", help="Field name for story points")
@click.option("--sprint-field", default="Sprint", help="Field name for sprint")
@click.option("--status-field", default="Status", help="Field name for status")
@click.option("--created-field", default="Created", help="Field name for created date")
@click.option("--resolved-field", default="Resolved", help="Field name for resolved date")
@click.option("--labels-field", default="Labels", help="Field name for labels")
@click.option("--type-field", default="Issue Type", help="Field name for issue type")
@click.option("--assignee-field", default="Assignee", help="Field name for assignee")
@click.option("--project-field", default="Project", help="Field name for project")
@click.option("--blocked-field", help="Field name for blocked status")
# Additional options
@click.option("--sprint-length", default=14, help="Sprint length in days")
@click.option("--stale-days", default=30, help="Days before item is considered stale")
@click.option("--abandoned-days", default=90, help="Days before item is considered abandoned")
def main(
    csv_paths: List[str],
    remaining: Optional[float],
    velocity_field: str,
    simulations: int,
    confidence_levels: List[int],
    project_name: Optional[str],
    output: Optional[str],
    lookback_sprints: int,
    done_status: List[str],
    analyze_only: bool,
    source: str,
    theme: str,
    open_browser: bool,
    no_health: bool,
    jira_url: Optional[str],
    # Field mappings
    key_field: str,
    summary_field: str,
    points_field: str,
    sprint_field: str,
    status_field: str,
    created_field: str,
    resolved_field: str,
    labels_field: str,
    type_field: str,
    assignee_field: str,
    project_field: str,
    blocked_field: Optional[str],
    # Additional
    sprint_length: int,
    stale_days: int,
    abandoned_days: int,
):
    """Sprint Radar - Agile Analytics & Forecasting Tool (Refactored)
    
    Analyzes CSV data to forecast project completion using Monte Carlo simulations.
    """
    try:
        # Create args object to match existing interface
        class Args:
            pass
        
        args = Args()
        args.csv_paths = csv_paths
        args.remaining_work = remaining
        args.velocity_field = velocity_field
        args.simulations = simulations
        args.confidence_levels = list(confidence_levels) or [50, 70, 85, 95]
        args.project_name = project_name
        args.output = output
        args.lookback_sprints = lookback_sprints
        args.done_status = list(done_status)
        args.analyze_only = analyze_only
        args.source = source
        args.theme = theme
        args.open_browser = open_browser
        args.no_health = no_health
        args.jira_url = jira_url
        
        # Field mappings
        args.key_field = key_field
        args.summary_field = summary_field
        args.points_field = points_field
        args.sprint_field = sprint_field
        args.status_field = status_field
        args.created_field = created_field
        args.resolved_field = resolved_field
        args.labels_field = labels_field
        args.type_field = type_field
        args.assignee_field = assignee_field
        args.project_field = project_field
        args.blocked_field = blocked_field
        
        # Additional
        args.sprint_length = sprint_length
        args.stale_days = stale_days
        args.abandoned_days = abandoned_days
        
        # Create orchestrator
        orchestrator = MainOrchestrator(console)
        
        # Determine workflow based on arguments
        if analyze_only:
            result = orchestrator.execute_analysis_only(args)
        elif len(csv_paths) > 1:
            result = orchestrator.execute_multi_project(args, csv_paths)
        else:
            # Full workflow: import -> forecast -> report
            result = orchestrator.execute_full_workflow(args)
        
        # Handle result
        if result.success:
            console.print("\n[bold green]✓ Sprint Radar completed successfully![/bold green]")
            
            # Show output path if report was generated
            if result.data and 'output_path' in result.data:
                console.print(f"Report: {result.data['output_path']}")
        else:
            console.print(f"\n[bold red]✗ Sprint Radar failed: {result.message}[/bold red]")
            if result.error:
                logger.exception("Error details:", exc_info=result.error)
    
    except Exception as e:
        console.print(f"\n[bold red]✗ Unexpected error: {str(e)}[/bold red]")
        logger.exception("Fatal error in Sprint Radar")
        raise


if __name__ == "__main__":
    # Check if we should use the refactored version
    if os.environ.get('USE_REFACTORED_CLI', 'false').lower() == 'true':
        main()
    else:
        # Import and run original CLI
        from .cli import main as original_main
        original_main()