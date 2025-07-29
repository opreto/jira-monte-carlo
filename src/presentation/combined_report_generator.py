"""Generate combined baseline/adjusted reports for velocity scenarios"""

import json
import logging
from pathlib import Path
from typing import Dict, Any

from ..domain.entities import SimulationConfig, SimulationResult
from ..domain.forecasting import ModelInfo
from ..domain.value_objects import VelocityMetrics
from ..domain.velocity_adjustments import ScenarioComparison, VelocityScenario
from .report_generator import HTMLReportGenerator
from .templates import ReportTemplates

logger = logging.getLogger(__name__)


class CombinedReportGenerator:
    """Generate a single HTML report with both baseline and adjusted forecasts"""

    def __init__(self, base_generator: HTMLReportGenerator):
        self.base_generator = base_generator
        self.templates = ReportTemplates()

    def generate_combined_report(
        self,
        baseline_results: SimulationResult,
        adjusted_results: SimulationResult,
        scenario: VelocityScenario,
        comparison: ScenarioComparison,
        velocity_metrics: VelocityMetrics,
        historical_data: list,
        remaining_work: float,
        config: SimulationConfig,
        output_path: Path,
        project_name: str,
        model_info: ModelInfo,
        **kwargs,
    ) -> Path:
        """Generate a single report with both baseline and adjusted data"""
        logger.info(f"Generating combined baseline/adjusted report: {output_path}")

        # Prepare data for both scenarios
        baseline_data = self._prepare_chart_data(
            baseline_results,
            velocity_metrics,
            historical_data,
            remaining_work,
            config,
            "baseline"
        )
        
        adjusted_data = self._prepare_chart_data(
            adjusted_results,
            velocity_metrics,
            historical_data,
            remaining_work,
            config,
            "adjusted"
        )

        # Generate the combined report
        scenario_info = {
            "description": scenario.get_summary(),
            "comparison": comparison.get_impact_summary(),
            "adjustments": [adj.get_description() for adj in scenario.adjustments],
            "team_changes": [tc.get_description() for tc in scenario.team_changes]
        }

        # Use the base generator but with modified data
        combined_data = {
            "baseline": baseline_data,
            "adjusted": adjusted_data,
            "scenario": scenario_info,
            "current_view": "adjusted"  # Default to showing adjusted view
        }

        # Generate the report with combined data
        self.base_generator.generate(
            simulation_results=adjusted_results,  # Use adjusted as primary
            velocity_metrics=velocity_metrics,
            historical_data=historical_data,
            remaining_work=remaining_work,
            config=config,
            output_path=output_path,
            project_name=project_name,
            model_info=model_info,
            combined_scenario_data=json.dumps(combined_data),
            scenario_banner=self._create_combined_banner(scenario, comparison),
            **kwargs,
        )

        return output_path

    def _prepare_chart_data(
        self,
        results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        historical_data: list,
        remaining_work: float,
        config: SimulationConfig,
        label: str
    ) -> Dict[str, Any]:
        """Prepare chart data for a single scenario"""
        # Extract key metrics
        percentiles = results.percentiles
        completion_sprints = results.completion_sprints[:1000] if results.completion_sprints else []
        
        # Prepare probability distribution data
        prob_data = []
        if results.probability_distribution:
            for sprint, prob in results.probability_distribution:
                prob_data.append({"sprint": sprint, "probability": prob})

        # Prepare confidence intervals
        confidence_data = []
        for level, (lower, upper) in results.confidence_intervals.items():
            confidence_data.append({
                "level": int(level * 100),
                "lower": lower,
                "upper": upper,
                "value": percentiles.get(level, 0)
            })

        return {
            "label": label,
            "percentiles": {
                "p50": percentiles.get(0.5, 0),
                "p70": percentiles.get(0.7, 0),
                "p85": percentiles.get(0.85, 0),
                "p95": percentiles.get(0.95, 0)
            },
            "completion_sprints": completion_sprints,
            "probability_distribution": prob_data,
            "confidence_intervals": confidence_data,
            "mean_completion": results.mean_completion_date.isoformat() if results.mean_completion_date else None,
            "std_dev_days": results.std_dev_days
        }

    def _create_combined_banner(self, scenario: VelocityScenario, comparison: ScenarioComparison) -> str:
        """Create banner for combined report with toggle"""
        scenario_desc = scenario.get_summary()
        impact_desc = comparison.get_impact_summary()
        
        return f"""
        <div class="scenario-banner combined-banner">
            <div class="scenario-header">
                <h3>📊 Velocity Scenario Analysis</h3>
                <div class="scenario-toggle">
                    <label class="toggle-label">
                        <input type="radio" name="scenario-view" value="baseline" 
                               onclick="switchScenario('baseline')">
                        Baseline
                    </label>
                    <label class="toggle-label">
                        <input type="radio" name="scenario-view" value="adjusted" 
                               onclick="switchScenario('adjusted')" checked>
                        Adjusted
                    </label>
                </div>
            </div>
            <div id="scenario-description" class="scenario-description">
                <p><strong>Scenario:</strong> {scenario_desc}</p>
                <p><strong>Impact:</strong> {impact_desc}</p>
            </div>
            <div id="baseline-notice" class="baseline-notice" style="display: none;">
                <p>This is the baseline forecast without any velocity adjustments.</p>
            </div>
        </div>
        """
