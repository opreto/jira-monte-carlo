"""Multi-project HTML report generator"""
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List
from jinja2 import Template

from ..domain.multi_project import MultiProjectReport, ProjectData
from .report_generator import HTMLReportGenerator


class MultiProjectReportGenerator:
    """Generate multi-page HTML report for multiple projects"""
    
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
        single_report_generator = HTMLReportGenerator()
        
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
                output_path=project_path
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
        return {
            "data": [{
                "x": names,
                "y": remaining,
                "name": "Remaining Work",
                "type": "bar",
                "marker": {"color": "#ff6b6b"}
            }, {
                "x": names,
                "y": velocities,
                "name": "Average Velocity",
                "type": "bar",
                "marker": {"color": "#4ecdc4"},
                "yaxis": "y2"
            }],
            "layout": {
                "title": "Project Comparison",
                "xaxis": {"title": "Projects"},
                "yaxis": {"title": "Remaining Work (Story Points)"},
                "yaxis2": {
                    "title": "Average Velocity",
                    "overlaying": "y",
                    "side": "right"
                },
                "barmode": "group",
                "hovermode": "x unified"
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
                project_colors = [
                    "78, 205, 196",  # Teal
                    "255, 107, 107", # Red
                    "255, 193, 7",   # Amber
                    "103, 126, 234", # Blue
                    "255, 87, 34",   # Orange
                ]
                base_color = project_colors[i % len(project_colors)]
                
                for conf_level, sprints in percentiles.items():
                    # Higher confidence = lighter color
                    opacity = 1.0 - (conf_level - 0.5) * 0.8  # Scale from 1.0 to 0.6
                    conf_percentage = int(conf_level * 100)
                    data.append({
                        "x": [sprints],
                        "y": [project.name],
                        "name": f"{conf_percentage}% confidence",
                        "type": "bar",
                        "orientation": "h",
                        "marker": {
                            "color": f"rgba({base_color}, {opacity})"
                        },
                        "showlegend": i == 0  # Only show legend for first project
                    })
        
        return {
            "data": data,
            "layout": {
                "title": "Sprint Completion Timeline Comparison",
                "xaxis": {"title": "Sprints to Complete"},
                "yaxis": {"title": "Projects"},
                "barmode": "overlay",
                "hovermode": "y unified"
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
        
        template = Template('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Multi-Project Monte Carlo Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .metric-card .value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #667eea;
            margin: 0.5rem 0;
        }
        
        .metric-card .label {
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .projects-table {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
            margin-bottom: 2rem;
        }
        
        .projects-table h2 {
            margin: 0;
            padding: 1.5rem;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th, td {
            padding: 1rem 1.5rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        
        th {
            background: #f8f9fa;
            font-weight: 600;
            color: #495057;
        }
        
        tr:hover {
            background: #f8f9fa;
        }
        
        .project-link {
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }
        
        .project-link:hover {
            text-decoration: underline;
        }
        
        .chart-container {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .chart-container h2 {
            margin: 0 0 1rem 0;
            color: #333;
        }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #dee2e6;
        }
        
        .confidence-high {
            background-color: #d4edda;
            color: #155724;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }
        
        .confidence-medium {
            background-color: #fff3cd;
            color: #856404;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }
        
        .confidence-low {
            background-color: #f8d7da;
            color: #721c24;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Multi-Project Monte Carlo Dashboard</h1>
        <p>Analyzing {{ multi_report.projects|length }} projects • Generated {{ multi_report.generated_at.strftime('%Y-%m-%d %H:%M') }}</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="label">Total Projects</div>
            <div class="value">{{ multi_report.aggregated_metrics.total_projects }}</div>
        </div>
        
        <div class="metric-card">
            <div class="label">Total Issues</div>
            <div class="value">{{ multi_report.aggregated_metrics.total_issues }}</div>
        </div>
        
        <div class="metric-card">
            <div class="label">Overall Completion</div>
            <div class="value">{{ "%.1f"|format(multi_report.aggregated_metrics.overall_completion_percentage) }}%</div>
        </div>
        
        <div class="metric-card">
            <div class="label">Total Remaining Work</div>
            <div class="value">{{ "%.0f"|format(multi_report.aggregated_metrics.total_remaining_work) }}</div>
        </div>
        
        <div class="metric-card">
            <div class="label">Combined Velocity</div>
            <div class="value">{{ "%.1f"|format(multi_report.aggregated_metrics.combined_velocity) }}</div>
        </div>
        
        <div class="metric-card">
            <div class="label">85% Confidence</div>
            <div class="value">{{ multi_report.aggregated_metrics.confidence_intervals.get(0.85, 0) }} sprints</div>
        </div>
    </div>
    
    <div class="projects-table">
        <h2>Individual Project Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Project</th>
                    <th>Total Issues</th>
                    <th>Completion</th>
                    <th>Remaining Work</th>
                    <th>Velocity</th>
                    <th>50% Conf.</th>
                    <th>85% Conf.</th>
                    <th>Report</th>
                </tr>
            </thead>
            <tbody>
                {% for project in multi_report.projects %}
                <tr>
                    <td><strong>{{ project.name }}</strong></td>
                    <td>{{ project.total_issues }}</td>
                    <td>{{ "%.1f"|format(project.completion_percentage) }}%</td>
                    <td>{{ "%.1f"|format(project.remaining_work) }}</td>
                    <td>{{ "%.1f"|format(project.velocity_metrics.average) if project.velocity_metrics else "N/A" }}</td>
                    <td>{{ project.simulation_result.percentiles.get(0.5, 0)|int if project.simulation_result else "N/A" }}</td>
                    <td>{{ project.simulation_result.percentiles.get(0.85, 0)|int if project.simulation_result else "N/A" }}</td>
                    <td><a href="{{ project_links[project.name] }}" class="project-link">View Details →</a></td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    
    <div class="chart-container">
        <h2>Project Comparison</h2>
        <div id="project-comparison"></div>
    </div>
    
    <div class="chart-container">
        <h2>Velocity Distribution</h2>
        <div id="velocity-comparison"></div>
    </div>
    
    <div class="chart-container">
        <h2>Timeline Comparison</h2>
        <div id="timeline-comparison"></div>
    </div>
    
    <div class="chart-container">
        <h2>Workload Distribution</h2>
        <div id="workload-distribution"></div>
    </div>
    
    <div class="footer">
        <p>Generated by Jira Monte Carlo Simulator</p>
    </div>
    
    <script>
        // Project Comparison Chart
        Plotly.newPlot('project-comparison', 
            {{ charts_data.project_comparison.data | tojson }},
            {{ charts_data.project_comparison.layout | tojson }},
            {responsive: true}
        );
        
        // Velocity Comparison Chart
        Plotly.newPlot('velocity-comparison',
            {{ charts_data.velocity_comparison.data | tojson }},
            {{ charts_data.velocity_comparison.layout | tojson }},
            {responsive: true}
        );
        
        // Timeline Comparison Chart
        Plotly.newPlot('timeline-comparison',
            {{ charts_data.timeline_comparison.data | tojson }},
            {{ charts_data.timeline_comparison.layout | tojson }},
            {responsive: true}
        );
        
        // Workload Distribution Chart
        Plotly.newPlot('workload-distribution',
            {{ charts_data.workload_distribution.data | tojson }},
            {{ charts_data.workload_distribution.layout | tojson }},
            {responsive: true}
        );
    </script>
</body>
</html>
        ''')
        
        return template.render(
            multi_report=multi_report,
            project_links=project_links,
            charts_data=charts_data
        )