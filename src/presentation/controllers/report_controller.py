"""Report controller for presentation layer"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from .base import Controller
from ..models.requests import ReportRequest
from ..models.responses import ReportResponse
from ..models.view_models import (
    ReportViewModel,
    MetricCardViewModel,
    ChartViewModel,
    HealthScoreViewModel,
    TableRowViewModel
)


class ReportController(Controller[ReportRequest, ReportResponse]):
    """Controller for handling report generation"""
    
    def __init__(
        self,
        report_generator,
        style_service,
        process_health_use_cases: Dict,
        chart_generator,
        view_model_mapper
    ):
        """Initialize report controller
        
        Args:
            report_generator: Report generation service
            style_service: Style service for themes
            process_health_use_cases: Dictionary of health analysis use cases
            chart_generator: Chart generation service
            view_model_mapper: Mapper for creating view models
        """
        super().__init__("Report")
        self.report_generator = report_generator
        self.style_service = style_service
        self.process_health_use_cases = process_health_use_cases
        self.chart_generator = chart_generator
        self.view_model_mapper = view_model_mapper
    
    def handle(self, request: ReportRequest) -> ReportResponse:
        """Handle report generation request
        
        Args:
            request: Report request model
            
        Returns:
            Report response model
        """
        try:
            # Determine output path
            output_path = self._determine_output_path(request)
            
            # Create report view model
            report_vm = self._create_report_view_model(request)
            
            # Generate styles
            theme = self.style_service.get_theme(request.theme)
            styles = self.style_service.generate_styles(theme)
            
            # Add styles to view model
            report_vm.theme_name = request.theme
            
            # Generate HTML
            html_content = self.report_generator.generate_from_view_model(
                report_vm,
                styles
            )
            
            # Write to file
            output_path.write_text(html_content, encoding='utf-8')
            
            # Build response
            response = ReportResponse(
                success=True,
                report_path=output_path,
                report_url=f"file://{output_path.absolute()}",
                generation_time=datetime.now(),
                charts_included=list(report_vm.charts.keys()),
                sections_included=self._get_included_sections(report_vm),
                theme_used=request.theme,
                health_score=report_vm.health_score.overall_score if report_vm.health_score else None,
                health_insights=self._extract_health_insights(report_vm),
                health_recommendations=self._extract_health_recommendations(report_vm)
            )
            
            # Open in browser if requested
            if request.open_browser:
                import webbrowser
                webbrowser.open(response.report_url)
            
            return response
            
        except Exception as e:
            self._logger.error(f"Report generation failed: {str(e)}")
            return ReportResponse(
                success=False,
                report_path=Path(""),
                errors=[str(e)]
            )
    
    def _determine_output_path(self, request: ReportRequest) -> Path:
        """Determine output path for report
        
        Args:
            request: Report request
            
        Returns:
            Output path
        """
        if request.output_path:
            return request.output_path
        
        # Default to reports directory
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = request.project_name or "project"
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_name)
        
        return reports_dir / f"{safe_name}_report_{timestamp}.html"
    
    def _create_report_view_model(self, request: ReportRequest) -> ReportViewModel:
        """Create report view model from request and context
        
        Args:
            request: Report request
            
        Returns:
            Report view model
        """
        # This would normally get data from context/state
        # For now, creating a basic view model
        
        report_vm = ReportViewModel(
            title="Sprint Radar Analytics",
            subtitle="Agile Project Forecasting Report",
            project_name=request.project_name,
            theme_name=request.theme,
            has_jql_query=bool(request.jql_query),
            jql_query=request.jql_query,
            jira_url=request.jira_url
        )
        
        # Add metric cards
        report_vm.metric_cards = self._create_metric_cards()
        
        # Add charts
        if request.include_charts:
            report_vm.charts = self._create_charts(request.include_charts)
        
        # Add health metrics if requested
        if request.include_health_metrics:
            report_vm.has_health_metrics = True
            report_vm.health_score = self._create_health_score_view_model(request)
            report_vm.health_charts = self._create_health_charts()
        
        # Add summary table
        report_vm.summary_table = self._create_summary_table()
        
        return report_vm
    
    def _create_metric_cards(self) -> List[MetricCardViewModel]:
        """Create metric cards for the report
        
        Returns:
            List of metric card view models
        """
        # Would get actual data from context
        return [
            MetricCardViewModel(
                label="Remaining Work",
                value="150",
                unit="Story Points",
                color="primary"
            ),
            MetricCardViewModel(
                label="Average Velocity",
                value="25.5",
                unit="per sprint",
                color="success"
            ),
            MetricCardViewModel(
                label="50% Confidence",
                value="6",
                unit="sprints",
                color="info"
            ),
            MetricCardViewModel(
                label="85% Confidence",
                value="8",
                unit="sprints",
                color="warning"
            )
        ]
    
    def _create_charts(self, chart_names: List[str]) -> Dict[str, ChartViewModel]:
        """Create charts for the report
        
        Args:
            chart_names: List of chart names to include
            
        Returns:
            Dictionary of chart view models
        """
        charts = {}
        
        # Would use chart generator to create actual chart data
        for chart_name in chart_names:
            charts[chart_name] = ChartViewModel(
                chart_id=chart_name,
                chart_type=self._get_chart_type(chart_name),
                title=self._get_chart_title(chart_name),
                description=self._get_chart_description(chart_name),
                data={},  # Would be actual Plotly data
                layout={}  # Would be actual Plotly layout
            )
        
        return charts
    
    def _create_health_score_view_model(
        self, 
        request: ReportRequest
    ) -> HealthScoreViewModel:
        """Create health score view model
        
        Args:
            request: Report request
            
        Returns:
            Health score view model
        """
        # Would calculate from actual health metrics
        score = 75.0
        
        return HealthScoreViewModel(
            overall_score=score,
            score_label=self._get_score_label(score),
            score_color=self._get_score_color(score),
            components=[],  # Would add actual components
            gauge_chart=ChartViewModel(
                chart_id="health_gauge",
                chart_type="gauge",
                title="Process Health Score",
                description="Overall health of your development process",
                data={},
                layout={}
            )
        )
    
    def _create_health_charts(self) -> Dict[str, ChartViewModel]:
        """Create health-related charts
        
        Returns:
            Dictionary of health chart view models
        """
        # Would create actual health charts
        return {}
    
    def _create_summary_table(self) -> List[TableRowViewModel]:
        """Create summary table rows
        
        Returns:
            List of table row view models
        """
        # Would create from actual data
        return [
            TableRowViewModel(
                cells=["50% Confidence", "6 sprints", "2024-03-15", "50% chance"],
                row_class="optimistic"
            ),
            TableRowViewModel(
                cells=["85% Confidence", "8 sprints", "2024-04-12", "85% chance"],
                row_class="conservative"
            )
        ]
    
    def _get_included_sections(self, report_vm: ReportViewModel) -> List[str]:
        """Get list of sections included in report
        
        Args:
            report_vm: Report view model
            
        Returns:
            List of section names
        """
        sections = ["header", "metrics", "charts", "summary"]
        
        if report_vm.has_health_metrics:
            sections.append("health")
        
        if report_vm.has_jql_query:
            sections.append("query")
        
        return sections
    
    def _extract_health_insights(
        self, 
        report_vm: ReportViewModel
    ) -> List[str]:
        """Extract health insights from report
        
        Args:
            report_vm: Report view model
            
        Returns:
            List of insights
        """
        insights = []
        
        if report_vm.health_score:
            for component in report_vm.health_score.components:
                insights.extend(component.insights)
        
        return insights
    
    def _extract_health_recommendations(
        self, 
        report_vm: ReportViewModel
    ) -> List[str]:
        """Extract health recommendations from report
        
        Args:
            report_vm: Report view model
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if report_vm.health_score:
            for component in report_vm.health_score.components:
                recommendations.extend(component.recommendations)
        
        return recommendations
    
    def _get_chart_type(self, chart_name: str) -> str:
        """Get chart type from name
        
        Args:
            chart_name: Chart name
            
        Returns:
            Chart type
        """
        type_map = {
            'probability_distribution': 'bar',
            'confidence_intervals': 'bar',
            'velocity_trend': 'line',
            'forecast_timeline': 'scatter',
            'story_size_breakdown': 'pie'
        }
        
        return type_map.get(chart_name, 'bar')
    
    def _get_chart_title(self, chart_name: str) -> str:
        """Get chart title from name
        
        Args:
            chart_name: Chart name
            
        Returns:
            Chart title
        """
        title_map = {
            'probability_distribution': 'Probability Distribution',
            'confidence_intervals': 'Confidence Intervals',
            'velocity_trend': 'Historical Velocity Trend',
            'forecast_timeline': 'Forecast Timeline',
            'story_size_breakdown': 'Remaining Work Distribution'
        }
        
        return title_map.get(chart_name, chart_name.replace('_', ' ').title())
    
    def _get_chart_description(self, chart_name: str) -> str:
        """Get chart description from name
        
        Args:
            chart_name: Chart name
            
        Returns:
            Chart description
        """
        desc_map = {
            'probability_distribution': 'The likelihood of completing work in different numbers of sprints',
            'confidence_intervals': 'Range of completion estimates at different confidence levels',
            'velocity_trend': 'Team velocity over recent sprints with trend line',
            'forecast_timeline': 'Projected completion dates with confidence levels',
            'story_size_breakdown': 'Breakdown of remaining work by size or category'
        }
        
        return desc_map.get(chart_name, '')
    
    def _get_score_label(self, score: float) -> str:
        """Get label for health score
        
        Args:
            score: Health score (0-100)
            
        Returns:
            Score label
        """
        if score >= 90:
            return "Excellent"
        elif score >= 75:
            return "Good"
        elif score >= 60:
            return "Fair"
        else:
            return "Poor"
    
    def _get_score_color(self, score: float) -> str:
        """Get color for health score
        
        Args:
            score: Health score (0-100)
            
        Returns:
            Color name
        """
        if score >= 90:
            return "success"
        elif score >= 75:
            return "primary"
        elif score >= 60:
            return "warning"
        else:
            return "error"