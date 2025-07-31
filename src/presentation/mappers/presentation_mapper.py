"""Aggregated presentation mapper that coordinates all specialized mappers"""

from typing import Dict, List, Any, Optional
from pathlib import Path

from .view_model_mapper import ViewModelMapper
from .chart_mapper import ChartMapper
from .request_response_mapper import RequestResponseMapper
from .entity_mapper import EntityMapper

from ..models.view_models import ReportViewModel, DashboardViewModel
from ..models.requests import ForecastRequest, ReportRequest
from ..models.responses import ForecastResponse, ReportResponse

from ...domain.value_objects import VelocityMetrics, HistoricalData
from ...domain.process_health import ProcessHealthMetrics
from ...domain.forecasting import ForecastResult, ModelType


class PresentationMapper:
    """Main mapper that coordinates all presentation layer mappings"""

    def __init__(self):
        """Initialize with all specialized mappers"""
        self.view_model_mapper = ViewModelMapper()
        self.chart_mapper = ChartMapper()
        self.request_response_mapper = RequestResponseMapper()
        self.entity_mapper = EntityMapper()

    def create_full_report_view_model(
        self,
        project_name: str,
        forecast_result: ForecastResult,
        velocity_metrics: VelocityMetrics,
        historical_data: HistoricalData,
        health_metrics: Optional[ProcessHealthMetrics] = None,
        report_request: Optional[ReportRequest] = None,
    ) -> ReportViewModel:
        """Create complete report view model from domain objects

        Args:
            project_name: Project name
            forecast_result: Forecast results
            velocity_metrics: Velocity metrics
            historical_data: Historical data
            health_metrics: Optional health metrics
            report_request: Optional report request for preferences

        Returns:
            Complete report view model
        """
        # Get simulation result (using Monte Carlo as default)
        sim_result = forecast_result.simulation_results.get(
            ModelType.MONTE_CARLO, list(forecast_result.simulation_results.values())[0]
        )
        sim_config = forecast_result.simulation_config

        # Create base report
        report_vm = ReportViewModel(
            title="Sprint Radar Analytics Report",
            subtitle=f"Forecast Analysis for {project_name}",
            project_name=project_name,
            theme_name=report_request.theme if report_request else "opreto",
        )

        # Add metadata from request
        if report_request:
            report_vm.has_jql_query = bool(report_request.jql_query)
            report_vm.jql_query = report_request.jql_query
            report_vm.jira_url = report_request.jira_url

        # Create forecast summary
        forecast_summary = self.view_model_mapper.create_forecast_summary(
            project_name, sim_config, sim_result, velocity_metrics
        )

        # Add metric cards
        report_vm.metric_cards = forecast_summary.summary_cards

        # Create charts
        chart_preferences = (
            self.request_response_mapper.extract_chart_preferences(report_request)
            if report_request
            else {
                "probability_distribution": True,
                "confidence_intervals": True,
                "velocity_trend": True,
            }
        )

        if chart_preferences.get("probability_distribution"):
            report_vm.charts["probability_distribution"] = (
                self.chart_mapper.create_probability_distribution_chart(sim_result)
            )

        if chart_preferences.get("confidence_intervals"):
            report_vm.charts["confidence_intervals"] = (
                self.chart_mapper.create_confidence_intervals_chart(sim_result)
            )

        if chart_preferences.get("velocity_trend"):
            report_vm.charts["velocity_trend"] = (
                self.chart_mapper.create_velocity_trend_chart(
                    historical_data, velocity_metrics
                )
            )

        # Create summary table
        report_vm.summary_table = self.view_model_mapper.create_summary_table(
            sim_result, sim_config.sprint_length
        )

        # Add health metrics if available
        if health_metrics and report_request and report_request.include_health_metrics:
            report_vm.has_health_metrics = True
            report_vm.health_score = self.view_model_mapper.create_health_score(
                health_metrics
            )

            # Add health charts
            report_vm.health_charts["health_gauge"] = (
                self.chart_mapper.create_health_gauge_chart(health_metrics)
            )

            if health_metrics.aging_analysis:
                report_vm.health_charts["aging_distribution"] = (
                    self.chart_mapper.create_aging_chart(health_metrics.aging_analysis)
                )

            if health_metrics.wip_analysis:
                report_vm.health_charts["wip_by_status"] = (
                    self.chart_mapper.create_wip_by_status_chart(
                        health_metrics.wip_analysis
                    )
                )

            if health_metrics.sprint_health:
                report_vm.health_charts["sprint_completion"] = (
                    self.chart_mapper.create_sprint_completion_chart(
                        health_metrics.sprint_health
                    )
                )

        # Add methodology description
        report_vm.methodology_description = f"Monte Carlo simulation with {forecast_result.monte_carlo_config.num_simulations:,} iterations"
        report_vm.simulation_count = str(
            forecast_result.monte_carlo_config.num_simulations
        )

        return report_vm

    def create_dashboard_view_model(
        self, projects: List[Dict[str, Any]]
    ) -> DashboardViewModel:
        """Create dashboard view model for multiple projects

        Args:
            projects: List of project data dictionaries

        Returns:
            Dashboard view model
        """
        dashboard = DashboardViewModel(
            title="Sprint Radar Multi-Project Dashboard",
            subtitle=f"Tracking {len(projects)} projects",
        )

        # Calculate summary metrics
        total_remaining = sum(p.get("remaining_work", 0) for p in projects)
        avg_velocity = (
            sum(p.get("velocity", 0) for p in projects) / len(projects)
            if projects
            else 0
        )
        at_risk_count = sum(1 for p in projects if p.get("risk_level") == "high")

        # Create summary cards
        dashboard.summary_cards = [
            self.view_model_mapper.create_metric_card(
                "Total Projects", len(projects), color="primary"
            ),
            self.view_model_mapper.create_metric_card(
                "Total Remaining Work", total_remaining, "points", color="info"
            ),
            self.view_model_mapper.create_metric_card(
                "Average Velocity", avg_velocity, "points/sprint", color="success"
            ),
            self.view_model_mapper.create_metric_card(
                "At Risk Projects",
                at_risk_count,
                color="warning" if at_risk_count > 0 else "success",
            ),
        ]

        # Create project table
        dashboard.project_table_headers = [
            "Project",
            "Remaining Work",
            "Velocity",
            "85% Confidence",
            "Health Score",
            "Risk Level",
        ]

        # Add project rows
        for project in projects:
            cells = [
                project.get("name", "Unknown"),
                f"{project.get('remaining_work', 0):.0f} points",
                f"{project.get('velocity', 0):.1f} pts/sprint",
                f"{project.get('confidence_85', 0)} sprints",
                f"{project.get('health_score', 0):.0f}%",
                project.get("risk_level", "unknown").title(),
            ]

            row_class = "risk-high" if project.get("risk_level") == "high" else None

            dashboard.project_table_rows.append(
                self.view_model_mapper.create_table_row(cells, row_class)
            )

        # Create project links
        for project in projects:
            name = project.get("name", "Unknown")
            report_path = project.get("report_path")
            if report_path:
                dashboard.project_links[name] = f"file://{report_path}"

        return dashboard

    def map_forecast_to_response(
        self,
        forecast_result: ForecastResult,
        velocity_metrics: VelocityMetrics,
        request: ForecastRequest,
    ) -> ForecastResponse:
        """Map forecast result to response

        Args:
            forecast_result: Domain forecast result
            velocity_metrics: Velocity metrics
            request: Original forecast request

        Returns:
            Forecast response
        """
        # Get simulation result
        sim_result = forecast_result.simulation_results.get(
            ModelType.MONTE_CARLO, list(forecast_result.simulation_results.values())[0]
        )

        return self.request_response_mapper.create_forecast_response(
            success=True,
            project_name=request.project_name or "Project",
            remaining_work=forecast_result.simulation_config.remaining_work,
            velocity_field=request.velocity_field,
            simulation_result=sim_result,
            velocity_metrics=velocity_metrics,
        )

    def create_error_response(
        self, response_type: str, error_message: str, **kwargs
    ) -> Any:
        """Create error response of specified type

        Args:
            response_type: Type of response ('forecast', 'report', 'import')
            error_message: Error message
            **kwargs: Additional parameters for response

        Returns:
            Appropriate error response
        """
        if response_type == "forecast":
            return ForecastResponse(
                success=False,
                project_name=kwargs.get("project_name", "Project"),
                remaining_work=0,
                velocity_field=kwargs.get("velocity_field", "storyPoints"),
                percentile_50=0,
                percentile_70=0,
                percentile_85=0,
                percentile_95=0,
                errors=[error_message],
            )
        elif response_type == "report":
            return ReportResponse(
                success=False, report_path=Path(""), errors=[error_message]
            )
        else:
            raise ValueError(f"Unknown response type: {response_type}")
