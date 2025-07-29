import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..domain.entities import Issue, SimulationConfig, SimulationResult
from ..domain.forecasting import ForecastingModelFactory, ModelType, MonteCarloConfiguration
from ..domain.repositories import IssueRepository, SprintRepository
from ..domain.value_objects import DateRange, HistoricalData, VelocityMetrics
from .forecasting_use_cases import GenerateForecastUseCase

logger = logging.getLogger(__name__)


class CalculateVelocityUseCase:
    def __init__(self, issue_repo: IssueRepository, sprint_repo: SprintRepository):
        self.issue_repo = issue_repo
        self.sprint_repo = sprint_repo

    def execute(self, lookback_sprints: int = 6, velocity_field: str = "story_points") -> VelocityMetrics:
        # Get all sprints first
        all_sprints = self.sprint_repo.get_all()

        # Collect velocities from sprints with completed points
        velocities = []
        for sprint in all_sprints:
            # Skip if sprint is not a Sprint object (safety check)
            if isinstance(sprint, dict):
                logger.warning(f"Found dict instead of Sprint object: {sprint}")
                continue

            # Use the sprint's velocity directly if available
            if hasattr(sprint, "velocity") and sprint.velocity > 0:
                velocities.append(sprint.velocity)
            elif hasattr(sprint, "completed_points") and sprint.completed_points > 0:
                velocities.append(sprint.completed_points)
            elif hasattr(sprint, "completed_issues"):
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

        # Calculate trend using simple linear regression
        if len(velocities) >= 2:
            x = list(range(len(velocities)))
            x_mean = sum(x) / len(x)
            y_mean = sum(velocities) / len(velocities)

            numerator = sum((x[i] - x_mean) * (velocities[i] - y_mean) for i in range(len(x)))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(len(x)))

            trend = numerator / denominator if denominator != 0 else 0.0
        else:
            trend = 0.0

        return VelocityMetrics(
            average=statistics.mean(velocities),
            median=statistics.median(velocities),
            std_dev=statistics.stdev(velocities) if len(velocities) > 1 else 0.0,
            min_value=min(velocities),
            max_value=max(velocities),
            trend=trend,
        )


class RunMonteCarloSimulationUseCase:
    """Legacy use case for backward compatibility - delegates to new forecasting model"""

    def __init__(self, issue_repo: IssueRepository, model_factory: Optional[ForecastingModelFactory] = None):
        self.issue_repo = issue_repo
        # Use injected factory or create default for backward compatibility
        if model_factory is None:
            # This is a temporary measure - in production, factory should always be injected
            from ..infrastructure.forecasting_model_factory import DefaultModelFactory
            model_factory = DefaultModelFactory()
        
        # Create Monte Carlo model for backward compatibility
        self.forecasting_model = model_factory.create(ModelType.MONTE_CARLO)
        self.forecast_use_case = GenerateForecastUseCase(self.forecasting_model, issue_repo)

    def execute(
        self, remaining_work: float, velocity_metrics: VelocityMetrics, config: SimulationConfig
    ) -> SimulationResult:
        """Execute Monte Carlo simulation using new forecasting model"""

        # Convert legacy config to new model config
        model_config = MonteCarloConfiguration(
            num_simulations=config.num_simulations,
            confidence_levels=config.confidence_levels,
            sprint_duration_days=config.sprint_duration_days,
        )

        # Run forecast using new model
        forecast_result = self.forecast_use_case.execute(remaining_work, velocity_metrics, model_config)

        # Convert new ForecastResult to legacy SimulationResult
        percentiles = {}
        confidence_intervals = {}

        for interval in forecast_result.prediction_intervals:
            confidence = interval.confidence_level
            percentiles[confidence] = interval.predicted_value
            confidence_intervals[confidence] = (interval.lower_bound, interval.upper_bound)

        # Convert probability distribution from dict to list format
        # Legacy format uses 50-bin histogram
        probability_distribution = []
        if forecast_result.probability_distribution:
            min_sprints = min(forecast_result.probability_distribution.keys())
            max_sprints = max(forecast_result.probability_distribution.keys())
            bins = 50
            bin_width = (max_sprints - min_sprints) / bins if max_sprints > min_sprints else 1
            hist = [0.0] * bins

            # Populate histogram bins
            for sprints, prob in forecast_result.probability_distribution.items():
                bin_index = int((sprints - min_sprints) / bin_width)
                bin_index = min(bin_index, bins - 1)
                hist[bin_index] += prob

            probability_distribution = hist

        # Generate sample completion dates for visualization
        today = datetime.now()
        completion_dates = []
        if forecast_result.sample_predictions:
            completion_dates = [
                today + timedelta(days=int(sprints * config.sprint_duration_days))
                for sprints in forecast_result.sample_predictions[:100]
            ]

        # Return legacy format
        return SimulationResult(
            percentiles=percentiles,
            mean_completion_date=forecast_result.expected_completion_date,
            std_dev_days=statistics.stdev(forecast_result.sample_predictions)
            if len(forecast_result.sample_predictions) > 1
            else 0.0,
            probability_distribution=probability_distribution,
            completion_dates=completion_dates,
            confidence_intervals=confidence_intervals,
            completion_sprints=forecast_result.sample_predictions[:1000],
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
            week_velocity = sum(issue.story_points for issue in issues if issue.story_points is not None)
            week_cycle_times = [issue.cycle_time for issue in issues if issue.cycle_time is not None]

            if week_velocity > 0:
                velocities.append(week_velocity)
                dates.append(week)

            if week_cycle_times:
                cycle_times.extend(week_cycle_times)
                throughput.append(len(issues))

        return HistoricalData(
            velocities=velocities, cycle_times=cycle_times, throughput=throughput, dates=dates, sprint_names=None
        )


class CalculateRemainingWorkUseCase:
    def __init__(self, issue_repo: IssueRepository):
        self.issue_repo = issue_repo

    def execute(self, todo_statuses: List[str], velocity_field: str = "story_points") -> float:
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

    def get_story_size_breakdown(self, todo_statuses: List[str]) -> Dict[float, int]:
        """Get count of remaining stories grouped by story points"""
        size_breakdown = {}

        for status in todo_statuses:
            issues = self.issue_repo.get_by_status(status)
            for issue in issues:
                if issue.story_points:
                    size = float(issue.story_points)
                    size_breakdown[size] = size_breakdown.get(size, 0) + 1

        return size_breakdown
