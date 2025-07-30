"""Monte Carlo implementation of the forecasting model"""

import logging
import random
import statistics
from datetime import datetime, timedelta
from typing import Dict, List

from ..domain.forecasting import (
    ForecastingModel,
    ForecastResult,
    ModelConfiguration,
    ModelInfo,
    ModelType,
    MonteCarloConfiguration,
    PredictionInterval,
)
from ..domain.value_objects import VelocityMetrics

logger = logging.getLogger(__name__)


class MonteCarloModel(ForecastingModel):
    """Monte Carlo simulation forecasting model"""

    def forecast(
        self,
        remaining_work: float,
        velocity_metrics: VelocityMetrics,
        config: ModelConfiguration,
    ) -> ForecastResult:
        """Run Monte Carlo simulation to forecast completion"""

        # Ensure we have Monte Carlo specific config
        if not isinstance(config, MonteCarloConfiguration):
            # Convert to Monte Carlo config with defaults
            mc_config = MonteCarloConfiguration(
                confidence_levels=config.confidence_levels,
                sprint_duration_days=config.sprint_duration_days,
            )
        else:
            mc_config = config

        # Validate configuration
        errors = mc_config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {'; '.join(errors)}")

        # Run simulations
        completion_sprints = self._run_simulations(
            remaining_work, velocity_metrics, mc_config
        )

        # Calculate prediction intervals
        prediction_intervals = self._calculate_prediction_intervals(
            completion_sprints, mc_config.confidence_levels
        )

        # Calculate probability distribution
        probability_distribution = self._calculate_probability_distribution(
            completion_sprints
        )

        # Calculate expected values
        expected_sprints = statistics.mean(completion_sprints)
        today = datetime.now()
        expected_completion_date = today + timedelta(
            days=int(expected_sprints * mc_config.sprint_duration_days)
        )

        # Create result
        return ForecastResult(
            prediction_intervals=prediction_intervals,
            expected_sprints=expected_sprints,
            expected_completion_date=expected_completion_date,
            probability_distribution=probability_distribution,
            model_type=ModelType.MONTE_CARLO,
            model_metadata={
                "num_simulations": mc_config.num_simulations,
                "velocity_mean": velocity_metrics.average,
                "velocity_std_dev": velocity_metrics.std_dev,
                "variance_multiplier": mc_config.variance_multiplier,
            },
            sample_predictions=completion_sprints[
                :1000
            ],  # Store sample for visualization
        )

    def get_model_info(self) -> ModelInfo:
        """Get information about Monte Carlo model"""
        return ModelInfo(
            model_type=ModelType.MONTE_CARLO,
            name="Monte Carlo Simulation",
            description="Uses random sampling from velocity distribution to predict completion",
            supports_probability_distribution=True,
            required_historical_periods=3,  # Need at least 3 data points for meaningful stats
            configuration_class=MonteCarloConfiguration,
            report_title="Monte Carlo Simulation Report",
            report_subtitle="Statistical forecasting using Monte Carlo method",
            methodology_description=(
                "Uses random sampling from historical velocity data to simulate thousands of "
                "possible project outcomes, providing confidence intervals for completion dates."
            ),
        )

    def validate_inputs(
        self, remaining_work: float, velocity_metrics: VelocityMetrics
    ) -> List[str]:
        """Validate inputs for Monte Carlo simulation"""
        errors = []

        if remaining_work <= 0:
            errors.append("Remaining work must be positive")

        if velocity_metrics.average <= 0:
            errors.append("Average velocity must be positive")

        if velocity_metrics.std_dev < 0:
            errors.append("Standard deviation cannot be negative")

        # Warn if std dev is very high relative to mean
        if velocity_metrics.std_dev > velocity_metrics.average * 0.5:
            logger.warning(
                f"High velocity variance detected: "
                f"mean={velocity_metrics.average:.1f}, "
                f"std_dev={velocity_metrics.std_dev:.1f}"
            )

        return errors

    def _run_simulations(
        self,
        remaining_work: float,
        velocity_metrics: VelocityMetrics,
        config: MonteCarloConfiguration,
    ) -> List[float]:
        """Run the Monte Carlo simulations"""
        completion_sprints = []

        # Apply variance multiplier for sensitivity analysis
        adjusted_std_dev = velocity_metrics.std_dev * config.variance_multiplier

        for _ in range(config.num_simulations):
            sprints = 0
            work_remaining = remaining_work

            while work_remaining > 0:
                # Sample velocity from normal distribution
                if config.use_historical_variance and adjusted_std_dev > 0:
                    velocity = random.gauss(velocity_metrics.average, adjusted_std_dev)
                else:
                    # Use fixed velocity if no variance
                    velocity = velocity_metrics.average

                # Ensure positive velocity
                velocity = max(0.1, velocity)

                work_remaining -= velocity
                sprints += 1

                # Safety check to prevent infinite loops
                if sprints > 1000:
                    logger.warning("Simulation exceeded 1000 sprints, breaking")
                    break

            completion_sprints.append(sprints)

        return completion_sprints

    def _calculate_prediction_intervals(
        self, completion_sprints: List[float], confidence_levels: List[float]
    ) -> List[PredictionInterval]:
        """Calculate prediction intervals from simulation results"""
        sorted_sprints = sorted(completion_sprints)
        n = len(sorted_sprints)
        intervals = []

        for confidence in confidence_levels:
            # Calculate percentile index
            percentile_idx = int(n * confidence)
            percentile_idx = min(percentile_idx, n - 1)

            # Calculate confidence interval bounds
            alpha = 1 - confidence
            lower_idx = int(n * alpha / 2)
            upper_idx = int(n * (1 - alpha / 2))

            # Ensure valid indices
            lower_idx = max(0, min(lower_idx, n - 1))
            upper_idx = max(0, min(upper_idx, n - 1))

            interval = PredictionInterval(
                confidence_level=confidence,
                lower_bound=sorted_sprints[lower_idx],
                predicted_value=sorted_sprints[percentile_idx],
                upper_bound=sorted_sprints[upper_idx],
            )
            intervals.append(interval)

        return intervals

    def _calculate_probability_distribution(
        self, completion_sprints: List[float]
    ) -> Dict[int, float]:
        """Calculate probability distribution of completion sprints"""
        from collections import Counter

        # Count occurrences of each sprint count
        sprint_counts = Counter(int(s) for s in completion_sprints)
        total = len(completion_sprints)

        # Convert to probabilities
        distribution = {
            sprints: count / total for sprints, count in sprint_counts.items()
        }

        return distribution
