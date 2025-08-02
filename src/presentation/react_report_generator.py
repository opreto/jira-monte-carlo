"""React-based HTML report generator using Node.js builder"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import logging

from ..domain.forecasting import ModelInfo
from ..domain.entities import SimulationConfig, SimulationResult
from ..domain.value_objects import VelocityMetrics, HistoricalData
from ..application.style_service import StyleService

logger = logging.getLogger(__name__)


class ReactReportGenerator:
    """Generate HTML reports using React components via Node.js builder"""

    def __init__(
        self,
        style_service: Optional[StyleService] = None,
        theme_name: Optional[str] = None,
    ):
        self.style_service = style_service or StyleService()
        self.theme_name = theme_name
        self.report_builder_path = self._find_report_builder()

    def _find_report_builder(self) -> Path:
        """Find the report-builder CLI tool"""
        # Look for the report builder in the packages directory
        project_root = Path(__file__).parent.parent.parent
        report_builder = project_root / "packages" / "report-builder"

        # Check if it exists
        if not report_builder.exists():
            raise RuntimeError(
                f"Report builder not found at {report_builder}. "
                "Please ensure the report-builder package is installed."
            )

        return report_builder

    def generate(
        self,
        simulation_results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        historical_data: HistoricalData,
        remaining_work: float,
        config: SimulationConfig,
        output_path: Path,
        project_name: Optional[str] = None,
        model_info: Optional[ModelInfo] = None,
        **kwargs,
    ) -> Path:
        """
        Generate HTML report using React components

        Args:
            simulation_results: Simulation results to display
            velocity_metrics: Velocity metrics data
            historical_data: Historical sprint data
            remaining_work: Remaining work in story points
            config: Simulation configuration
            output_path: Path to save the report
            project_name: Name of the project
            model_info: Model information
            **kwargs: Additional data (process health, charts, etc.)

        Returns:
            Path to the generated report
        """
        # Prepare data for the React component
        report_data = self._prepare_report_data(
            simulation_results=simulation_results,
            velocity_metrics=velocity_metrics,
            historical_data=historical_data,
            remaining_work=remaining_work,
            config=config,
            project_name=project_name,
            model_info=model_info,
            **kwargs,
        )

        # Convert to JSON
        json_data = json.dumps(report_data, indent=2, default=str)

        # Log the processHealth data for debugging
        import json as json_module

        process_health_json = json_module.loads(json_data).get("processHealth", {})
        logger.info(
            f"ProcessHealth data being sent: score={process_health_json.get('score')}, breakdown={len(process_health_json.get('health_score_breakdown', []))} items"
        )

        # Debug: save full report data to file
        with open("reports/debug-full-report.json", "w") as f:
            json_module.dump(json_module.loads(json_data), f, indent=2)

        # Call the Node.js builder
        try:
            # Use npx to run the builder
            # Ensure output path is absolute
            absolute_output_path = Path(output_path).absolute()
            cmd = [
                "npx",
                "tsx",
                str(self.report_builder_path / "src" / "cli.ts"),
                "build",
                "-o",
                str(absolute_output_path),
            ]

            # Run the command with JSON data as stdin
            result = subprocess.run(
                cmd,
                input=json_data,
                text=True,
                capture_output=True,
                cwd=str(self.report_builder_path),
            )

            if result.returncode != 0:
                logger.error(f"Report builder failed: {result.stderr}")
                raise RuntimeError(f"Failed to generate report: {result.stderr}")

            logger.info(f"Report generated successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating React report: {e}")
            raise

    def _prepare_report_data(
        self,
        simulation_results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        historical_data: HistoricalData,
        remaining_work: float,
        config: SimulationConfig,
        project_name: Optional[str] = None,
        model_info: Optional[ModelInfo] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Prepare data for the React report component"""

        # Extract process health metrics
        process_health = kwargs.get("process_health_metrics", {})
        if hasattr(process_health, "__dict__"):
            process_health_dict = {
                "score": getattr(process_health, "health_score", 0)
                * 100,  # Convert to percentage
                "wipScore": getattr(process_health, "wip_score", 0),
                "sprintHealthScore": getattr(process_health, "sprint_health_score", 0),
                "flowEfficiencyScore": getattr(
                    process_health, "flow_efficiency_score", 0
                ),
                "leadTimeScore": getattr(process_health, "lead_time_score", 0),
                "defectRateScore": getattr(process_health, "defect_rate_score", 0),
                "blockedItemsScore": getattr(process_health, "blocked_items_score", 0),
            }

            # Add detailed health breakdown if available
            if hasattr(process_health, "health_score_breakdown"):
                breakdown = process_health.health_score_breakdown
                logger.info(f"Health breakdown has {len(breakdown)} components")
                if breakdown:
                    process_health_dict["health_score_breakdown"] = [
                        {
                            "name": comp.name,
                            "score": comp.score,
                            "description": comp.description,
                            "insights": comp.insights,
                            "recommendations": comp.recommendations,
                            "detail_items": comp.detail_items,
                        }
                        for comp in breakdown
                    ]
                    logger.info(
                        f"Serialized health breakdown: {process_health_dict['health_score_breakdown'][:1]}"
                    )  # Log first component
            if hasattr(process_health, "aging_analysis"):
                process_health_dict["aging_analysis"] = process_health.aging_analysis
            if hasattr(process_health, "wip_analysis"):
                process_health_dict["wip_analysis"] = process_health.wip_analysis
            if hasattr(process_health, "sprint_health"):
                process_health_dict["sprint_health"] = process_health.sprint_health
            if hasattr(process_health, "blocked_items"):
                process_health_dict["blocked_items"] = process_health.blocked_items
        else:
            process_health_dict = {
                "score": 0,
                "wipScore": 0,
                "sprintHealthScore": 0,
                "flowEfficiencyScore": 0,
                "leadTimeScore": 0,
                "defectRateScore": 0,
                "blockedItemsScore": 0,
            }

        # Prepare sprint data
        sprints = []
        for i in range(len(historical_data.sprint_names)):
            sprint = {
                "name": historical_data.sprint_names[i],
                "completedPoints": historical_data.velocities[i]
                if i < len(historical_data.velocities)
                else 0,
                "committedPoints": historical_data.velocities[i]
                if i < len(historical_data.velocities)
                else 0,  # We don't have committed data
            }
            if i < len(historical_data.dates) and historical_data.dates[i]:
                sprint["endDate"] = historical_data.dates[i].isoformat()
            sprints.append(sprint)

        # Prepare simulation results
        percentiles_dict = {}
        for level, value in simulation_results.percentiles.items():
            percentiles_dict[str(level)] = value

        # Extract additional data from kwargs
        reporting_capabilities = kwargs.get("reporting_capabilities")
        if reporting_capabilities and hasattr(reporting_capabilities, "__dict__"):
            reporting_capabilities_dict = {
                "available_reports": getattr(
                    reporting_capabilities, "available_reports", []
                ),
                "all_reports": getattr(reporting_capabilities, "all_reports", []),
                "unavailable_reports": getattr(
                    reporting_capabilities, "unavailable_reports", {}
                ),
                "data_quality_score": getattr(
                    reporting_capabilities, "data_quality_score", 0
                ),
            }
        else:
            reporting_capabilities_dict = None

        # Get charts data if passed from CLI
        charts_data = kwargs.get("charts_data", {})

        # Extract model info
        model_info_dict = None
        if model_info:
            model_info_dict = {
                "report_title": getattr(model_info, "report_title", None),
                "report_subtitle": getattr(model_info, "report_subtitle", None),
                "methodology_description": getattr(
                    model_info, "methodology_description", None
                ),
            }

        # Extract summary stats if available
        summary_stats = kwargs.get("summary_stats", {})

        # Extract ML decisions if available
        ml_decisions = kwargs.get("ml_decisions")
        ml_decisions_dict = None
        if ml_decisions and hasattr(ml_decisions, "decisions"):
            ml_decisions_dict = {
                "decisions": [
                    {
                        "decision_type": decision.decision_type,
                        "method": decision.method,
                        "value": decision.value,
                        "model_name": decision.model_name,
                        "reasoning": getattr(decision, "reasoning", None),
                        "confidence": getattr(decision, "confidence", None),
                        "details": getattr(decision, "details", None),
                    }
                    for decision in ml_decisions.decisions
                ]
            }

        # Check for combined scenario data
        combined_scenario_data = kwargs.get("combined_scenario_data")
        scenario_banner = kwargs.get("scenario_banner")
        baseline_charts = kwargs.get("baseline_charts_data", {})
        adjusted_charts = kwargs.get("adjusted_charts_data", {})

        # When we have scenario charts, use the appropriate normalized charts for initial render
        # Default to adjusted view to match the combined_scenario_data default
        if baseline_charts and adjusted_charts:
            # Use adjusted charts as the default view
            # Merge with health charts from charts_data (velocity trend, aging, etc.)
            initial_charts = {**charts_data, **adjusted_charts}
        else:
            # Fall back to regular charts if no scenario charts
            initial_charts = charts_data

        report_data = {
            "projectName": project_name or "Sprint Radar Project",
            "generatedAt": kwargs.get("generated_at", datetime.now().isoformat()),
            "remainingWork": remaining_work,
            "velocityMetrics": {
                "average": velocity_metrics.average,
                "median": velocity_metrics.median,
                "stdDev": velocity_metrics.std_dev,
                "min": velocity_metrics.min_value,
                "max": velocity_metrics.max_value,
                "trend": velocity_metrics.trend,
            },
            "simulationResults": {
                "percentiles": percentiles_dict,
            },
            "processHealth": process_health_dict,
            "sprints": sprints,
            "charts": initial_charts,
            "jql_query": kwargs.get("jql_query"),
            "jql_queries": kwargs.get("jql_queries"),
            "jira_url": kwargs.get("jira_url"),
            "velocity_field": kwargs.get("velocity_field", "story_points"),
            "model_info": model_info_dict,
            "num_simulations": config.num_simulations,
            "reporting_capabilities": reporting_capabilities_dict,
            "summary_stats": summary_stats,
            "ml_decisions": ml_decisions_dict,
        }

        # Add combined scenario data if present
        if combined_scenario_data:
            report_data["combinedScenarioData"] = json.loads(combined_scenario_data)
            report_data["scenarioBanner"] = scenario_banner

            # Add scenario-specific charts if available
            if baseline_charts and adjusted_charts:
                # Merge health charts with scenario-specific charts
                report_data["scenarioCharts"] = {
                    "baseline": {**charts_data, **baseline_charts},
                    "adjusted": {**charts_data, **adjusted_charts},
                }

        return report_data

    def _calculate_summary_stats(
        self,
        results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        config: SimulationConfig,
    ) -> Dict:
        """Calculate summary statistics for display"""
        if not results:
            return {}

        today = datetime.now()
        summary = {}

        # Calculate sprint duration based on historical data
        sprint_duration = config.sprint_duration_days or 14  # Default to 14 days

        for level in [0.5, 0.7, 0.85, 0.95]:
            sprints = results.percentiles.get(level, 0)
            days = sprints * sprint_duration
            completion_date = today + timedelta(days=days)

            summary[f"{int(level * 100)}%"] = {
                "sprints": int(sprints),
                "date": completion_date.strftime("%Y-%m-%d"),
                "probability": f"{int(level * 100)}",
                "class": self._get_confidence_class(level),
            }

        return summary

    def _get_confidence_class(self, level: float) -> str:
        """Get CSS class for confidence level"""
        if level <= 0.5:
            return "aggressive"
        elif level <= 0.7:
            return "moderate"
        elif level <= 0.85:
            return "recommended"
        else:
            return "conservative"

    def _create_chart_dict(self, chart_json: str) -> Dict[str, Any]:
        """Convert chart JSON string to dict for React component"""
        import json

        try:
            chart_data = json.loads(chart_json)
            # Extract data and layout from Plotly figure structure
            return {
                "data": chart_data.get("data", []),
                "layout": chart_data.get("layout", {}),
            }
        except (json.JSONDecodeError, TypeError):
            # Return empty chart if parsing fails
            return {"data": [], "layout": {}}
