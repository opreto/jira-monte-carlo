#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the Jira Monte Carlo simulation.
This can be useful for automation or integration with other tools.
"""

from datetime import datetime
from pathlib import Path

from src.application.use_cases import (
    CalculateRemainingWorkUseCase,
    CalculateVelocityUseCase,
    RunMonteCarloSimulationUseCase,
)
from src.domain.entities import SimulationConfig
from src.domain.value_objects import FieldMapping
from src.infrastructure.csv_parser import JiraCSVParser
from src.infrastructure.repositories import InMemoryIssueRepository, InMemorySprintRepository, SprintExtractor
from src.presentation.report_generator import HTMLReportGenerator


def main():
    # Configuration
    csv_file = Path("jira-sample.csv")

    # Define field mappings (you can also load from config)
    field_mapping = FieldMapping(
        key_field="Issue key",
        summary_field="Summary",
        issue_type_field="Issue Type",
        status_field="Status",
        created_field="Created",
        updated_field="Updated",
        resolved_field="Resolved",
        story_points_field="Custom field (Story Points)",
        assignee_field="Assignee",
        reporter_field="Reporter",
        labels_field="Labels",
        sprint_field="Sprint",
    )

    # Status mapping
    status_mapping = {
        "done": ["Done", "Closed", "Resolved", "Complete"],
        "in_progress": ["In Progress", "In Development", "In Review"],
        "todo": ["To Do", "Open", "Backlog", "Ready"],
    }

    # Initialize repositories
    issue_repo = InMemoryIssueRepository()
    sprint_repo = InMemorySprintRepository()

    print("Parsing CSV file...")
    # Parse CSV
    parser = JiraCSVParser(field_mapping)
    issues = parser.parse_file(csv_file)
    issue_repo.add_issues(issues)
    print(f"Loaded {len(issues)} issues")

    # Extract sprints
    sprints = SprintExtractor.extract_sprints_from_issues(
        issues, sprint_field="Sprint", done_statuses=status_mapping["done"]
    )
    sprint_repo.add_sprints(sprints)
    print(f"Extracted {len(sprints)} sprints")

    # Calculate velocity
    print("\nCalculating velocity...")
    velocity_use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
    velocity_metrics = velocity_use_case.execute(lookback_sprints=6, velocity_field="story_points")

    print(f"Average velocity: {velocity_metrics.average:.1f}")
    print(f"Velocity std dev: {velocity_metrics.std_dev:.1f}")

    # Calculate remaining work
    remaining_use_case = CalculateRemainingWorkUseCase(issue_repo)
    remaining_work = remaining_use_case.execute(todo_statuses=status_mapping["todo"], velocity_field="story_points")
    print(f"\nRemaining work: {remaining_work:.1f} story points")

    # Run simulation
    print("\nRunning Monte Carlo simulation...")
    config = SimulationConfig(
        num_simulations=10000,
        velocity_field="story_points",
        done_statuses=status_mapping["done"],
        in_progress_statuses=status_mapping["in_progress"],
        todo_statuses=status_mapping["todo"],
    )

    simulation_use_case = RunMonteCarloSimulationUseCase(issue_repo)
    results = simulation_use_case.execute(remaining_work, velocity_metrics, config)

    # Display results
    print("\nSimulation Results:")
    print(f"50% confidence: {results.percentiles[0.5]:.0f} days")
    print(f"85% confidence: {results.percentiles[0.85]:.0f} days")
    print(f"95% confidence: {results.percentiles[0.95]:.0f} days")
    print(f"Mean completion date: {results.mean_completion_date.strftime('%Y-%m-%d')}")

    # Generate report
    print("\nGenerating HTML report...")
    from src.application.use_cases import AnalyzeHistoricalDataUseCase

    historical_use_case = AnalyzeHistoricalDataUseCase(issue_repo)
    historical_data = historical_use_case.execute()

    report_generator = HTMLReportGenerator()
    report_path = report_generator.generate(
        simulation_results=results,
        velocity_metrics=velocity_metrics,
        historical_data=historical_data,
        remaining_work=remaining_work,
        config=config,
        output_path=Path("example_report.html"),
    )

    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
