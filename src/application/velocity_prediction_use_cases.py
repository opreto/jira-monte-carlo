"""Use cases for velocity prediction and scenario modeling"""

import logging
from typing import List, Optional, Tuple

from ..domain.entities import SimulationResult
from ..domain.forecasting import ForecastingModel, ModelConfiguration
from ..domain.value_objects import VelocityMetrics
from ..domain.velocity_adjustments import (
    ScenarioComparison,
    TeamChange,
    VelocityAdjustment,
    VelocityScenario,
)

logger = logging.getLogger(__name__)


class ApplyVelocityAdjustmentsUseCase:
    """Apply velocity adjustments to forecasting"""

    def __init__(self, forecasting_model: ForecastingModel):
        self.forecasting_model = forecasting_model

    def execute(
        self,
        remaining_work: float,
        velocity_metrics: VelocityMetrics,
        scenario: Optional[VelocityScenario],
        config: ModelConfiguration,
        team_size: int = 5,  # Default team size
    ) -> Tuple[SimulationResult, Optional[SimulationResult]]:
        """
        Generate baseline and (optionally) adjusted forecasts
        Returns: (baseline_result, adjusted_result)
        """
        # Always generate baseline
        logger.info("Generating baseline forecast")
        baseline_result = self.forecasting_model.forecast(
            remaining_work, velocity_metrics, config
        )

        if not scenario:
            return baseline_result, None

        # Generate adjusted forecast
        logger.info(f"Applying scenario: {scenario.name}")

        # Create adjusted velocity metrics
        adjusted_metrics = self._create_adjusted_metrics(
            velocity_metrics, scenario, config, team_size
        )

        # Run forecast with adjusted metrics
        adjusted_result = self.forecasting_model.forecast(
            remaining_work, adjusted_metrics, config
        )

        return baseline_result, adjusted_result

    def _create_adjusted_metrics(
        self,
        base_metrics: VelocityMetrics,
        scenario: VelocityScenario,
        config: ModelConfiguration,
        team_size: int,
    ) -> VelocityMetrics:
        """Create velocity metrics with adjustments applied"""
        # For Monte Carlo, we need to modify the velocity samples
        # This is a simplified version - in reality, we'd need to
        # track sprint numbers and apply adjustments accordingly

        # Calculate average adjustment factor across future sprints
        # This is a simplification for the initial implementation
        future_sprints = 10  # Look ahead 10 sprints
        total_factor = 0.0

        for sprint in range(1, future_sprints + 1):
            adjusted_velocity, _ = scenario.get_adjusted_velocity(
                sprint, base_metrics.average, team_size
            )
            total_factor += adjusted_velocity / base_metrics.average

        avg_factor = total_factor / future_sprints

        # Apply average factor to all metrics
        return VelocityMetrics(
            average=base_metrics.average * avg_factor,
            median=base_metrics.median * avg_factor,
            std_dev=base_metrics.std_dev,  # Keep variance the same
            min_value=base_metrics.min_value * avg_factor,
            max_value=base_metrics.max_value * avg_factor,
            trend=base_metrics.trend,
        )


class GenerateScenarioComparisonUseCase:
    """Generate comparison data for reporting"""

    def execute(
        self,
        baseline: SimulationResult,
        adjusted: SimulationResult,
        scenario: VelocityScenario,
    ) -> ScenarioComparison:
        """Generate comparison metrics and descriptions"""
        # Get key percentiles
        baseline_p50 = baseline.percentiles.get(0.5, 0)
        baseline_p85 = baseline.percentiles.get(0.85, 0)
        adjusted_p50 = adjusted.percentiles.get(0.5, 0)
        adjusted_p85 = adjusted.percentiles.get(0.85, 0)

        # Calculate velocity impact
        # Use mean of completion sprints to estimate average
        baseline_avg_sprints = (
            sum(baseline.completion_sprints[:100])
            / min(100, len(baseline.completion_sprints))
            if baseline.completion_sprints
            else baseline_p50
        )
        adjusted_avg_sprints = (
            sum(adjusted.completion_sprints[:100])
            / min(100, len(adjusted.completion_sprints))
            if adjusted.completion_sprints
            else adjusted_p50
        )
        velocity_impact = (
            ((baseline_avg_sprints - adjusted_avg_sprints) / baseline_avg_sprints * 100)
            if baseline_avg_sprints > 0
            else 0
        )

        return ScenarioComparison(
            baseline_p50_sprints=int(baseline_p50),
            baseline_p85_sprints=int(baseline_p85),
            adjusted_p50_sprints=int(adjusted_p50),
            adjusted_p85_sprints=int(adjusted_p85),
            velocity_impact_percentage=velocity_impact,
            scenario_description=scenario.get_summary(),
        )


class CreateVelocityScenarioUseCase:
    """Create a velocity scenario from individual adjustments"""

    def execute(
        self,
        name: str,
        velocity_adjustments: List[VelocityAdjustment],
        team_changes: List[TeamChange],
    ) -> VelocityScenario:
        """Create a scenario from adjustments"""
        # Sort adjustments by sprint for consistency
        sorted_adjustments = sorted(velocity_adjustments, key=lambda a: a.sprint_start)
        sorted_changes = sorted(team_changes, key=lambda c: c.sprint)

        return VelocityScenario(
            name=name, adjustments=sorted_adjustments, team_changes=sorted_changes
        )
