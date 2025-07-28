"""HTML templates for reports"""
from jinja2 import Template


class ReportTemplates:
    """HTML templates for report generation"""

    @staticmethod
    def get_base_template() -> Template:
        """Get base HTML template"""
        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
{{ styles }}
    </style>
</head>
<body>
    <div class="container">
        {{ content }}
    </div>
</body>
</html>
"""
        return Template(template_str)

    @staticmethod
    def get_single_report_template() -> Template:
        """Get single project report template"""
        template_str = """
<div class="header">
    <h1>{% if model_info and model_info.report_title %}{{ model_info.report_title }}{% else %}Statistical Forecasting Report{% endif %}{% if project_name %}: {{ project_name }}{% endif %}</h1>
    {% if model_info and model_info.report_subtitle %}
    <p class="subtitle">{{ model_info.report_subtitle }}</p>
    {% endif %}
    <p class="subtitle">Generated on {{ generation_date }}</p>
</div>

<div class="metrics-grid">
    <div class="metric-card">
        <div class="label">Remaining Work</div>
        <div class="value">{{ "%.1f"|format(remaining_work) }}</div>
        <div class="label">{{ velocity_field }}</div>
    </div>
    
    <div class="metric-card">
        <div class="label">Average Velocity</div>
        <div class="value">{{ "%.1f"|format(velocity_metrics.average) }}</div>
        <div class="label">per sprint</div>
    </div>
    
    <div class="metric-card">
        <div class="label">50% Confidence</div>
        <div class="value">{{ "%.0f"|format(percentiles.p50) }}</div>
        <div class="label">sprints</div>
    </div>
    
    <div class="metric-card">
        <div class="label">85% Confidence</div>
        <div class="value">{{ "%.0f"|format(percentiles.p85) }}</div>
        <div class="label">sprints</div>
    </div>
</div>

<div class="chart-container">
    <h2>Probability Distribution</h2>
    <div id="probability-distribution"></div>
</div>

<div class="chart-container">
    <h2>Forecast Timeline</h2>
    <div id="forecast-timeline"></div>
</div>

<div class="chart-container">
    <h2>Historical Velocity Trend</h2>
    <div id="velocity-trend"></div>
</div>

<div class="chart-container">
    <h2>Remaining Work Distribution</h2>
    <div id="story-size-breakdown"></div>
</div>

<div class="chart-container">
    <h2>Confidence Intervals</h2>
    <div id="confidence-intervals"></div>
</div>

<div class="chart-container">
    <h2>Completion Forecast Summary</h2>
    <table class="summary-table">
        <thead>
            <tr>
                <th>Confidence Level</th>
                <th>Sprints to Complete</th>
                <th>Completion Date</th>
                <th>Probability</th>
            </tr>
        </thead>
        <tbody>
            {% for level, data in summary_stats.items() %}
            <tr class="{{ data.class }}">
                <td>{{ level }}</td>
                <td>{{ data.sprints }} sprints</td>
                <td>{{ data.date }}</td>
                <td>{{ data.probability }}% chance of completing by this date</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<div class="footer">
    <p>{% if model_info and model_info.name %}{{ model_info.name }}{% else %}Statistical Forecasting{% endif %} by Opreto Agile Analytics</p>
    {% if model_info and model_info.methodology_description %}
    <p>{{ model_info.methodology_description }}</p>
    {% endif %}
    <p>Based on {{ "{:,}".format(num_simulations) }} iterations • Analysis of historical data and velocity metrics</p>
</div>

<script>
    // Render all charts
    {% for chart_id, chart_json in charts.items() %}
    try {
        const chartData = {{ chart_json|safe }};
        Plotly.newPlot('{{ chart_id.replace("_", "-") }}', chartData.data, chartData.layout, {responsive: true});
    } catch (e) {
        console.error('Error rendering chart {{ chart_id }}:', e);
    }
    {% endfor %}
</script>
"""
        return Template(template_str)

    @staticmethod
    def get_dashboard_template() -> Template:
        """Get multi-project dashboard template"""
        template_str = """
<div class="header">
    <h1>{% if model_info and model_info.report_title %}Multi-Project {{ model_info.name }} Dashboard{% else %}Multi-Project Forecasting Dashboard{% endif %}</h1>
    <p class="subtitle">{% if model_info and model_info.report_subtitle %}{{ model_info.report_subtitle }} • {% endif %}Analyzing {{ multi_report.projects|length }} projects • 
        Generated {{ multi_report.generated_at.strftime('%Y-%m-%d %H:%M') }}</p>
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
        <div class="value">
            {% if multi_report.aggregated_metrics.combined_simulation_result %}
                {{ multi_report.aggregated_metrics.combined_simulation_result.percentiles.get(0.85, 0)|int }} sprints
            {% else %}
                N/A
            {% endif %}
        </div>
    </div>
</div>

<div class="data-table">
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
                <td>
                    {% if project.velocity_metrics %}
                        {{ "%.1f"|format(project.velocity_metrics.average) }}
                    {% else %}
                        N/A
                    {% endif %}
                </td>
                <td>
                    {% if project.simulation_result %}
                        {{ project.simulation_result.percentiles.get(0.5, 0)|int }}
                    {% else %}
                        N/A
                    {% endif %}
                </td>
                <td>
                    {% if project.simulation_result %}
                        {{ project.simulation_result.percentiles.get(0.85, 0)|int }}
                    {% else %}
                        N/A
                    {% endif %}
                </td>
                <td><a href="{{ project_links[project.name] }}">View Details →</a></td>
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
    <p>Statistical Forecasting by Opreto Agile Analytics</p>
</div>

<script>
    // Render all charts
    {% for chart_name, chart_data in charts_data.items() %}
    Plotly.newPlot('{{ chart_name.replace("_", "-") }}', 
        {{ chart_data.data | tojson }},
        {{ chart_data.layout | tojson }},
        {responsive: true}
    );
    {% endfor %}
</script>

<div class="footer">
    <p>{% if model_info and model_info.methodology_description %}{{ model_info.methodology_description }}{% else %}Statistical Forecasting{% endif %} by Opreto Agile Analytics</p>
</div>
"""
        return Template(template_str)
