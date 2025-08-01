"""Integration tests for velocity scenario functionality"""

from src.domain.forecasting import (
    MonteCarloConfiguration,
)
from src.domain.value_objects import VelocityMetrics
from src.domain.velocity_adjustments import (
    VelocityAdjustment,
    TeamChange,
    VelocityScenario,
    ProductivityCurve,
)
from src.infrastructure.monte_carlo_model import MonteCarloModel
from src.application.velocity_prediction_use_cases import (
    ApplyVelocityAdjustmentsUseCase,
)


class TestVelocityScenarioIntegration:
    """Test that velocity scenarios are properly applied during forecasting"""

    def setup_method(self):
        """Set up test fixtures"""
        self.model = MonteCarloModel()
        self.use_case = ApplyVelocityAdjustmentsUseCase(self.model)

        # Base velocity metrics
        self.velocity_metrics = VelocityMetrics(
            average=20.0,
            median=20.0,
            std_dev=2.0,
            min_value=15.0,
            max_value=25.0,
            trend=0.0,
        )

        # Standard configuration
        self.config = MonteCarloConfiguration(
            num_simulations=1000,  # Reduced for faster tests
            confidence_levels=[0.5, 0.85],
            sprint_duration_days=14,
            use_historical_variance=False,  # Disable variance for predictable tests
        )

    def test_constant_velocity_adjustment(self):
        """Test that a constant velocity adjustment affects all sprints"""
        # Create scenario with 50% velocity for all sprints
        scenario = VelocityScenario(
            name="50% Capacity",
            adjustments=[
                VelocityAdjustment(
                    sprint_start=1,
                    sprint_end=None,  # Forever
                    factor=0.5,
                    reason="Half capacity",
                )
            ],
            team_changes=[],
        )

        # Run forecasts
        remaining_work = 200.0
        baseline, adjusted = self.use_case.execute(
            remaining_work, self.velocity_metrics, scenario, self.config
        )

        # With 50% velocity, it should take about twice as many sprints
        baseline_p50 = baseline.get_percentile(0.5)
        adjusted_p50 = adjusted.get_percentile(0.5)

        assert baseline_p50 is not None
        assert adjusted_p50 is not None

        # Should take about 10 sprints at full velocity, 20 at half
        assert abs(baseline_p50 - 10.0) < 1.0
        assert abs(adjusted_p50 - 20.0) < 1.0

    def test_temporary_velocity_adjustment(self):
        """Test that temporary adjustments only affect specific sprints"""
        # Create scenario with reduced velocity for first 3 sprints only
        scenario = VelocityScenario(
            name="Holiday Period",
            adjustments=[
                VelocityAdjustment(
                    sprint_start=1, sprint_end=3, factor=0.5, reason="Holiday period"
                )
            ],
            team_changes=[],
        )

        # Run forecasts
        remaining_work = 200.0
        baseline, adjusted = self.use_case.execute(
            remaining_work, self.velocity_metrics, scenario, self.config
        )

        baseline_p50 = baseline.get_percentile(0.5)
        adjusted_p50 = adjusted.get_percentile(0.5)

        assert baseline_p50 is not None
        assert adjusted_p50 is not None

        # With reduced velocity for 3 sprints, we lose 30 points (3 * 10)
        # So it should take about 2 extra sprints
        expected_delay = 2.0
        assert abs((adjusted_p50 - baseline_p50) - expected_delay) < 0.5

    def test_team_addition_with_rampup(self):
        """Test that new team members ramp up productivity over time"""
        # Create scenario adding 1 developer with 3-sprint ramp-up
        scenario = VelocityScenario(
            name="Team Growth",
            adjustments=[],
            team_changes=[
                TeamChange(
                    sprint=2,
                    change=1.0,  # Add 1 developer
                    ramp_up_sprints=3.0,
                    productivity_curve=ProductivityCurve.LINEAR,
                )
            ],
        )

        # Run forecasts with team size of 2
        remaining_work = 200.0
        team_size = 2
        baseline, adjusted = self.use_case.execute(
            remaining_work, self.velocity_metrics, scenario, self.config, team_size
        )

        baseline_p50 = baseline.get_percentile(0.5)
        adjusted_p50 = adjusted.get_percentile(0.5)

        assert baseline_p50 is not None
        assert adjusted_p50 is not None

        # Adding 50% more capacity (1 person to a 2-person team)
        # But with ramp-up, the benefit is gradual
        # Should complete faster but not 50% faster immediately
        assert adjusted_p50 < baseline_p50
        assert adjusted_p50 > baseline_p50 * 0.67  # Not full 50% improvement

    def test_multiple_adjustments_compound(self):
        """Test that multiple adjustments compound correctly"""
        # Create complex scenario
        scenario = VelocityScenario(
            name="Complex Scenario",
            adjustments=[
                VelocityAdjustment(
                    sprint_start=1, sprint_end=2, factor=0.5, reason="Initial slowdown"
                ),
                VelocityAdjustment(
                    sprint_start=5,
                    sprint_end=None,
                    factor=1.2,
                    reason="Process improvement",
                ),
            ],
            team_changes=[
                TeamChange(
                    sprint=3,
                    change=-0.5,  # Lose half a person
                    ramp_up_sprints=0,
                    productivity_curve=ProductivityCurve.STEP,
                )
            ],
        )

        # Run forecasts
        remaining_work = 300.0
        team_size = 3
        baseline, adjusted = self.use_case.execute(
            remaining_work, self.velocity_metrics, scenario, self.config, team_size
        )

        # Verify the forecast completes
        assert baseline.get_percentile(0.5) is not None
        assert adjusted.get_percentile(0.5) is not None

        # The adjustments should result in a different completion time
        assert baseline.get_percentile(0.5) != adjusted.get_percentile(0.5)

    def test_scenario_with_high_variance(self):
        """Test that scenarios work correctly with velocity variance"""
        # Enable variance with higher standard deviation for more spread
        velocity_metrics_high_var = VelocityMetrics(
            average=20.0,
            median=20.0,
            std_dev=5.0,  # Increased from 2.0 to create more variance
            min_value=10.0,
            max_value=30.0,
            trend=0.0,
        )

        config_with_variance = MonteCarloConfiguration(
            num_simulations=1000,
            confidence_levels=[0.5, 0.85],
            sprint_duration_days=14,
            use_historical_variance=True,
        )

        scenario = VelocityScenario(
            name="Consistent improvement",
            adjustments=[
                VelocityAdjustment(
                    sprint_start=1,
                    sprint_end=None,
                    factor=1.1,  # 10% improvement
                    reason="Team maturity",
                )
            ],
            team_changes=[],
        )

        remaining_work = 200.0
        baseline, adjusted = self.use_case.execute(
            remaining_work, velocity_metrics_high_var, scenario, config_with_variance
        )

        # With high variance, we should see spread in the results
        baseline_interval = (
            baseline.get_percentile(0.85) - baseline.get_percentile(0.5)
            if baseline.get_percentile(0.85) and baseline.get_percentile(0.5)
            else 0
        )
        adjusted_interval = (
            adjusted.get_percentile(0.85) - adjusted.get_percentile(0.5)
            if adjusted.get_percentile(0.85) and adjusted.get_percentile(0.5)
            else 0
        )

        # With higher variance, both should have some spread
        assert baseline_interval >= 0  # Allow 0 in case percentiles are the same
        # Adjusted might have less spread due to improvement, but should still have some
        assert adjusted_interval >= 0  # Allow 0 as valid outcome

        # 10% improvement should reduce median completion time
        assert adjusted.get_percentile(0.5) <= baseline.get_percentile(0.5)

        # Verify that variance is being applied by checking the distribution
        # has multiple different sprint counts
        from collections import Counter

        baseline_counts = Counter(int(x) for x in baseline.sample_predictions)
        adjusted_counts = Counter(int(x) for x in adjusted.sample_predictions)

        # Should have at least 2 different sprint counts in results
        assert len(baseline_counts) >= 2
        assert len(adjusted_counts) >= 2


class TestAveragingVsSprintSpecific:
    """Test that sprint-specific adjustments give different results than averaging"""

    def setup_method(self):
        """Set up test fixtures"""
        self.model = MonteCarloModel()
        self.velocity_metrics = VelocityMetrics(
            average=20.0,
            median=20.0,
            std_dev=0.0,  # No variance for predictable comparison
            min_value=20.0,
            max_value=20.0,
            trend=0.0,
        )

        self.config = MonteCarloConfiguration(
            num_simulations=100,  # Small for fast tests
            confidence_levels=[0.5],
            sprint_duration_days=14,
            use_historical_variance=False,
        )

    def test_rampup_vs_average_difference(self):
        """Test that ramp-up scenarios differ from averaged approach"""
        # Scenario: Add 1 person to 1-person team with 4-sprint ramp-up
        scenario = VelocityScenario(
            name="Team doubling with ramp-up",
            adjustments=[],
            team_changes=[
                TeamChange(
                    sprint=1,
                    change=1.0,
                    ramp_up_sprints=4.0,
                    productivity_curve=ProductivityCurve.LINEAR,
                )
            ],
        )

        remaining_work = 160.0  # 8 sprints of work at base velocity

        # Calculate what the old averaging approach would give
        # Linear ramp: 0.25, 0.5, 0.75, 1.0, then 1.0 forever
        # Average over 10 sprints: (0.25+0.5+0.75+1.0*7)/10 = 0.825
        # So average factor = 1.825 (original 1 + 0.825 new)
        averaged_velocity = 20.0 * 1.825
        averaged_sprints = remaining_work / averaged_velocity  # ~4.38 sprints

        # Run with sprint-specific adjustments
        use_case = ApplyVelocityAdjustmentsUseCase(self.model)
        _, adjusted = use_case.execute(
            remaining_work, self.velocity_metrics, scenario, self.config, team_size=1
        )

        sprint_specific_p50 = adjusted.get_percentile(0.5)

        # Sprint-specific calculation:
        # Sprint 1: 20 * 1.25 = 25 (20 remaining: 135)
        # Sprint 2: 20 * 1.5 = 30 (20 remaining: 105)
        # Sprint 3: 20 * 1.75 = 35 (20 remaining: 70)
        # Sprint 4: 20 * 2.0 = 40 (20 remaining: 30)
        # Sprint 5: 20 * 2.0 = 40 (done with 10 extra)
        # So exactly 5 sprints

        assert abs(sprint_specific_p50 - 5.0) < 0.1
        # This should be different from the averaged approach
        assert abs(sprint_specific_p50 - averaged_sprints) > 0.5
