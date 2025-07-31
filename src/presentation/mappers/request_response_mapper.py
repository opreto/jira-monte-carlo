"""Mapper for converting between presentation requests/responses and domain objects"""

from typing import Dict, Any, List
from pathlib import Path

from ..models.requests import ImportDataRequest, ForecastRequest, ReportRequest
from ..models.responses import ImportDataResponse, ForecastResponse, ReportResponse
from ...domain.value_objects import FieldMapping
from ...domain.entities import SimulationConfig
from ...domain.forecasting import MonteCarloConfiguration


class RequestResponseMapper:
    """Maps between presentation layer requests/responses and domain objects"""

    def map_import_request_to_field_mapping(
        self, request: ImportDataRequest
    ) -> FieldMapping:
        """Convert import request to field mapping

        Args:
            request: Import data request

        Returns:
            Field mapping value object
        """
        # Use provided field mapping or create from individual fields
        if request.field_mapping:
            return FieldMapping(**request.field_mapping)

        return FieldMapping(
            id_field=request.key_field,
            title_field=request.summary_field,
            estimation_field=request.points_field,
            velocity_field=request.velocity_field,
            sprint_field=request.sprint_field,
            status_field=request.status_field,
            created_date_field=request.created_field,
            resolved_date_field=request.resolved_field,
            labels_field=request.labels_field,
            issue_type_field=request.type_field,
            assignee_field=request.assignee_field,
            project_field=request.project_field,
            blocked_field=request.blocked_field,
        )

    def map_forecast_request_to_simulation_config(
        self, request: ForecastRequest, remaining_work: float
    ) -> SimulationConfig:
        """Convert forecast request to simulation config

        Args:
            request: Forecast request
            remaining_work: Calculated or provided remaining work

        Returns:
            Simulation configuration
        """
        return SimulationConfig(
            remaining_work=remaining_work,
            sprint_length=request.sprint_length,
            team_capacity=1.0,  # Default for now
            confidence_levels=request.confidence_levels,
            num_simulations=request.simulations,
        )

    def map_forecast_request_to_monte_carlo_config(
        self, request: ForecastRequest
    ) -> MonteCarloConfiguration:
        """Convert forecast request to Monte Carlo configuration

        Args:
            request: Forecast request

        Returns:
            Monte Carlo configuration
        """
        return MonteCarloConfiguration(
            num_simulations=request.simulations,
            confidence_levels=request.confidence_levels,
            use_historical_pattern=request.use_historical_pattern,
            min_velocity_factor=request.min_velocity_factor,
            max_velocity_factor=request.max_velocity_factor,
        )

    def create_import_response(
        self,
        success: bool,
        issues_count: int = 0,
        sprints_count: int = 0,
        source_type: str = "unknown",
        field_mapping: Dict[str, str] = None,
        data_quality_score: float = 0.0,
        missing_fields: Dict[str, int] = None,
        errors: List[str] = None,
        analysis_results: Dict[str, Any] = None,
    ) -> ImportDataResponse:
        """Create import data response

        Args:
            Various response parameters

        Returns:
            Import data response
        """
        return ImportDataResponse(
            success=success,
            issues_count=issues_count,
            sprints_count=sprints_count,
            source_type=source_type,
            field_mapping_used=field_mapping or {},
            data_quality_score=data_quality_score,
            missing_fields=missing_fields or {},
            errors=errors or [],
            analysis_results=analysis_results,
        )

    def create_forecast_response(
        self,
        success: bool,
        project_name: str,
        remaining_work: float,
        velocity_field: str,
        simulation_result: Any = None,
        velocity_metrics: Any = None,
        errors: List[str] = None,
    ) -> ForecastResponse:
        """Create forecast response from domain results

        Args:
            Various response parameters including domain objects

        Returns:
            Forecast response
        """
        response = ForecastResponse(
            success=success,
            project_name=project_name,
            remaining_work=remaining_work,
            velocity_field=velocity_field,
            percentile_50=0,
            percentile_70=0,
            percentile_85=0,
            percentile_95=0,
            errors=errors or [],
        )

        if simulation_result and success:
            # Extract percentiles
            percentiles = simulation_result.percentiles
            response.percentile_50 = int(percentiles.get(0.5, 0))
            response.percentile_70 = int(percentiles.get(0.7, 0))
            response.percentile_85 = int(percentiles.get(0.85, 0))
            response.percentile_95 = int(percentiles.get(0.95, 0))

        if velocity_metrics and success:
            # Add velocity metrics
            response.average_velocity = velocity_metrics.average
            response.median_velocity = velocity_metrics.median
            response.velocity_std_dev = velocity_metrics.std_dev
            response.velocity_trend = velocity_metrics.trend

        return response

    def create_report_response(
        self,
        success: bool,
        report_path: Path = None,
        report_url: str = None,
        generation_time: Any = None,
        errors: List[str] = None,
        **kwargs,
    ) -> ReportResponse:
        """Create report response

        Args:
            Various response parameters

        Returns:
            Report response
        """
        if not success:
            return ReportResponse(
                success=False, report_path=Path(""), errors=errors or []
            )

        response = ReportResponse(
            success=success,
            report_path=report_path,
            report_url=report_url,
            generation_time=generation_time,
            errors=errors or [],
        )

        # Add optional fields from kwargs
        for key, value in kwargs.items():
            if hasattr(response, key):
                setattr(response, key, value)

        return response

    def extract_chart_preferences(self, request: ReportRequest) -> Dict[str, bool]:
        """Extract chart preferences from report request

        Args:
            request: Report request

        Returns:
            Dictionary of chart name to include flag
        """
        preferences = {}

        if request.include_charts:
            for chart in request.include_charts:
                preferences[chart] = True

        # Default charts if none specified
        if not preferences:
            preferences = {
                "probability_distribution": True,
                "confidence_intervals": True,
                "velocity_trend": True,
                "forecast_timeline": True,
            }

        return preferences

    def extract_health_preferences(self, request: ReportRequest) -> Dict[str, bool]:
        """Extract health metric preferences from report request

        Args:
            request: Report request

        Returns:
            Dictionary of health metric preferences
        """
        return {
            "include_aging": request.include_health_metrics,
            "include_wip": request.include_health_metrics,
            "include_sprint_health": request.include_health_metrics,
            "include_blocked": request.include_health_metrics,
            "include_lead_time": request.include_health_metrics,
        }
