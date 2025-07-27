"""Multi-project HTML report generator"""
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Optional
from jinja2 import Template

from ..domain.multi_project import MultiProjectReport, ProjectData
from .report_generator import HTMLReportGenerator
from ..application.style_service import StyleService
from .templates import ReportTemplates
from .style_generator import StyleGenerator


class MultiProjectReportGenerator:
    """Generate multi-page HTML report for multiple projects"""
    
    def __init__(self, style_service: Optional[StyleService] = None, theme_name: Optional[str] = None):
        self.style_service = style_service or StyleService()
        self.theme_name = theme_name
        self.style_generator = self.style_service.get_style_generator(theme_name)
        self.chart_colors = self.style_generator.get_chart_colors()
        self.base_template = ReportTemplates.get_base_template()
        self.dashboard_template = ReportTemplates.get_dashboard_template()
    
    def generate(self, 
                multi_report: MultiProjectReport,
                output_dir: Path,
                output_filename: str = "index.html") -> Path:
        """
        Generate multi-project report with dashboard and individual pages
        
        Args:
            multi_report: Multi-project report data
            output_dir: Directory to save report files
            output_filename: Name of main dashboard file
            
        Returns:
            Path to main dashboard file
        """
        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate individual project reports
        project_links = {}
        single_report_generator = HTMLReportGenerator(self.style_service, self.theme_name)
        
        for project in multi_report.projects:
            # Generate individual report
            project_filename = f"{project.name}_report.html"
            project_path = output_dir / project_filename
            
            # Create a simulation config from the project data
            from ..domain.entities import SimulationConfig
            config = SimulationConfig(
                num_simulations=10000,  # Default
                confidence_levels=[0.5, 0.7, 0.85, 0.95],
                sprint_duration_days=14
            )
            
            # Generate historical data from velocity analysis
            from ..domain.value_objects import HistoricalData
            historical_data = HistoricalData(
                velocities=[],
                cycle_times=[],
                throughput=[],
                dates=[]
            )
            
            if project.sprints:
                for sprint in project.sprints:
                    if hasattr(sprint, 'completed_points'):
                        historical_data.velocities.append(sprint.completed_points)
                        historical_data.dates.append(sprint.start_date)
            
            # Generate individual report
            single_report_generator.generate(
                simulation_results=project.simulation_result,
                velocity_metrics=project.velocity_metrics,
                historical_data=historical_data,
                remaining_work=project.remaining_work,
                config=config,
                output_path=project_path,
                project_name=project.name
            )
            
            project_links[project.name] = project_filename
        
        # Generate dashboard
        dashboard_path = output_dir / output_filename
        self._generate_dashboard(multi_report, project_links, dashboard_path)
        
        return dashboard_path
    
    def _generate_dashboard(self, 
                          multi_report: MultiProjectReport,
                          project_links: Dict[str, str],
                          output_path: Path):
        """Generate the main dashboard page"""
        
        # Prepare data for charts
        project_names = [p.name for p in multi_report.projects]
        remaining_work = [p.remaining_work for p in multi_report.projects]
        velocities = [p.velocity_metrics.average if p.velocity_metrics else 0 
                     for p in multi_report.projects]
        completion_percentages = [p.completion_percentage for p in multi_report.projects]
        
        # Generate charts data
        charts_data = {
            "project_comparison": self._create_project_comparison_chart(
                project_names, remaining_work, velocities, completion_percentages
            ),
            "velocity_comparison": self._create_velocity_comparison_chart(
                project_names, multi_report.projects
            ),
            "timeline_comparison": self._create_timeline_comparison_chart(
                multi_report.projects
            ),
            "workload_distribution": self._create_workload_distribution_chart(
                project_names, remaining_work
            )
        }
        
        # Generate HTML
        html_content = self._render_dashboard_template(
            multi_report=multi_report,
            project_links=project_links,
            charts_data=charts_data
        )
        
        # Write to file
        output_path.write_text(html_content, encoding='utf-8')
    
    def _create_project_comparison_chart(self, names, remaining, velocities, completion):
        """Create project comparison bar chart"""
        # Calculate completed work for each project
        completed_work = []
        for i, comp_pct in enumerate(completion):
            # Convert percentage to decimal (56.6% -> 0.566)
            comp_decimal = comp_pct / 100.0
            if comp_decimal > 0 and comp_decimal < 1:
                # If we know X% is complete and Y points remain, total = Y / (1 - X%)
                total_work = remaining[i] / (1 - comp_decimal)
                completed_work.append(total_work - remaining[i])  # Completed = Total - Remaining
            else:
                completed_work.append(0)
        
        return {
            "data": [{
                "x": names,
                "y": completed_work,
                "name": "Completed Work",
                "type": "bar",
                "marker": {"color": self.chart_colors['high_confidence']},  # Green for completed
                "text": [f"{c:.1f}%" for c in completion],
                "textposition": "inside"
            }, {
                "x": names,
                "y": remaining,
                "name": "Remaining Work",
                "type": "bar",
                "marker": {"color": self.chart_colors['low_confidence']},  # Red for remaining
                "text": [f"{100-c:.1f}%" for c in completion],
                "textposition": "inside"
            }],
            "layout": {
                "title": "Project Progress Overview",
                "xaxis": {"title": "Projects"},
                "yaxis": {"title": "Story Points"},
                "barmode": "stack",
                "hovermode": "x unified",
                "showlegend": True
            }
        }
    
    def _create_velocity_comparison_chart(self, names, projects):
        """Create velocity box plot comparison"""
        data = []
        for project in projects:
            if project.sprints:
                velocities = [s.completed_points for s in project.sprints 
                            if hasattr(s, 'completed_points')]
                if velocities:
                    data.append({
                        "y": velocities,
                        "name": project.name,
                        "type": "box",
                        "boxpoints": "all",
                        "jitter": 0.3,
                        "pointpos": -1.8
                    })
        
        return {
            "data": data,
            "layout": {
                "title": "Velocity Distribution by Project",
                "yaxis": {"title": "Velocity (Story Points)"},
                "showlegend": False
            }
        }
    
    def _create_timeline_comparison_chart(self, projects):
        """Create timeline comparison chart"""
        data = []
        
        for i, project in enumerate(projects):
            if project.simulation_result:
                percentiles = project.simulation_result.percentiles
                
                # Create a horizontal bar for each confidence level
                # Use different colors for each project
                data_colors = [
                    self.chart_colors['data1'],
                    self.chart_colors['data2'],
                    self.chart_colors['data3'],
                    self.chart_colors['data4'],
                    self.chart_colors['data5']
                ]
                base_color = data_colors[i % len(data_colors)]
                
                # Get the project's base color
                if self.style_generator.theme.colors.chart_colors:
                    chart_colors = self.style_generator.theme.colors.chart_colors
                    project_colors = [
                        chart_colors.data1,
                        chart_colors.data2,
                        chart_colors.data3,
                        chart_colors.data4,
                        chart_colors.data5
                    ]
                    project_color = project_colors[i % len(project_colors)]
                else:
                    # Fallback
                    project_color = self.style_generator.theme.colors.primary
                
                for conf_level, sprints in percentiles.items():
                    # Vary opacity based on confidence level
                    # Higher confidence = more opaque
                    opacity = 0.3 + (0.7 * (1 - conf_level))  # 0.3 to 1.0
                    
                    conf_percentage = int(conf_level * 100)
                    data.append({
                        "x": [sprints],
                        "y": [project.name],
                        "name": f"{conf_percentage}% confidence",
                        "type": "bar",
                        "orientation": "h",
                        "marker": {
                            "color": project_color.to_rgba(opacity)
                        },
                        "showlegend": i == 0  # Only show legend for first project
                    })
        
        return {
            "data": data,
            "layout": {
                "title": "Sprint Completion Timeline Comparison",
                "xaxis": {"title": "Sprints to Complete"},
                "yaxis": {
                    "title": "Projects",
                    "automargin": True,  # Automatically adjust margin for long labels
                    "tickmode": "linear"
                },
                "barmode": "overlay",
                "hovermode": "y unified",
                "margin": {"l": 150}  # More left margin for project names
            }
        }
    
    def _create_workload_distribution_chart(self, names, remaining):
        """Create pie chart of workload distribution"""
        return {
            "data": [{
                "values": remaining,
                "labels": names,
                "type": "pie",
                "hole": 0.4,
                "textposition": "inside",
                "textinfo": "label+percent"
            }],
            "layout": {
                "title": "Workload Distribution",
                "showlegend": True
            }
        }
    
    def _render_dashboard_template(self, multi_report, project_links, charts_data):
        """Render the dashboard HTML template"""
        
        # Generate content from dashboard template
        content = self.dashboard_template.render(
            multi_report=multi_report,
            project_links=project_links,
            charts_data=charts_data
        )
        
        # Generate complete HTML with styles
        styles = self.style_generator.generate_css()
        
        return self.base_template.render(
            title="Multi-Project Monte Carlo Dashboard",
            styles=styles,
            content=content
        )