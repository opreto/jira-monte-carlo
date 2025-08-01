"""Mapper for converting domain entities to view models"""

from datetime import datetime
from typing import List, Any, Optional

from ..models.view_models import (
    MetricCardViewModel,
    TableRowViewModel,
    HealthScoreViewModel,
    HealthComponentViewModel,
    ForecastSummaryViewModel,
    ProgressBarViewModel,
    AlertViewModel,
)
from ...domain.entities import SimulationConfig, SimulationResult
from ...domain.value_objects import VelocityMetrics
from ...domain.process_health import (
    ProcessHealthMetrics,
    AgingAnalysis,
    WIPAnalysis,
    SprintHealthAnalysis,
)


class ViewModelMapper:
    """Maps domain entities to presentation view models"""

    def create_metric_card(
        self,
        label: str,
        value: Any,
        unit: Optional[str] = None,
        trend: Optional[float] = None,
        color: str = "primary",
    ) -> MetricCardViewModel:
        """Create a metric card view model

        Args:
            label: Metric label
            value: Metric value
            unit: Unit of measurement
            trend: Trend value (-1 to 1)
            color: Card color

        Returns:
            Metric card view model
        """
        # Format value
        if isinstance(value, float):
            value_str = f"{value:.1f}"
        else:
            value_str = str(value)

        # Determine trend
        trend_str = None
        trend_value_str = None
        if trend is not None:
            if trend > 0:
                trend_str = "up"
                trend_value_str = f"+{trend:.1%}"
            elif trend < 0:
                trend_str = "down"
                trend_value_str = f"{trend:.1%}"
            else:
                trend_str = "stable"
                trend_value_str = "0%"

        return MetricCardViewModel(
            label=label,
            value=value_str,
            unit=unit,
            trend=trend_str,
            trend_value=trend_value_str,
            color=color,
        )

    def create_forecast_summary(
        self,
        project_name: str,
        simulation_config: SimulationConfig,
        simulation_result: SimulationResult,
        velocity_metrics: VelocityMetrics,
    ) -> ForecastSummaryViewModel:
        """Create forecast summary view model

        Args:
            project_name: Project name
            simulation_config: Simulation configuration
            simulation_result: Simulation results
            velocity_metrics: Velocity metrics

        Returns:
            Forecast summary view model
        """
        # Format remaining work
        remaining_work_display = f"{simulation_config.remaining_work:.1f} points"
        velocity_display = f"{velocity_metrics.average:.1f} points/sprint"

        # Build confidence levels
        confidence_levels = []
        for confidence in [0.5, 0.7, 0.85, 0.95]:
            if confidence in simulation_result.percentiles:
                sprints = simulation_result.percentiles[confidence]
                level_str = f"{int(confidence * 100)}%"
                sprints_str = f"{int(sprints)} sprints"
                # Would calculate actual date
                date_str = f"Sprint +{int(sprints)}"
                confidence_levels.append((level_str, sprints_str, date_str))

        # Assess risk
        risk_level, risk_color, risk_message = self._assess_forecast_risk(
            simulation_result, velocity_metrics
        )

        # Create summary cards
        summary_cards = [
            self.create_metric_card(
                "Remaining Work", simulation_config.remaining_work, "points"
            ),
            self.create_metric_card(
                "Average Velocity",
                velocity_metrics.average,
                "points/sprint",
                velocity_metrics.trend,
            ),
            self.create_metric_card(
                "Velocity Stability",
                f"{(1 - velocity_metrics.std_dev / velocity_metrics.average) * 100:.0f}",
                "%",
                color="success"
                if velocity_metrics.std_dev < velocity_metrics.average * 0.2
                else "warning",
            ),
        ]

        return ForecastSummaryViewModel(
            project_name=project_name,
            remaining_work_display=remaining_work_display,
            velocity_display=velocity_display,
            confidence_levels=confidence_levels,
            risk_level=risk_level,
            risk_color=risk_color,
            risk_message=risk_message,
            summary_cards=summary_cards,
        )

    def create_health_score(
        self, health_metrics: ProcessHealthMetrics
    ) -> HealthScoreViewModel:
        """Create health score view model

        Args:
            health_metrics: Process health metrics

        Returns:
            Health score view model
        """
        # Calculate overall score
        overall_score = health_metrics.overall_health_score * 100

        # Determine label and color
        if overall_score >= 90:
            score_label = "Excellent"
            score_color = "success"
        elif overall_score >= 75:
            score_label = "Good"
            score_color = "primary"
        elif overall_score >= 60:
            score_label = "Fair"
            score_color = "warning"
        else:
            score_label = "Poor"
            score_color = "error"

        # Create components
        components = []

        if health_metrics.aging_analysis:
            components.append(
                self._create_aging_component(health_metrics.aging_analysis)
            )

        if health_metrics.wip_analysis:
            components.append(self._create_wip_component(health_metrics.wip_analysis))

        if health_metrics.sprint_health:
            components.append(
                self._create_sprint_health_component(health_metrics.sprint_health)
            )

        return HealthScoreViewModel(
            overall_score=overall_score,
            score_label=score_label,
            score_color=score_color,
            components=components,
        )

    def create_table_row(
        self, cells: List[str], row_class: Optional[str] = None, is_header: bool = False
    ) -> TableRowViewModel:
        """Create a table row view model

        Args:
            cells: List of cell values
            row_class: Optional CSS class for styling
            is_header: Whether this is a header row

        Returns:
            Table row view model
        """
        return TableRowViewModel(cells=cells, row_class=row_class, is_header=is_header)

    def create_summary_table(
        self, simulation_result: SimulationResult, sprint_length: int = 14
    ) -> List[TableRowViewModel]:
        """Create summary table rows

        Args:
            simulation_result: Simulation results
            sprint_length: Sprint length in days

        Returns:
            List of table rows
        """
        rows = []

        # Add header row
        rows.append(
            TableRowViewModel(
                cells=[
                    "Confidence Level",
                    "Sprints to Complete",
                    "Completion Date",
                    "Probability",
                ],
                is_header=True,
            )
        )

        # Add data rows
        for confidence, label, css_class in [
            (0.5, "50% (Optimistic)", "optimistic"),
            (0.7, "70% (Likely)", "likely"),
            (0.85, "85% (Conservative)", "conservative"),
            (0.95, "95% (Very Conservative)", "very-conservative"),
        ]:
            if confidence in simulation_result.percentiles:
                sprints = simulation_result.percentiles[confidence]
                sprints_str = f"{int(sprints)} sprints"

                # Calculate date (simplified)
                # TODO: Add days to date based on sprint length
                date = datetime.now()
                date_str = date.strftime("%Y-%m-%d")

                probability_str = (
                    f"{int(confidence * 100)}% chance of completing by this date"
                )

                rows.append(
                    TableRowViewModel(
                        cells=[label, sprints_str, date_str, probability_str],
                        row_class=css_class,
                    )
                )

        return rows

    def create_progress_bar(
        self, label: str, current: float, total: float, color: str = "primary"
    ) -> ProgressBarViewModel:
        """Create progress bar view model

        Args:
            label: Progress bar label
            current: Current value
            total: Total value
            color: Bar color

        Returns:
            Progress bar view model
        """
        percentage = (current / total * 100) if total > 0 else 0

        return ProgressBarViewModel(
            label=label, value=percentage, color=color, show_percentage=True
        )

    def create_alert(
        self, message: str, alert_type: str = "info", dismissible: bool = True
    ) -> AlertViewModel:
        """Create alert view model

        Args:
            message: Alert message
            alert_type: Type of alert
            dismissible: Whether alert can be dismissed

        Returns:
            Alert view model
        """
        # Map type to icon
        icon_map = {"info": "ℹ️", "success": "✅", "warning": "⚠️", "error": "❌"}

        return AlertViewModel(
            message=message,
            type=alert_type,
            dismissible=dismissible,
            icon=icon_map.get(alert_type),
        )

    def _assess_forecast_risk(
        self, simulation_result: SimulationResult, velocity_metrics: VelocityMetrics
    ) -> tuple[str, str, str]:
        """Assess forecast risk level

        Args:
            simulation_result: Simulation results
            velocity_metrics: Velocity metrics

        Returns:
            Tuple of (risk_level, risk_color, risk_message)
        """
        # Calculate spread
        if (
            0.95 in simulation_result.percentiles
            and 0.5 in simulation_result.percentiles
        ):
            spread = (
                simulation_result.percentiles[0.95] - simulation_result.percentiles[0.5]
            )
            relative_spread = spread / simulation_result.percentiles[0.5]
        else:
            relative_spread = 0

        # Calculate velocity stability
        velocity_cv = (
            velocity_metrics.std_dev / velocity_metrics.average
            if velocity_metrics.average > 0
            else 0
        )

        # Assess risk
        if relative_spread > 0.5 or velocity_cv > 0.3:
            return ("high", "error", "High uncertainty in estimates")
        elif relative_spread > 0.3 or velocity_cv > 0.2:
            return ("medium", "warning", "Moderate uncertainty in estimates")
        else:
            return ("low", "success", "Low uncertainty - predictable delivery")

    def _create_aging_component(self, aging: AgingAnalysis) -> HealthComponentViewModel:
        """Create aging component view model

        Args:
            aging: Aging analysis

        Returns:
            Health component view model
        """
        # Calculate score (inverse of old items ratio)
        old_ratio = (aging.stale_count + aging.abandoned_count) / max(
            aging.total_items, 1
        )
        score = (1 - old_ratio) * 100

        # Determine color
        if score >= 80:
            color = "success"
        elif score >= 60:
            color = "warning"
        else:
            color = "error"

        # Build insights
        insights = []
        if aging.fresh_count > 0:
            insights.append(f"{aging.fresh_count} fresh items (< 7 days)")
        if aging.stale_count > 0:
            insights.append(f"{aging.stale_count} stale items (> 30 days)")
        if aging.abandoned_count > 0:
            insights.append(f"{aging.abandoned_count} abandoned items (> 90 days)")

        # Build recommendations
        recommendations = []
        if aging.abandoned_count > 0:
            recommendations.append(
                f"Review and close {aging.abandoned_count} abandoned items"
            )
        if old_ratio > 0.2:
            recommendations.append("Over 20% of items are old - review your backlog")

        return HealthComponentViewModel(
            name="Work Item Age",
            score=score,
            weight=0.25,
            description="Measures how fresh your work items are",
            color=color,
            icon="📅",
            insights=insights,
            recommendations=recommendations,
        )

    def _create_wip_component(self, wip: WIPAnalysis) -> HealthComponentViewModel:
        """Create WIP component view model

        Args:
            wip: WIP analysis

        Returns:
            Health component view model
        """
        # Calculate score based on WIP violations
        violations = len(wip.items_over_limit)
        score = max(0, 100 - (violations * 20))

        # Determine color
        if violations == 0:
            color = "success"
        elif violations <= 2:
            color = "warning"
        else:
            color = "error"

        # Build insights
        insights = []
        for status, data in wip.wip_by_status.items():
            insights.append(f"{status}: {data['count']} items")

        # Build recommendations
        recommendations = []
        if violations > 0:
            recommendations.append(f"Reduce WIP in {violations} states to improve flow")

        return HealthComponentViewModel(
            name="Work In Progress",
            score=score,
            weight=0.25,
            description="Monitors WIP limits for better flow",
            color=color,
            icon="🔄",
            insights=insights,
            recommendations=recommendations,
        )

    def _create_sprint_health_component(
        self, sprint_health: SprintHealthAnalysis
    ) -> HealthComponentViewModel:
        """Create sprint health component view model

        Args:
            sprint_health: Sprint health analysis

        Returns:
            Health component view model
        """
        # Use average completion rate as score
        score = sprint_health.average_completion_rate * 100

        # Determine color
        if score >= 80:
            color = "success"
        elif score >= 60:
            color = "warning"
        else:
            color = "error"

        # Build insights
        insights = [
            f"Average completion: {score:.0f}%",
            f"Analyzed {sprint_health.sprints_analyzed} sprints",
        ]

        # Build recommendations
        recommendations = []
        if score < 80:
            recommendations.append(
                "Improve sprint planning to increase completion rate"
            )
        if (
            sprint_health.average_scope_change
            and abs(sprint_health.average_scope_change) > 0.2
        ):
            recommendations.append(
                "High scope change detected - stabilize sprint commitments"
            )

        return HealthComponentViewModel(
            name="Sprint Health",
            score=score,
            weight=0.25,
            description="Measures sprint completion and stability",
            color=color,
            icon="🏃",
            insights=insights,
            recommendations=recommendations,
        )
