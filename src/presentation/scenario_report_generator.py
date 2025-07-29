"""Generate linked baseline/adjusted reports for velocity scenarios"""

import logging
from pathlib import Path
from typing import Tuple

from ..domain.entities import SimulationConfig, SimulationResult
from ..domain.forecasting import ModelInfo
from ..domain.value_objects import VelocityMetrics
from ..domain.velocity_adjustments import ScenarioComparison, VelocityScenario
from .report_generator import HTMLReportGenerator

logger = logging.getLogger(__name__)


class ScenarioReportGenerator:
    """Generate linked baseline/adjusted reports"""

    def __init__(self, base_generator: HTMLReportGenerator):
        self.base_generator = base_generator

    def generate_reports(
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
    ) -> Tuple[Path, Path]:
        """Generate both baseline and adjusted reports with cross-links"""
        # Generate filenames
        base_name = output_path.stem
        suffix = output_path.suffix
        parent_dir = output_path.parent

        baseline_path = parent_dir / f"{base_name}-baseline{suffix}"
        adjusted_path = parent_dir / f"{base_name}-adjusted{suffix}"

        # Generate baseline report
        logger.info(f"Generating baseline report: {baseline_path}")
        self.base_generator.generate(
            simulation_results=baseline_results,
            velocity_metrics=velocity_metrics,
            historical_data=historical_data,
            remaining_work=remaining_work,
            config=config,
            output_path=baseline_path,
            project_name=project_name,
            model_info=model_info,
            scenario_banner=self._create_baseline_banner(adjusted_path),
            **kwargs,
        )

        # Generate adjusted report
        logger.info(f"Generating adjusted report: {adjusted_path}")
        self.base_generator.generate(
            simulation_results=adjusted_results,
            velocity_metrics=velocity_metrics,
            historical_data=historical_data,
            remaining_work=remaining_work,
            config=config,
            output_path=adjusted_path,
            project_name=project_name,
            model_info=model_info,
            scenario_banner=self._create_adjusted_banner(scenario, comparison, baseline_path),
            **kwargs,
        )

        return baseline_path, adjusted_path

    def _create_baseline_banner(self, adjusted_path: Path) -> str:
        """Create banner for baseline report"""
        adjusted_link = adjusted_path.name
        return f"""
        <div class="scenario-banner baseline-banner">
            <h3>📊 Baseline Forecast</h3>
            <p>This is the baseline forecast without any velocity adjustments.</p>
            <p><a href="{adjusted_link}" class="scenario-link">View Adjusted Forecast →</a></p>
        </div>
        """

    def _create_adjusted_banner(
        self, scenario: VelocityScenario, comparison: ScenarioComparison, baseline_path: Path
    ) -> str:
        """Create banner for adjusted report"""
        baseline_link = baseline_path.name
        scenario_desc = scenario.get_summary()
        impact_desc = comparison.get_impact_summary()

        return f"""
        <div class="scenario-banner adjusted-banner">
            <h3>🔧 Adjusted Forecast</h3>
            <p><strong>Scenario:</strong> {scenario_desc}</p>
            <p><strong>Impact:</strong> {impact_desc}</p>
            <p><a href="{baseline_link}" class="scenario-link">← View Baseline Forecast</a></p>
        </div>
        """

    def _add_chart_disclaimer(self, chart_html: str, scenario: VelocityScenario) -> str:
        """Add disclaimer to velocity-related charts"""
        # This would be implemented to inject disclaimers into specific charts
        # For now, we'll rely on the banner
        return chart_html
