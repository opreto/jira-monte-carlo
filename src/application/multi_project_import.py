"""Use cases for multi-project import using data source abstraction"""

import logging
import statistics
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.data_sources import DataSourceFactory, DataSourceType
from ..domain.entities import SimulationConfig
from ..domain.multi_project import AggregatedMetrics, MultiProjectReport, ProjectData
from ..domain.repositories import ConfigRepository, IssueRepository, SprintRepository
from ..domain.value_objects import FieldMapping, VelocityMetrics
from .import_data import ImportDataUseCase
from .use_cases import (
    AnalyzeHistoricalDataUseCase,
    CalculateRemainingWorkUseCase,
    CalculateVelocityUseCase,
    RunMonteCarloSimulationUseCase,
)

logger = logging.getLogger(__name__)


class ProcessMultipleDataSourcesUseCase:
    """Process multiple data files using the new data source abstraction"""

    def __init__(
        self, data_source_factory: DataSourceFactory, issue_repo_factory, sprint_repo_factory, config_repo_factory
    ):
        """
        Initialize with factories

        Args:
            data_source_factory: Factory for creating data sources
            issue_repo_factory: Callable that returns a new IssueRepository instance
            sprint_repo_factory: Callable that returns a new SprintRepository instance
            config_repo_factory: Callable that returns a new ConfigRepository instance
        """
        self.data_source_factory = data_source_factory
        self.issue_repo_factory = issue_repo_factory
        self.sprint_repo_factory = sprint_repo_factory
        self.config_repo_factory = config_repo_factory

    def execute(
        self,
        file_paths: List[Path],
        source_type: Optional[DataSourceType],
        field_mapping: Optional[FieldMapping],
        status_mapping: Dict[str, List[str]],
        simulation_config: SimulationConfig,
        velocity_config: Dict,
    ) -> MultiProjectReport:
        """
        Process multiple data files and generate report

        Args:
            file_paths: List of paths to data files
            source_type: Data source type (None for auto-detect)
            field_mapping: Field mapping configuration (None for default)
            status_mapping: Status category mapping
            simulation_config: Monte Carlo simulation configuration
            velocity_config: Velocity calculation configuration

        Returns:
            MultiProjectReport with individual and aggregated results
        """
        logger.info(f"Processing {len(file_paths)} data files")

        projects = []

        # Process each file independently
        for file_path in file_paths:
            logger.info(f"Processing {file_path.name}")

            # Create separate repositories for each project
            issue_repo = self.issue_repo_factory()
            sprint_repo = self.sprint_repo_factory()
            config_repo = self.config_repo_factory()

            # Process the file
            project_data = self._process_single_file(
                file_path=file_path,
                source_type=source_type,
                field_mapping=field_mapping,
                status_mapping=status_mapping,
                simulation_config=simulation_config,
                velocity_config=velocity_config,
                issue_repo=issue_repo,
                sprint_repo=sprint_repo,
                config_repo=config_repo,
            )

            projects.append(project_data)

        # Calculate aggregated metrics
        aggregated_metrics = self._calculate_aggregated_metrics(projects, simulation_config)

        return MultiProjectReport(projects=projects, aggregated_metrics=aggregated_metrics)

    def _process_single_file(
        self,
        file_path: Path,
        source_type: Optional[DataSourceType],
        field_mapping: Optional[FieldMapping],
        status_mapping: Dict[str, List[str]],
        simulation_config: SimulationConfig,
        velocity_config: Dict,
        issue_repo: IssueRepository,
        sprint_repo: SprintRepository,
        config_repo: ConfigRepository,
    ) -> ProjectData:
        """Process a single data file"""

        # Import data using the data source abstraction
        import_use_case = ImportDataUseCase(
            data_source_factory=self.data_source_factory,
            issue_repo=issue_repo,
            sprint_repo=sprint_repo,
            config_repo=config_repo,
        )

        try:
            issues, sprints = import_use_case.execute(
                file_path=file_path, source_type=source_type, field_mapping=field_mapping
            )
        except Exception as e:
            logger.error(f"Failed to process {file_path}: {str(e)}")
            # Return empty project data
            return ProjectData(
                name=file_path.stem,
                file_path=file_path,
                total_issues=0,
                completed_issues=0,
                remaining_work=0.0,
                completion_percentage=0.0,
                velocity_metrics=None,
                simulation_result=None,
                historical_data=None,
                sprints=[],
            )

        # Calculate metrics
        velocity_use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
        velocity_metrics = velocity_use_case.execute(
            lookback_sprints=velocity_config["lookback_sprints"], velocity_field=velocity_config["velocity_field"]
        )

        # Calculate remaining work
        remaining_use_case = CalculateRemainingWorkUseCase(issue_repo)
        remaining_work = remaining_use_case.execute(
            todo_statuses=status_mapping.get("todo", []), velocity_field=velocity_config["velocity_field"]
        )

        # Get story size breakdown
        story_size_breakdown = remaining_use_case.get_story_size_breakdown(status_mapping.get("todo", []))

        # Count completed issues
        completed_issues = []
        for status in status_mapping.get("done", []):
            completed_issues.extend(issue_repo.get_by_status(status))

        # Calculate completion percentage
        total_issues = len(issues)
        completion_percentage = (len(completed_issues) / total_issues * 100) if total_issues > 0 else 0

        # Run simulation if we have velocity
        simulation_result = None
        if velocity_metrics.average > 0 and remaining_work > 0:
            simulation_use_case = RunMonteCarloSimulationUseCase(issue_repo)
            simulation_result = simulation_use_case.execute(remaining_work, velocity_metrics, simulation_config)

        # Get historical data
        historical_use_case = AnalyzeHistoricalDataUseCase(issue_repo)
        historical_data = historical_use_case.execute()

        return ProjectData(
            name=file_path.stem,
            file_path=file_path,
            total_issues=total_issues,
            completed_issues=len(completed_issues),
            remaining_work=remaining_work,
            completion_percentage=completion_percentage,
            velocity_metrics=velocity_metrics,
            simulation_result=simulation_result,
            historical_data=historical_data,
            sprints=sprints,
            story_size_breakdown=story_size_breakdown,
        )

    def _calculate_aggregated_metrics(
        self, projects: List[ProjectData], simulation_config: SimulationConfig
    ) -> AggregatedMetrics:
        """Calculate aggregated metrics across all projects"""

        # Basic counts
        total_issues = sum(p.total_issues for p in projects)
        total_completed = sum(p.completed_issues for p in projects)
        total_remaining_work = sum(p.remaining_work for p in projects)

        # Combined velocity (sum of individual velocities)
        combined_velocity = sum(
            p.velocity_metrics.average for p in projects if p.velocity_metrics and p.velocity_metrics.average > 0
        )

        # Overall completion percentage
        # overall_completion = (total_completed / total_issues * 100) if total_issues > 0 else 0

        # Combined simulation results
        combined_simulation = None
        if combined_velocity > 0 and total_remaining_work > 0:
            # Combine velocity metrics
            velocities = [p.velocity_metrics for p in projects if p.velocity_metrics]
            if velocities:
                avg_velocity = statistics.mean([v.average for v in velocities])
                avg_std_dev = statistics.mean([v.std_dev for v in velocities if v.std_dev > 0])

                combined_velocity_metrics = VelocityMetrics(
                    average=combined_velocity,
                    median=combined_velocity,
                    std_dev=avg_std_dev * (combined_velocity / avg_velocity),  # Scale std dev
                    min_value=min(v.min_value for v in velocities),
                    max_value=sum(v.max_value for v in velocities),
                    trend=statistics.mean([v.trend for v in velocities]),
                )

                # Run combined simulation
                # Create a temporary issue repo with all remaining work
                temp_repo = self.issue_repo_factory()

                # Use first project's repo as a template for simulation
                for project in projects:
                    if project.simulation_result:
                        combined_simulation = RunMonteCarloSimulationUseCase(temp_repo).execute(
                            total_remaining_work, combined_velocity_metrics, simulation_config
                        )
                        break

        return AggregatedMetrics(
            total_projects=len(projects),
            total_issues=total_issues,
            total_completed_issues=total_completed,
            total_remaining_work=total_remaining_work,
            combined_velocity=combined_velocity,
            combined_simulation_result=combined_simulation,
        )
