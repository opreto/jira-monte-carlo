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
    <h1>
        {% if model_info and model_info.report_title %}{{ model_info.report_title }}
        {% else %}Statistical Forecasting Report{% endif %}
        {% if project_name %}: {{ project_name }}{% endif %}
    </h1>
    {% if model_info and model_info.report_subtitle %}
    <p class="subtitle">{{ model_info.report_subtitle }}</p>
    {% endif %}
    <p class="subtitle">Generated on {{ generation_date }}</p>
</div>

{% if scenario_banner %}
{{ scenario_banner|safe }}
{% endif %}

{% if jql_query %}
<div class="jql-query-container">
    <h3>Data Selection Query (JQL)</h3>
    <pre class="jql-query"><code>{{ jql_query }}</code></pre>
</div>
{% endif %}

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
    <div class="chart-description">
        <strong>What it shows:</strong> The likelihood of completing work in different numbers of sprints.<br>
        <strong>Why it matters:</strong> Helps set realistic expectations and manage stakeholder commitments.<br>
        <strong>What to look for:</strong> The shape of the distribution (narrow = predictable, wide = uncertain) and where your target date falls on the curve.
    </div>
    <div id="probability-distribution"></div>
</div>

<div class="chart-container">
    <h2>Forecast Timeline</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Projected completion dates with different confidence levels.<br>
        <strong>Why it matters:</strong> Visualizes the range of possible outcomes and risk levels.<br>
        <strong>What to look for:</strong> The spread between optimistic (50%) and conservative (95%) estimates indicates project uncertainty.
    </div>
    <div id="forecast-timeline"></div>
</div>

<div class="chart-container">
    <h2>Historical Velocity Trend</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Team velocity over recent sprints with trend line.<br>
        <strong>Why it matters:</strong> Reveals if team performance is improving, declining, or stable.<br>
        <strong>What to look for:</strong> Consistency (low variance = predictable), trend direction, and any outliers that might skew forecasts.
    </div>
    <div id="velocity-trend"></div>
</div>

<div class="chart-container">
    <h2>Remaining Work Distribution
        <div class="chart-toggle">
            <button id="pie-toggle" class="toggle-btn" onclick="toggleChartType('pie')">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path>
                    <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
                </svg>
                Pie
            </button>
            <button id="bar-toggle" class="toggle-btn active" onclick="toggleChartType('bar')">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <rect x="2" y="13" width="6" height="8"></rect>
                    <rect x="10" y="9" width="6" height="12"></rect>
                    <rect x="18" y="5" width="6" height="16"></rect>
                </svg>
                Bar
            </button>
        </div>
    </h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Breakdown of remaining work by size or category.<br>
        <strong>Why it matters:</strong> Identifies where effort is concentrated and potential bottlenecks.<br>
        <strong>What to look for:</strong> Large items that might benefit from splitting, or categories with disproportionate work.
    </div>
    <div id="story-size-breakdown" class="chart-transition"></div>
</div>

<div class="chart-container">
    <h2>Confidence Intervals</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Range of completion estimates at different confidence levels.<br>
        <strong>Why it matters:</strong> Quantifies uncertainty and helps with risk-based planning.<br>
        <strong>What to look for:</strong> Width of intervals (narrow = more certain) and which confidence level aligns with your risk tolerance.
    </div>
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

{% if process_health_metrics %}
<div class="chart-container">
    <h2>Process Health Score</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Overall health of your development process across multiple dimensions.<br>
        <strong>Why it matters:</strong> Identifies process improvement opportunities before they impact delivery.<br>
        <strong>What to look for:</strong> Scores below 70% indicate areas needing attention. Review the breakdown for specific issues.
    </div>
    <div id="health-score-gauge"></div>
    
    {% if process_health_metrics.health_score_breakdown %}
    <!-- Health Score Breakdown Chart -->
    <div id="health-score-breakdown" style="margin-top: 20px;"></div>
    
    <!-- Health Score Breakdown Details -->
    <div style="margin-top: 30px;">
        <h3 style="margin-bottom: 15px;">Score Breakdown & Insights</h3>
        {% for component in process_health_metrics.health_score_breakdown %}
        <div style="margin-bottom: 20px; padding: 15px; background: rgba(0,0,0,0.02); border-radius: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h4 style="margin: 0; font-size: 16px;">{{ component.name }}</h4>
                <span style="font-size: 20px; font-weight: bold; 
                    color: {% if component.score >= 0.8 %}#28a745
                    {% elif component.score >= 0.6 %}#ffc107
                    {% else %}#dc3545{% endif %};">
                    {{ (component.score * 100)|round|int }}%
                </span>
            </div>
            <p style="margin: 5px 0; color: #666; font-size: 14px;">{{ component.description }}</p>
            
            {% if component.insights %}
            <div style="margin-top: 10px;">
                <strong style="font-size: 14px;">Current State:</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    {% for insight in component.insights %}
                    <li style="font-size: 14px; color: #666;">{{ insight }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if component.recommendations %}
            <div style="margin-top: 10px;">
                <strong style="font-size: 14px; color: #333;">Recommendations:</strong>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    {% for recommendation in component.recommendations %}
                    <li style="font-size: 14px; color: #333; font-style: italic;">{{ recommendation }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if component.detail_items %}
            <div style="margin-top: 10px;">
                <details class="issue-details">
                    <summary style="cursor: pointer; font-size: 14px; color: #0066cc; font-weight: 500;">
                        View {{ component.detail_items|length }} affected items ▶
                    </summary>
                    <div class="issue-list" style="margin-top: 10px; max-height: 300px; overflow-y: auto;">
                        <table style="width: 100%; font-size: 13px; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #f8f9fa; border-bottom: 2px solid #dee2e6;">
                                    <th style="padding: 8px; text-align: left;">Key</th>
                                    <th style="padding: 8px; text-align: left;">Summary</th>
                                    <th style="padding: 8px; text-align: left;">Age</th>
                                    <th style="padding: 8px; text-align: left;">Status</th>
                                    <th style="padding: 8px; text-align: left;">Assignee</th>
                                </tr>
                            </thead>
                            <tbody>
                                {% for item in component.detail_items %}
                                <tr style="border-bottom: 1px solid #dee2e6;">
                                    <td style="padding: 8px;">
                                        {% if jira_url %}
                                        <a href="{{ jira_url }}/browse/{{ item.key }}" target="_blank" style="color: #0066cc; text-decoration: none;">{{ item.key }}</a>
                                        {% else %}
                                        <span style="color: #0066cc;">{{ item.key }}</span>
                                        {% endif %}
                                    </td>
                                    <td style="padding: 8px;">{{ item.summary[:50] }}{% if item.summary|length > 50 %}...{% endif %}</td>
                                    <td style="padding: 8px;">{{ item.age_days }} days</td>
                                    <td style="padding: 8px;">
                                        <span class="status-badge status-{{ item.type }}" 
                                              style="padding: 2px 8px; border-radius: 12px; font-size: 12px; 
                                                     background: {% if item.type == 'abandoned' %}#dc3545{% else %}#ffc107{% endif %}; 
                                                     color: white;">
                                            {{ item.status }}
                                        </span>
                                    </td>
                                    <td style="padding: 8px;">{{ item.assignee }}</td>
                                </tr>
                                {% endfor %}
                            </tbody>
                        </table>
                    </div>
                </details>
            </div>
            {% endif %}
        </div>
        {% endfor %}
    </div>
    {% else %}
    <!-- Limited health data message -->
    <div style="margin-top: 20px; padding: 15px; background: rgba(255,193,7,0.1); border-radius: 8px;">
        <p style="margin: 0; color: #856404;">
            <strong>Limited Health Data:</strong> Additional metrics require more complete data fields 
            (created dates, labels, etc.) to provide detailed insights.
        </p>
    </div>
    {% endif %}
</div>

{% if process_health_metrics.aging_analysis %}
<div class="chart-container">
    <h2>Aging Work Items</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Distribution of work items by age category.<br>
        <strong>Why it matters:</strong> Old items represent risk, blocked work, or forgotten tasks.<br>
        <strong>What to look for:</strong> Items over 30 days old (stale/abandoned) need review or closure.
    </div>
    <div id="aging-distribution"></div>
</div>

<div class="chart-container">
    <h2>Average Age by Status</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> How long items spend in each workflow state.<br>
        <strong>Why it matters:</strong> Reveals bottlenecks and process inefficiencies.<br>
        <strong>What to look for:</strong> Statuses with unusually high average age indicate workflow problems.
    </div>
    <div id="aging-by-status"></div>
</div>
{% endif %}

{% if process_health_metrics.wip_analysis %}
<div class="chart-container">
    <h2>Work In Progress</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Current work items in each workflow state.<br>
        <strong>Why it matters:</strong> Too much WIP reduces flow and increases cycle time.<br>
        <strong>What to look for:</strong> WIP exceeding limits (red bars) or uneven distribution suggesting bottlenecks.
    </div>
    <div id="wip-by-status"></div>
</div>
{% endif %}

{% if process_health_metrics.sprint_health %}
<div class="chart-container">
    <h2>Sprint Completion Trend</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Percentage of committed work completed each sprint.<br>
        <strong>Why it matters:</strong> Measures planning accuracy and delivery predictability.<br>
        <strong>What to look for:</strong> Consistent completion rates above 80% indicate mature planning. High variance suggests estimation issues.
    </div>
    <div id="sprint-completion-trend"></div>
</div>

<div class="chart-container">
    <h2>Sprint Scope Changes</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Work added and removed during sprints.<br>
        <strong>Why it matters:</strong> Excessive scope change disrupts team focus and predictability.<br>
        <strong>What to look for:</strong> Net changes above 20% suggest planning or prioritization issues. The trend line shows if it's improving.
    </div>
    <div id="sprint-scope-change"></div>
</div>
{% endif %}

{% if process_health_metrics.blocked_items %}
<div class="chart-container">
    <h2>Blocked Items by Severity</h2>
    <div class="chart-description">
        <strong>What it shows:</strong> Blocked work categorized by how long it's been blocked.<br>
        <strong>Why it matters:</strong> Blocked items waste capacity and delay delivery.<br>
        <strong>What to look for:</strong> High-severity blocks (>5 days) need immediate escalation.
    </div>
    <div id="blocked-severity"></div>
</div>
{% endif %}
{% endif %}

<div class="footer">
    <p>
        {% if model_info and model_info.name %}{{ model_info.name }}
        {% else %}Statistical Forecasting{% endif %} by Opreto Agile Analytics
    </p>
    {% if model_info and model_info.methodology_description %}
    <p>{{ model_info.methodology_description }}</p>
    {% endif %}
    <p>Based on {{ "{:,}".format(num_simulations) }} iterations • Analysis of historical data and velocity metrics</p>
    {% if reporting_capabilities %}
    <p><small>
        Available reports: {{ reporting_capabilities.available_reports|length }} of 
        {{ reporting_capabilities.all_reports|length }} • 
        Data quality score: {{ "%.0f"|format(reporting_capabilities.data_quality_score * 100) }}%
        {% if reporting_capabilities.unavailable_reports %}
        <span class="tooltip">
            <span class="tooltip-icon">i</span>
            <span class="tooltip-text">
                <strong>Unavailable Reports:</strong><br>
                {% for report_name, requirements in reporting_capabilities.unavailable_reports.items() %}
                • {{ report_name }}: Missing {{ requirements|join(', ') }}<br>
                {% endfor %}
            </span>
        </span>
        {% endif %}
    </small></p>
    {% endif %}
</div>

<script>
    // Store chart data globally for toggling
    let storySizeCharts = {};
    let currentChartType = 'bar';
    
    // Render all charts
    {% for chart_id, chart_json in charts.items() %}
    try {
        {% if chart_id == 'story_size_breakdown' %}
        // Special handling for story size breakdown with multiple chart types
        storySizeCharts = {
            pie: {{ chart_json.pie|safe }},
            bar: {{ chart_json.bar|safe }}
        };
        
        // Render initial bar chart
        if (storySizeCharts.bar) {
            const barData = storySizeCharts.bar;
            Plotly.newPlot('story-size-breakdown', barData.data, barData.layout, {responsive: true});
        }
        {% else %}
        // Regular chart rendering
        const chartData = {{ chart_json|safe }};
        Plotly.newPlot('{{ chart_id.replace("_", "-") }}', chartData.data, chartData.layout, {responsive: true});
        {% endif %}
    } catch (e) {
        console.error('Error rendering chart {{ chart_id }}:', e);
    }
    {% endfor %}
    
    // Render process health charts
    {% for chart_id, chart_json in process_health_charts.items() %}
    try {
        const phChartData = {{ chart_json|safe }};
        Plotly.newPlot('{{ chart_id.replace("_", "-") }}', phChartData.data, phChartData.layout, {responsive: true});
    } catch (e) {
        console.error('Error rendering process health chart {{ chart_id }}:', e);
    }
    {% endfor %}
    
    // Toggle function for chart type
    function toggleChartType(type) {
        if (type === currentChartType || !storySizeCharts[type]) return;
        
        // Store current scroll position
        const scrollPosition = window.scrollY;
        
        // Update button states
        document.getElementById('pie-toggle').classList.toggle('active', type === 'pie');
        document.getElementById('bar-toggle').classList.toggle('active', type === 'bar');
        
        // Get chart data
        const chartData = storySizeCharts[type];
        
        // Get container and lock its height
        const container = document.getElementById('story-size-breakdown');
        const containerHeight = container.offsetHeight;
        container.style.height = containerHeight + 'px';
        container.style.opacity = '0';
        
        setTimeout(() => {
            // Update chart
            Plotly.react('story-size-breakdown', chartData.data, chartData.layout, {responsive: true});
            
            // Fade in and restore height to auto
            container.style.opacity = '1';
            setTimeout(() => {
                container.style.height = 'auto';
                // Restore scroll position
                window.scrollTo(0, scrollPosition);
            }, 50);
            currentChartType = type;
        }, 300);
    }
</script>
"""
        return Template(template_str)

    @staticmethod
    def get_dashboard_template() -> Template:
        """Get multi-project dashboard template"""
        template_str = """
<div class="header">
    <h1>
        {% if model_info and model_info.report_title %}Multi-Project {{ model_info.name }} Dashboard
        {% else %}Multi-Project Forecasting Dashboard{% endif %}
    </h1>
    <p class="subtitle">
        {% if model_info and model_info.report_subtitle %}{{ model_info.report_subtitle }} • {% endif %}
        Analyzing {{ multi_report.projects|length }} projects • 
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
    <p>
        {% if model_info and model_info.methodology_description %}{{ model_info.methodology_description }}
        {% else %}Statistical Forecasting{% endif %} by Opreto Agile Analytics
    </p>
</div>
"""
        return Template(template_str)
