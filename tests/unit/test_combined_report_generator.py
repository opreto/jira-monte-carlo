"""Test combined report generator"""

import json
from unittest.mock import Mock

from src.domain.entities import SimulationConfig, SimulationResult
from src.domain.value_objects import VelocityMetrics
from src.domain.velocity_adjustments import (
    ScenarioComparison,
    VelocityAdjustment,
    VelocityScenario,
)
from src.presentation.combined_report_generator import CombinedReportGenerator


class TestCombinedReportGenerator:
    def test_generate_combined_report(self, tmp_path):
        # Mock dependencies
        mock_base_generator = Mock()
        mock_base_generator.generate.return_value = tmp_path / "report.html"

        # Mock the _calculate_summary_stats method to return a proper dict
        mock_base_generator._calculate_summary_stats.return_value = {
            "50%": {
                "class": "confidence-moderate",
                "sprints": 10,
                "date": "2024-03-15",
                "probability": 50,
            },
            "85%": {
                "class": "confidence-conservative",
                "sprints": 15,
                "date": "2024-04-15",
                "probability": 85,
            },
        }

        generator = CombinedReportGenerator(mock_base_generator)

        # Create test data
        baseline_results = SimulationResult(
            percentiles={0.5: 10, 0.7: 12, 0.85: 15, 0.95: 20},
            mean_completion_date=None,
            std_dev_days=5.0,
            probability_distribution=[(8, 0.1), (10, 0.4), (12, 0.3), (15, 0.2)],
            completion_dates=[],
            confidence_intervals={0.5: (8, 12), 0.85: (12, 18)},
            completion_sprints=[8, 9, 10, 10, 11, 12],
        )

        adjusted_results = SimulationResult(
            percentiles={0.5: 12, 0.7: 14, 0.85: 17, 0.95: 22},
            mean_completion_date=None,
            std_dev_days=6.0,
            probability_distribution=[(10, 0.1), (12, 0.4), (14, 0.3), (17, 0.2)],
            completion_dates=[],
            confidence_intervals={0.5: (10, 14), 0.85: (14, 20)},
            completion_sprints=[10, 11, 12, 12, 13, 14],
        )

        scenario = VelocityScenario(
            name="Test Scenario",
            adjustments=[
                VelocityAdjustment(
                    sprint_start=5, sprint_end=7, factor=0.7, reason="vacation"
                )
            ],
            team_changes=[],
        )

        comparison = ScenarioComparison(
            baseline_p50_sprints=10,
            baseline_p85_sprints=15,
            adjusted_p50_sprints=12,
            adjusted_p85_sprints=17,
            velocity_impact_percentage=-20.0,
            scenario_description="Test scenario with vacation",
        )

        velocity_metrics = VelocityMetrics(
            average=20.0,
            median=20.0,
            std_dev=5.0,
            min_value=10.0,
            max_value=30.0,
            trend=0.1,
        )

        config = SimulationConfig(
            num_simulations=1000,
            velocity_field="story_points",
            done_statuses=["Done"],
            in_progress_statuses=["In Progress"],
            todo_statuses=["To Do"],
        )

        # Generate report
        output_path = tmp_path / "combined_report.html"
        generator.generate_combined_report(
            baseline_results=baseline_results,
            adjusted_results=adjusted_results,
            scenario=scenario,
            comparison=comparison,
            velocity_metrics=velocity_metrics,
            historical_data=[],
            remaining_work=100.0,
            config=config,
            output_path=output_path,
            project_name="Test Project",
            model_info=None,
        )

        # Verify the generate method was called with correct parameters
        assert mock_base_generator.generate.called
        call_args = mock_base_generator.generate.call_args

        # Check that combined_scenario_data was passed
        assert "combined_scenario_data" in call_args.kwargs

        # Parse and verify the combined data structure
        combined_data = json.loads(call_args.kwargs["combined_scenario_data"])
        assert "baseline" in combined_data
        assert "adjusted" in combined_data
        assert "scenario" in combined_data
        assert combined_data["current_view"] == "adjusted"

        # Verify baseline data
        assert combined_data["baseline"]["percentiles"]["p50"] == 10
        assert combined_data["baseline"]["percentiles"]["p85"] == 15

        # Verify adjusted data
        assert combined_data["adjusted"]["percentiles"]["p50"] == 12
        assert combined_data["adjusted"]["percentiles"]["p85"] == 17

        # Verify scenario info
        assert len(combined_data["scenario"]["adjustments"]) == 1
        assert "vacation" in combined_data["scenario"]["adjustments"][0]

    def test_combined_banner_html(self):
        # Test the banner HTML generation
        generator = CombinedReportGenerator(Mock())

        scenario = VelocityScenario(
            name="Test",
            adjustments=[
                VelocityAdjustment(
                    sprint_start=1, sprint_end=3, factor=0.8, reason="holidays"
                )
            ],
            team_changes=[],
        )

        comparison = ScenarioComparison(
            baseline_p50_sprints=10,
            baseline_p85_sprints=15,
            adjusted_p50_sprints=12,
            adjusted_p85_sprints=18,
            velocity_impact_percentage=-20.0,
            scenario_description="Holiday impact",
        )

        banner_html = generator._create_combined_banner(scenario, comparison)

        # Check key elements are present
        assert "scenario-banner combined-banner" in banner_html
        assert "scenario-toggle" in banner_html
        assert 'name="scenario-view"' in banner_html
        assert 'value="baseline"' in banner_html
        assert 'value="adjusted"' in banner_html
        assert "switchScenario" in banner_html
        assert scenario.get_summary() in banner_html
        assert comparison.get_impact_summary() in banner_html
