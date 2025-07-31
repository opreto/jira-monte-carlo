"""Tests for velocity adjustment functionality"""

import pytest

from src.domain.velocity_adjustments import (
    ProductivityCurve,
    ScenarioComparison,
    TeamChange,
    VelocityAdjustment,
    VelocityScenario,
)
from src.infrastructure.velocity_adjustment_parser import VelocityAdjustmentParser


class TestVelocityAdjustment:
    """Test velocity adjustment domain model"""

    def test_single_sprint_adjustment(self):
        """Test adjustment for a single sprint"""
        adj = VelocityAdjustment(
            sprint_start=3, sprint_end=3, factor=0.5, reason="vacation"
        )

        assert not adj.applies_to_sprint(2)
        assert adj.applies_to_sprint(3)
        assert not adj.applies_to_sprint(4)
        assert adj.get_description() == "50% capacity for sprint +2 (vacation)"

    def test_sprint_range_adjustment(self):
        """Test adjustment for a sprint range"""
        adj = VelocityAdjustment(
            sprint_start=5, sprint_end=7, factor=0.7, reason="summer holidays"
        )

        assert not adj.applies_to_sprint(4)
        assert adj.applies_to_sprint(5)
        assert adj.applies_to_sprint(6)
        assert adj.applies_to_sprint(7)
        assert not adj.applies_to_sprint(8)
        assert (
            adj.get_description()
            == "70% capacity for sprint +4 through sprint +6 (summer holidays)"
        )

    def test_forever_adjustment(self):
        """Test adjustment that applies forever"""
        adj = VelocityAdjustment(
            sprint_start=10, sprint_end=None, factor=1.2, reason="process improvements"
        )  # Forever

        assert not adj.applies_to_sprint(9)
        assert adj.applies_to_sprint(10)
        assert adj.applies_to_sprint(100)
        assert adj.applies_to_sprint(1000)
        assert (
            adj.get_description()
            == "120% capacity for from sprint +9 onwards (process improvements)"
        )


class TestTeamChange:
    """Test team change domain model"""

    def test_team_addition_linear_ramp(self):
        """Test adding team member with linear ramp-up"""
        change = TeamChange(
            sprint=4,
            change=1,
            ramp_up_sprints=4,
            productivity_curve=ProductivityCurve.LINEAR,
        )

        # Before ramp-up complete
        assert change.get_productivity_factor(0) == 0.25  # Sprint 4: 25%
        assert change.get_productivity_factor(1) == 0.4375  # Sprint 5: ~44%
        assert change.get_productivity_factor(2) == 0.625  # Sprint 6: 62.5%
        assert change.get_productivity_factor(3) == 0.8125  # Sprint 7: ~81%

        # After ramp-up
        assert change.get_productivity_factor(4) == 1.0  # Sprint 8: 100%
        assert change.get_productivity_factor(10) == 1.0  # Still 100%

        desc = change.get_description()
        assert "Adding 1 developer" in desc
        assert "starting sprint +3" in desc
        assert "ramp-up: 4 sprints" in desc

    def test_team_reduction(self):
        """Test removing team members"""
        change = TeamChange(
            sprint=8, change=-2, ramp_up_sprints=0
        )  # No ramp-up for departures

        # Always full productivity impact for departures
        assert change.get_productivity_factor(0) == 1.0
        assert change.get_productivity_factor(10) == 1.0

        desc = change.get_description()
        assert "Removing 2 developers" in desc
        assert "after sprint +7" in desc

    def test_exponential_ramp_up(self):
        """Test exponential productivity curve"""
        change = TeamChange(
            sprint=1,
            change=1,
            ramp_up_sprints=3,
            productivity_curve=ProductivityCurve.EXPONENTIAL,
        )

        # Exponential starts slower, accelerates
        assert change.get_productivity_factor(0) == 0.25  # 25%
        assert 0.25 < change.get_productivity_factor(1) < 0.6  # Between 25% and 60%
        assert change.get_productivity_factor(3) == 1.0  # 100%

    def test_step_productivity_curve(self):
        """Test step function productivity curve"""
        change = TeamChange(
            sprint=1,
            change=1,
            ramp_up_sprints=4,
            productivity_curve=ProductivityCurve.STEP,
        )

        # Step function: 25%, 50%, 75%, 100%
        assert change.get_productivity_factor(0) == 0.25
        assert change.get_productivity_factor(1) == 0.5
        assert change.get_productivity_factor(2) == 0.75
        assert change.get_productivity_factor(3) == 1.0  # 100% at completion
        assert change.get_productivity_factor(4) == 1.0


class TestVelocityScenario:
    """Test velocity scenario calculations"""

    def test_scenario_with_adjustments_only(self):
        """Test scenario with only velocity adjustments"""
        adjustments = [
            VelocityAdjustment(3, 3, 0.5, "vacation"),
            VelocityAdjustment(10, None, 1.1, "improvements"),
        ]

        scenario = VelocityScenario(
            name="Test Scenario", adjustments=adjustments, team_changes=[]
        )

        base_velocity = 20.0
        team_size = 5

        # Sprint 2: No adjustments
        velocity, reason = scenario.get_adjusted_velocity(2, base_velocity, team_size)
        assert velocity == 20.0
        assert reason == "No adjustments"

        # Sprint 3: 50% capacity
        velocity, reason = scenario.get_adjusted_velocity(3, base_velocity, team_size)
        assert velocity == 10.0
        assert "50% capacity" in reason

        # Sprint 10: 110% capacity
        velocity, reason = scenario.get_adjusted_velocity(10, base_velocity, team_size)
        assert velocity == 22.0
        assert "110% capacity" in reason

    def test_scenario_with_team_changes(self):
        """Test scenario with team changes"""
        team_changes = [
            TeamChange(4, 1, 2),  # Add 1 person at sprint 4
        ]

        scenario = VelocityScenario(
            name="Scaling", adjustments=[], team_changes=team_changes
        )

        base_velocity = 20.0
        team_size = 4

        # Sprint 4: New person at 25% productivity
        # Team factor = (4 + 1*0.25) / 4 = 4.25/4 = 1.0625
        velocity, reason = scenario.get_adjusted_velocity(4, base_velocity, team_size)
        assert abs(velocity - 21.25) < 0.01
        assert "25% productivity" in reason

        # Sprint 6: New person at 100% productivity
        # Team factor = (4 + 1*1.0) / 4 = 5/4 = 1.25
        velocity, reason = scenario.get_adjusted_velocity(6, base_velocity, team_size)
        assert velocity == 25.0
        assert "Team scaled up by 1" in reason

    def test_scenario_summary(self):
        """Test scenario summary generation"""
        scenario = VelocityScenario(
            name="Complex",
            adjustments=[
                VelocityAdjustment(2, 3, 0.8, "holidays"),
                VelocityAdjustment(10, None, 1.1, "improvements"),
            ],
            team_changes=[
                TeamChange(5, 2, 3),
                TeamChange(15, -1, 0),
            ],
        )

        summary = scenario.get_summary(team_size=4)
        assert "80% capacity for next 2 sprints (holidays)" in summary
        assert "110% capacity for from sprint +9 onwards (improvements)" in summary
        assert "Adding 2 developers (+50% capacity after ramp-up)" in summary
        assert "Reducing team by 1.0 FTE (-25% capacity)" in summary

    def test_scenario_summary_with_fractional_team(self):
        """Test scenario summary with part-time team member"""
        scenario = VelocityScenario(
            name="Part-time addition",
            adjustments=[],
            team_changes=[
                TeamChange(1, 0.5, 3),  # Add 0.5 FTE
            ],
        )

        summary = scenario.get_summary(team_size=2)
        assert "Adding part-time developer (+25% capacity after ramp-up)" in summary


class TestVelocityAdjustmentParser:
    """Test CLI argument parsing"""

    def test_parse_velocity_change_single_sprint(self):
        """Test parsing single sprint velocity change"""
        parser = VelocityAdjustmentParser()
        adj = parser.parse_velocity_change("sprint:3,factor:0.5,reason:vacation")

        assert adj.sprint_start == 3
        assert adj.sprint_end == 3
        assert adj.factor == 0.5
        assert adj.reason == "vacation"

    def test_parse_velocity_change_range(self):
        """Test parsing sprint range velocity change"""
        parser = VelocityAdjustmentParser()
        adj = parser.parse_velocity_change("sprint:5-7,factor:0.7")

        assert adj.sprint_start == 5
        assert adj.sprint_end == 7
        assert adj.factor == 0.7
        assert adj.reason is None

    def test_parse_velocity_change_forever(self):
        """Test parsing forever velocity change"""
        parser = VelocityAdjustmentParser()
        adj = parser.parse_velocity_change("sprint:10+,factor:1.2,reason:new-process")

        assert adj.sprint_start == 10
        assert adj.sprint_end is None
        assert adj.factor == 1.2
        assert adj.reason == "new-process"

    def test_parse_team_change_addition(self):
        """Test parsing team addition"""
        parser = VelocityAdjustmentParser()
        change = parser.parse_team_change("sprint:4,change:+1")

        assert change.sprint == 4
        assert change.change == 1
        assert change.ramp_up_sprints == 3  # Default
        assert change.productivity_curve == ProductivityCurve.LINEAR

    def test_parse_team_change_reduction(self):
        """Test parsing team reduction"""
        parser = VelocityAdjustmentParser()
        change = parser.parse_team_change("sprint:8,change:-2")

        assert change.sprint == 8
        assert change.change == -2
        assert change.ramp_up_sprints == 0  # No ramp for departures

    def test_parse_team_change_with_options(self):
        """Test parsing team change with all options"""
        parser = VelocityAdjustmentParser()
        change = parser.parse_team_change("sprint:6,change:+2,ramp:4,curve:exponential")

        assert change.sprint == 6
        assert change.change == 2
        assert change.ramp_up_sprints == 4
        assert change.productivity_curve == ProductivityCurve.EXPONENTIAL

    def test_parse_fractional_team_change(self):
        """Test parsing fractional team member (part-time)"""
        parser = VelocityAdjustmentParser()
        change = parser.parse_team_change("sprint:1,change:+0.5,ramp:3")

        assert change.sprint == 1
        assert change.change == 0.5
        assert change.ramp_up_sprints == 3
        assert change.productivity_curve == ProductivityCurve.LINEAR

    def test_parse_invalid_formats(self):
        """Test parsing invalid formats raises errors"""
        parser = VelocityAdjustmentParser()

        # Missing required fields
        with pytest.raises(
            ValueError, match="Invalid velocity change format.*Expected:"
        ):
            parser.parse_velocity_change("factor:0.5")

        with pytest.raises(
            ValueError, match="Invalid velocity change format.*Expected:"
        ):
            parser.parse_velocity_change("sprint:3")

        with pytest.raises(ValueError, match="Invalid team change format.*Expected:"):
            parser.parse_team_change("sprint:4")

        # Invalid values
        with pytest.raises(ValueError):
            parser.parse_velocity_change("sprint:3,factor:0")  # Factor must be positive

        with pytest.raises(ValueError):
            parser.parse_team_change("sprint:4,change:0")  # Change must be non-zero


class TestScenarioComparison:
    """Test scenario comparison"""

    def test_comparison_with_delay(self):
        """Test comparison showing delay"""
        comparison = ScenarioComparison(
            baseline_p50_sprints=10,
            baseline_p85_sprints=13,
            adjusted_p50_sprints=12,
            adjusted_p85_sprints=16,
            velocity_impact_percentage=-15.0,
            scenario_description="Team reduction",
        )

        summary = comparison.get_impact_summary()
        assert "2 sprints delay at 50% confidence" in summary
        assert "3 sprints delay at 85% confidence" in summary

    def test_comparison_with_improvement(self):
        """Test comparison showing improvement"""
        comparison = ScenarioComparison(
            baseline_p50_sprints=15,
            baseline_p85_sprints=20,
            adjusted_p50_sprints=12,
            adjusted_p85_sprints=16,
            velocity_impact_percentage=20.0,
            scenario_description="Team scaling",
        )

        summary = comparison.get_impact_summary()
        assert "3 sprints earlier at 50% confidence" in summary
        assert "4 sprints earlier at 85% confidence" in summary

    def test_comparison_no_impact(self):
        """Test comparison with no impact"""
        comparison = ScenarioComparison(
            baseline_p50_sprints=10,
            baseline_p85_sprints=13,
            adjusted_p50_sprints=10,
            adjusted_p85_sprints=13,
            velocity_impact_percentage=0.0,
            scenario_description="No changes",
        )

        summary = comparison.get_impact_summary()
        assert summary == "No significant impact on timeline"
