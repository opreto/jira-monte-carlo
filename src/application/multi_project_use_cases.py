"""Use cases for multi-project/CSV processing"""
import logging
from typing import List, Dict, Tuple
from pathlib import Path
from datetime import datetime
import numpy as np

from ..domain.multi_project import ProjectData, AggregatedMetrics, MultiProjectReport
from ..domain.value_objects import FieldMapping, VelocityMetrics
from ..domain.entities import SimulationConfig
from ..domain.repositories import IssueRepository, SprintRepository
from ..infrastructure.csv_parser import JiraCSVParser
from ..infrastructure.csv_analyzer import SmartCSVParser, EnhancedSprintExtractor, VelocityExtractor
from .use_cases import (
    CalculateVelocityUseCase, 
    RunMonteCarloSimulationUseCase,
    CalculateRemainingWorkUseCase,
    AnalyzeHistoricalDataUseCase
)
from .csv_analysis import AnalyzeCSVStructureUseCase, AnalyzeVelocityUseCase

logger = logging.getLogger(__name__)


class ProcessMultipleCSVsUseCase:
    """Process multiple CSV files and generate individual and aggregated results"""
    
    def __init__(self, 
                 issue_repo_factory,
                 sprint_repo_factory):
        """
        Initialize with repository factories to create separate repos per project
        
        Args:
            issue_repo_factory: Callable that returns a new IssueRepository instance
            sprint_repo_factory: Callable that returns a new SprintRepository instance
        """
        self.issue_repo_factory = issue_repo_factory
        self.sprint_repo_factory = sprint_repo_factory
    
    def execute(self,
                csv_paths: List[Path],
                field_mapping: FieldMapping,
                status_mapping: Dict[str, List[str]],
                simulation_config: SimulationConfig,
                velocity_config: Dict) -> MultiProjectReport:
        """
        Process multiple CSV files and generate report
        
        Args:
            csv_paths: List of paths to CSV files
            field_mapping: Field mapping configuration
            status_mapping: Status category mapping
            simulation_config: Monte Carlo simulation configuration
            velocity_config: Velocity calculation configuration
            
        Returns:
            MultiProjectReport with individual and aggregated results
        """
        logger.info(f"Processing {len(csv_paths)} CSV files")
        
        projects = []
        
        # Process each CSV file independently
        for csv_path in csv_paths:
            logger.info(f"Processing {csv_path.name}")
            
            # Create separate repositories for each project
            issue_repo = self.issue_repo_factory()
            sprint_repo = self.sprint_repo_factory()
            
            # Process the CSV
            project_data = self._process_single_csv(
                csv_path=csv_path,
                field_mapping=field_mapping,
                status_mapping=status_mapping,
                simulation_config=simulation_config,
                velocity_config=velocity_config,
                issue_repo=issue_repo,
                sprint_repo=sprint_repo
            )
            
            projects.append(project_data)
        
        # Calculate aggregated metrics
        aggregated_metrics = self._calculate_aggregated_metrics(projects, simulation_config)
        
        return MultiProjectReport(
            projects=projects,
            aggregated_metrics=aggregated_metrics
        )
    
    def _process_single_csv(self,
                           csv_path: Path,
                           field_mapping: FieldMapping,
                           status_mapping: Dict[str, List[str]],
                           simulation_config: SimulationConfig,
                           velocity_config: Dict,
                           issue_repo: IssueRepository,
                           sprint_repo: SprintRepository) -> ProjectData:
        """Process a single CSV file"""
        
        # Derive project name from filename (remove extension)
        project_name = csv_path.stem
        
        # Analyze CSV structure
        analyze_csv_use_case = AnalyzeCSVStructureUseCase()
        with open(csv_path, 'r', encoding='utf-8') as f:
            import csv
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        analysis_result = analyze_csv_use_case.execute(headers, rows)
        
        # Parse CSV with smart parser
        smart_parser = SmartCSVParser(field_mapping, analysis_result.column_groups)
        df = smart_parser.parse_file(csv_path)
        
        # Convert to issues
        parser = JiraCSVParser(field_mapping)
        issues = parser.parse_dataframe(df)
        
        # Store issues
        issue_repo.save_all(issues)
        
        # Extract sprint velocities
        sprint_velocities = EnhancedSprintExtractor.extract_from_dataframe(
            df,
            field_mapping.sprint_field,
            field_mapping.status_field,
            status_mapping.get("done", []),
            field_mapping.story_points_field
        )
        
        # Extract velocity data points
        velocity_data_points = VelocityExtractor.extract_velocity_data(
            df,
            sprint_velocities,
            field_mapping.resolved_field or "Resolved"
        )
        
        # Analyze velocity
        from ..domain.analysis import VelocityAnalysisConfig
        velocity_analysis_config = VelocityAnalysisConfig(
            lookback_sprints=velocity_config.get('lookback_sprints', 6),
            outlier_std_devs=velocity_config.get('outlier_std_devs', 2.0),
            max_age_days=velocity_config.get('max_age_days', 240),
            min_velocity=velocity_config.get('min_velocity', 10.0)
        )
        
        analyze_velocity_use_case = AnalyzeVelocityUseCase()
        velocity_analysis = analyze_velocity_use_case.execute(
            velocity_data_points, 
            velocity_analysis_config
        )
        
        # Create sprints in repository
        sprints = []
        for vdp in velocity_analysis.filtered_velocities:
            from ..domain.entities import Sprint
            sprint = Sprint(
                name=vdp.sprint_name,
                completed_points=vdp.completed_points,
                start_date=vdp.sprint_date,
                end_date=vdp.sprint_date
            )
            sprints.append(sprint)
        sprint_repo.add_sprints(sprints)
        
        # Calculate velocity metrics
        velocity_use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
        velocity_metrics = velocity_use_case.execute(
            velocity_config.get('lookback_sprints', 6),
            velocity_config.get('velocity_field', 'story_points')
        )
        
        # Calculate remaining work
        remaining_use_case = CalculateRemainingWorkUseCase(issue_repo)
        remaining_work = remaining_use_case.execute(
            status_mapping.get("todo", []),
            velocity_config.get('velocity_field', 'story_points')
        )
        
        # Run simulation
        simulation_use_case = RunMonteCarloSimulationUseCase(issue_repo)
        simulation_result = simulation_use_case.execute(
            remaining_work,
            velocity_metrics,
            simulation_config
        )
        
        return ProjectData(
            name=project_name,
            source_path=csv_path,
            issues=issues,
            sprints=sprints,
            velocity_metrics=velocity_metrics,
            simulation_result=simulation_result,
            remaining_work=remaining_work
        )
    
    def _calculate_aggregated_metrics(self, 
                                    projects: List[ProjectData],
                                    simulation_config: SimulationConfig) -> AggregatedMetrics:
        """Calculate aggregated metrics across all projects"""
        
        total_issues = sum(p.total_issues for p in projects)
        total_done_issues = sum(p.done_issues for p in projects)
        total_remaining_work = sum(p.remaining_work for p in projects)
        
        # Calculate average and combined velocity
        velocities = [p.velocity_metrics.average for p in projects if p.velocity_metrics]
        average_velocity = np.mean(velocities) if velocities else 0.0
        combined_velocity = sum(velocities)
        
        # Get earliest and latest completion dates from all projects
        all_completion_dates = []
        for project in projects:
            if project.simulation_result and hasattr(project.simulation_result, 'mean_completion_date'):
                all_completion_dates.append(project.simulation_result.mean_completion_date)
        
        earliest_completion = min(all_completion_dates) if all_completion_dates else datetime.now()
        latest_completion = max(all_completion_dates) if all_completion_dates else datetime.now()
        
        # Calculate combined confidence intervals (using combined velocity)
        if combined_velocity > 0:
            confidence_intervals = {}
            for confidence_level in simulation_config.confidence_levels:
                sprints_needed = int(np.ceil(total_remaining_work / combined_velocity))
                # Add some variance based on individual project uncertainties
                variance_factor = 1.0 + (confidence_level - 0.5) * 0.5
                confidence_intervals[confidence_level] = int(sprints_needed * variance_factor)
        else:
            confidence_intervals = {level: 0 for level in simulation_config.confidence_levels}
        
        return AggregatedMetrics(
            total_projects=len(projects),
            total_issues=total_issues,
            total_done_issues=total_done_issues,
            total_remaining_work=total_remaining_work,
            average_velocity=average_velocity,
            combined_velocity=combined_velocity,
            earliest_completion_date=earliest_completion,
            latest_completion_date=latest_completion,
            confidence_intervals=confidence_intervals
        )