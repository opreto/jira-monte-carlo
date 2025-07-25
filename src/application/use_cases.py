from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from dataclasses import dataclass

from ..domain.entities import Issue, Sprint, Team, SimulationConfig, SimulationResult
from ..domain.repositories import IssueRepository, SprintRepository
from ..domain.value_objects import DateRange, VelocityMetrics, HistoricalData


class CalculateVelocityUseCase:
    def __init__(self, issue_repo: IssueRepository, sprint_repo: SprintRepository):
        self.issue_repo = issue_repo
        self.sprint_repo = sprint_repo
    
    def execute(self, 
                lookback_sprints: int = 6,
                velocity_field: str = "story_points") -> VelocityMetrics:
        # Get all sprints first
        all_sprints = self.sprint_repo.get_all()
        
        # Collect velocities from sprints with completed points
        velocities = []
        for sprint in all_sprints:
            # Use the sprint's velocity directly if available
            if hasattr(sprint, 'velocity') and sprint.velocity > 0:
                velocities.append(sprint.velocity)
            elif hasattr(sprint, 'completed_points') and sprint.completed_points > 0:
                velocities.append(sprint.completed_points)
            elif hasattr(sprint, 'completed_issues'):
                # Fall back to calculating from issues if available
                sprint_velocity = 0.0
                for issue in sprint.completed_issues:
                    if velocity_field == "story_points" and issue.story_points:
                        sprint_velocity += issue.story_points
                    elif velocity_field == "time_estimate" and issue.time_estimate:
                        sprint_velocity += issue.time_estimate
                    elif velocity_field == "count":
                        sprint_velocity += 1
                if sprint_velocity > 0:
                    velocities.append(sprint_velocity)
        
        # Take only the last N sprints if we have more
        if len(velocities) > lookback_sprints:
            velocities = velocities[-lookback_sprints:]
        
        if not velocities:
            return VelocityMetrics(0, 0, 0, 0, 0, 0)
        
        # Calculate trend
        if len(velocities) >= 2:
            x = np.arange(len(velocities))
            coefficients = np.polyfit(x, velocities, 1)
            trend = coefficients[0]
        else:
            trend = 0.0
        
        return VelocityMetrics(
            average=np.mean(velocities),
            median=np.median(velocities),
            std_dev=np.std(velocities) if len(velocities) > 1 else 0.0,
            min_value=min(velocities),
            max_value=max(velocities),
            trend=trend
        )


class RunMonteCarloSimulationUseCase:
    def __init__(self, issue_repo: IssueRepository):
        self.issue_repo = issue_repo
    
    def execute(self,
                remaining_work: float,
                velocity_metrics: VelocityMetrics,
                config: SimulationConfig) -> SimulationResult:
        completion_sprints = []
        
        # Run simulations
        for _ in range(config.num_simulations):
            sprints = 0
            work_remaining = remaining_work
            
            while work_remaining > 0:
                # Sample velocity from normal distribution
                velocity = np.random.normal(
                    velocity_metrics.average,
                    velocity_metrics.std_dev
                )
                velocity = max(0.1, velocity)  # Ensure positive velocity
                
                work_remaining -= velocity
                sprints += 1
            
            completion_sprints.append(sprints)
        
        # Calculate results
        completion_sprints = np.array(completion_sprints)
        percentiles = {}
        confidence_intervals = {}
        
        for level in config.confidence_levels:
            percentile = level * 100
            # Store sprint counts instead of days
            percentiles[level] = np.percentile(completion_sprints, percentile)
            
            # Calculate confidence interval in sprints
            lower = np.percentile(completion_sprints, (1 - level) * 50)
            upper = np.percentile(completion_sprints, 100 - (1 - level) * 50)
            confidence_intervals[level] = (lower, upper)
        
        # Create probability distribution
        hist, bin_edges = np.histogram(completion_sprints, bins=50)
        probability_distribution = hist / hist.sum()
        
        # Calculate completion dates based on sprints
        today = datetime.now()
        completion_dates = [
            today + timedelta(days=int(sprints * config.sprint_duration_days)) 
            for sprints in completion_sprints
        ]
        mean_completion_date = today + timedelta(
            days=int(np.mean(completion_sprints) * config.sprint_duration_days)
        )
        
        return SimulationResult(
            percentiles=percentiles,
            mean_completion_date=mean_completion_date,
            std_dev_days=float(np.std(completion_sprints)),  # Now represents std dev in sprints
            probability_distribution=probability_distribution.tolist(),
            completion_dates=completion_dates[:100],  # Sample for visualization
            confidence_intervals=confidence_intervals,
            completion_sprints=completion_sprints.tolist()[:1000]  # Store first 1000 for visualization
        )


class AnalyzeHistoricalDataUseCase:
    def __init__(self, issue_repo: IssueRepository):
        self.issue_repo = issue_repo
    
    def execute(self, lookback_days: int = 180) -> HistoricalData:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_days)
        date_range = DateRange(start_date, end_date)
        
        completed_issues = self.issue_repo.get_completed_in_range(date_range)
        
        # Group by week
        weekly_data: Dict[datetime, List[Issue]] = {}
        for issue in completed_issues:
            if issue.resolved:
                week_start = issue.resolved - timedelta(days=issue.resolved.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                
                if week_start not in weekly_data:
                    weekly_data[week_start] = []
                weekly_data[week_start].append(issue)
        
        # Calculate metrics per week
        velocities = []
        cycle_times = []
        throughput = []
        dates = []
        
        for week, issues in sorted(weekly_data.items()):
            week_velocity = sum(
                issue.story_points for issue in issues 
                if issue.story_points is not None
            )
            week_cycle_times = [
                issue.cycle_time for issue in issues 
                if issue.cycle_time is not None
            ]
            
            if week_velocity > 0:
                velocities.append(week_velocity)
                dates.append(week)
            
            if week_cycle_times:
                cycle_times.extend(week_cycle_times)
                throughput.append(len(issues))
        
        return HistoricalData(
            velocities=velocities,
            cycle_times=cycle_times,
            throughput=throughput,
            dates=dates
        )


class CalculateRemainingWorkUseCase:
    def __init__(self, issue_repo: IssueRepository):
        self.issue_repo = issue_repo
    
    def execute(self, 
                todo_statuses: List[str],
                velocity_field: str = "story_points") -> float:
        remaining_work = 0.0
        
        for status in todo_statuses:
            issues = self.issue_repo.get_by_status(status)
            for issue in issues:
                if velocity_field == "story_points" and issue.story_points:
                    remaining_work += issue.story_points
                elif velocity_field == "time_estimate" and issue.time_estimate:
                    remaining_work += issue.time_estimate
                elif velocity_field == "count":
                    remaining_work += 1
        
        return remaining_work