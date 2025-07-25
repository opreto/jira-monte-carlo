import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from jinja2 import Template
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
from typing import List, Dict
import json

from ..domain.entities import SimulationResult, SimulationConfig
from ..domain.value_objects import VelocityMetrics, HistoricalData


class HTMLReportGenerator:
    def __init__(self):
        self.template = self._load_template()
    
    def generate(self,
                simulation_results: SimulationResult,
                velocity_metrics: VelocityMetrics,
                historical_data: HistoricalData,
                remaining_work: float,
                config: SimulationConfig,
                output_path: Path) -> Path:
        
        # Generate charts
        charts = {
            "probability_distribution": self._create_probability_chart(simulation_results, config),
            "velocity_trend": self._create_velocity_trend_chart(historical_data, velocity_metrics),
            "forecast_timeline": self._create_forecast_timeline(simulation_results),
            "confidence_intervals": self._create_confidence_chart(simulation_results)
        }
        
        # Prepare data for template
        context = {
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "remaining_work": remaining_work,
            "velocity_field": config.velocity_field,
            "num_simulations": config.num_simulations,
            "velocity_metrics": velocity_metrics,
            "simulation_results": simulation_results,
            "charts": charts,
            "percentiles": self._format_percentiles(simulation_results),
            "summary_stats": self._calculate_summary_stats(simulation_results, velocity_metrics, config)
        }
        
        # Render HTML
        html_content = self.template.render(**context)
        
        # Save to file
        with open(output_path, "w") as f:
            f.write(html_content)
        
        return output_path
    
    def _load_template(self) -> Template:
        template_str = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jira Monte Carlo Simulation Report</title>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
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
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        h1 {
            margin: 0;
            font-size: 2.5rem;
        }
        
        .subtitle {
            opacity: 0.9;
            margin-top: 0.5rem;
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
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
            margin: 0.5rem 0;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.9rem;
        }
        
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .chart-title {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: #333;
        }
        
        .summary-table {
            width: 100%;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .summary-table th {
            background: #667eea;
            color: white;
            padding: 1rem;
            text-align: left;
        }
        
        .summary-table td {
            padding: 1rem;
            border-bottom: 1px solid #eee;
        }
        
        .summary-table tr:last-child td {
            border-bottom: none;
        }
        
        .confidence-high {
            background-color: #d4edda;
        }
        
        .confidence-medium {
            background-color: #fff3cd;
        }
        
        .confidence-low {
            background-color: #f8d7da;
        }
        
        .footer {
            text-align: center;
            color: #666;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #ddd;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Monte Carlo Simulation Report</h1>
        <p class="subtitle">Generated on {{ generation_date }}</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-label">Remaining Work</div>
            <div class="metric-value">{{ "%.1f"|format(remaining_work) }}</div>
            <div class="metric-label">{{ velocity_field }}</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">Average Velocity</div>
            <div class="metric-value">{{ "%.1f"|format(velocity_metrics.average) }}</div>
            <div class="metric-label">per sprint</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">50% Confidence</div>
            <div class="metric-value">{{ "%.0f"|format(percentiles.p50) }}</div>
            <div class="metric-label">sprints</div>
        </div>
        
        <div class="metric-card">
            <div class="metric-label">85% Confidence</div>
            <div class="metric-value">{{ "%.0f"|format(percentiles.p85) }}</div>
            <div class="metric-label">sprints</div>
        </div>
    </div>
    
    <div class="chart-container">
        <h2 class="chart-title">Probability Distribution</h2>
        <div id="probability-distribution"></div>
    </div>
    
    <div class="chart-container">
        <h2 class="chart-title">Forecast Timeline</h2>
        <div id="forecast-timeline"></div>
    </div>
    
    <div class="chart-container">
        <h2 class="chart-title">Historical Velocity Trend</h2>
        <div id="velocity-trend"></div>
    </div>
    
    <div class="chart-container">
        <h2 class="chart-title">Confidence Intervals</h2>
        <div id="confidence-intervals"></div>
    </div>
    
    
    <div class="chart-container">
        <h2 class="chart-title">Completion Forecast Summary</h2>
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
        <p>Monte Carlo Simulation based on {{ "{:,}".format(num_simulations) }} iterations</p>
        <p>Analysis based on historical data and velocity metrics</p>
    </div>
    
    <script>
        // Render all charts
        {% for chart_id, chart_json in charts.items() %}
        try {
            const chartData = {{ chart_json|safe }};
            Plotly.newPlot('{{ chart_id.replace("_", "-") }}', chartData.data, chartData.layout);
        } catch (e) {
            console.error('Error rendering chart {{ chart_id }}:', e);
            console.error('Chart data:', {{ chart_json|safe }});
        }
        {% endfor %}
    </script>
</body>
</html>
        '''
        return Template(template_str)
    
    def _create_probability_chart(self, results: SimulationResult, config: SimulationConfig) -> str:
        # Use the sprint counts directly if available
        if hasattr(results, 'completion_sprints') and results.completion_sprints:
            completion_sprints = results.completion_sprints
        else:
            # Fallback: reconstruct from dates
            today = datetime.now()
            completion_sprints = []
            for date in results.completion_dates:
                days_diff = (date - today).days
                sprints = round(days_diff / config.sprint_duration_days)
                completion_sprints.append(sprints)
        
        # Count occurrences of each sprint count
        from collections import Counter
        sprint_counts = Counter(completion_sprints)
        sprints_sorted = sorted(sprint_counts.keys())
        counts = [sprint_counts[s] for s in sprints_sorted]
        
        # Calculate probabilities
        total_simulations = len(completion_sprints)
        probabilities = [c / total_simulations for c in counts]
        
        # Create simple bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=sprints_sorted,
                y=probabilities,
                name='Probability Distribution',
                marker_color='rgba(102, 126, 234, 0.7)',
                marker_line_color='rgba(102, 126, 234, 1)',
                marker_line_width=1,
                text=[f'{p:.1%}' for p in probabilities],
                textposition='outside'
            )
        ])
        
        # Add percentile lines
        for confidence, sprints in results.percentiles.items():
            fig.add_vline(
                x=sprints, 
                line_dash="dash", 
                line_color="red",
                line_width=2,
                annotation_text=f"{confidence*100:.0f}%",
                annotation_position="top right"
            )
        
        fig.update_layout(
            title="Sprints to Complete - Probability Distribution",
            xaxis_title="Sprints to Complete",
            yaxis_title="Probability",
            showlegend=False,
            height=400,
            xaxis=dict(
                tickmode='linear',
                tick0=min(sprints_sorted) if sprints_sorted else 0,
                dtick=1,
                range=[min(sprints_sorted) - 0.5, max(sprints_sorted) + 0.5] if sprints_sorted else [0, 10]
            ),
            yaxis=dict(
                tickformat='.1%'
            ),
            bargap=0.1
        )
        
        return fig.to_json()
    
    def _create_velocity_trend_chart(self, historical: HistoricalData, metrics: VelocityMetrics) -> str:
        if not historical.velocities:
            return go.Figure().to_json()
        
        fig = go.Figure()
        
        # Historical velocities
        fig.add_trace(go.Scatter(
            x=historical.dates,
            y=historical.velocities,
            mode='lines+markers',
            name='Historical Velocity',
            line=dict(color='rgba(102, 126, 234, 1)', width=2),
            marker=dict(size=8)
        ))
        
        # Average line
        fig.add_hline(
            y=metrics.average,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Average: {metrics.average:.1f}"
        )
        
        # Trend line
        if len(historical.velocities) >= 2:
            x_numeric = list(range(len(historical.dates)))
            z = np.polyfit(x_numeric, historical.velocities, 1)
            p = np.poly1d(z)
            fig.add_trace(go.Scatter(
                x=historical.dates,
                y=p(x_numeric),
                mode='lines',
                name='Trend',
                line=dict(color='rgba(255, 0, 0, 0.5)', width=2, dash='dash')
            ))
        
        fig.update_layout(
            title="Historical Velocity Trend",
            xaxis_title="Date",
            yaxis_title="Velocity",
            height=400
        )
        
        return fig.to_json()
    
    def _create_cycle_time_chart(self, historical: HistoricalData) -> str:
        if not historical.cycle_times:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="Cycle time data not available<br>(Requires resolved date information)",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title="Cycle Time Distribution",
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig.to_json()
        
        fig = go.Figure(data=[
            go.Histogram(
                x=historical.cycle_times,
                nbinsx=30,
                name='Cycle Time Distribution',
                marker_color='rgba(234, 102, 126, 0.7)',
                marker_line_color='rgba(234, 102, 126, 1)',
                marker_line_width=1
            )
        ])
        
        # Add average line
        avg_cycle_time = np.mean(historical.cycle_times)
        fig.add_vline(
            x=avg_cycle_time,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Avg: {avg_cycle_time:.1f} days"
        )
        
        fig.update_layout(
            title="Cycle Time Distribution",
            xaxis_title="Days",
            yaxis_title="Frequency",
            showlegend=False,
            height=400
        )
        
        return fig.to_json()
    
    def _create_forecast_timeline(self, results: SimulationResult) -> str:
        # Create a timeline showing confidence levels
        today = datetime.now()
        
        # Get sprint counts and convert to days for timeline
        min_sprints = min(results.percentiles.values())
        max_sprints = max(results.percentiles.values())
        
        # Use sprint duration from config (passed through SimulationResult)
        sprint_duration = 14  # Default, should be passed from config
        if hasattr(results, 'sprint_duration_days'):
            sprint_duration = results.sprint_duration_days
        
        max_days = max_sprints * sprint_duration
        
        # Create timeline with weeks
        timeline_dates = []
        current_date = today
        while (current_date - today).days <= max_days + sprint_duration:
            timeline_dates.append(current_date)
            current_date += timedelta(days=7)  # Weekly increments
        
        fig = go.Figure()
        
        # Add timeline background
        fig.add_trace(go.Scatter(
            x=timeline_dates,
            y=[0] * len(timeline_dates),
            mode='lines',
            line=dict(color='lightgray', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add confidence markers
        for confidence, sprints in sorted(results.percentiles.items()):
            days = sprints * sprint_duration
            date = today + timedelta(days=int(days))
            
            if confidence <= 0.5:
                color = 'green'
            elif confidence <= 0.85:
                color = 'orange'
            else:
                color = 'red'
                
            fig.add_trace(go.Scatter(
                x=[date],
                y=[0],
                mode='markers+text',
                marker=dict(size=20, color=color, symbol='diamond'),
                text=[f"{confidence*100:.0f}%<br>{sprints:.0f} sprints"],
                textposition='top center',
                showlegend=False,
                name=f"{confidence*100:.0f}% Confidence"
            ))
        
        # Add today marker
        fig.add_trace(go.Scatter(
            x=[today],
            y=[0],
            mode='markers+text',
            marker=dict(size=15, color='blue', symbol='star'),
            text=['Today'],
            textposition='bottom center',
            showlegend=False
        ))
        
        fig.update_layout(
            title="Forecast Timeline",
            xaxis_title="Date",
            yaxis=dict(visible=False, range=[-0.5, 0.5]),
            height=300,
            xaxis=dict(
                tickformat='%b %d',
                tickangle=-45,
                range=[today - timedelta(days=7), today + timedelta(days=max_days + sprint_duration)]
            ),
            hovermode='closest'
        )
        
        return fig.to_json()
    
    def _create_confidence_chart(self, results: SimulationResult) -> str:
        confidences = list(results.percentiles.keys())
        sprints = list(results.percentiles.values())
        
        # Create labels showing both confidence and sprint count
        labels = []
        colors = []
        for c, s in zip(confidences, sprints):
            labels.append(f"{c*100:.0f}%")
            if c <= 0.5:
                colors.append('green')
            elif c <= 0.7:
                colors.append('lightgreen')
            elif c <= 0.85:
                colors.append('orange')
            else:
                colors.append('red')
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=sprints,
                marker_color=colors,
                text=[f"{s:.0f} sprints" for s in sprints],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Sprints to Complete by Confidence Level",
            xaxis_title="Confidence Level",
            yaxis_title="Sprints",
            showlegend=False,
            height=400,
            yaxis=dict(
                tickmode='linear',
                tick0=0,
                dtick=1
            )
        )
        
        return fig.to_json()
    
    def _create_throughput_chart(self, historical: HistoricalData) -> str:
        if not historical.throughput or not historical.dates:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="Throughput data not available<br>(Requires resolved date information)",
                xref="paper", yref="paper",
                x=0.5, y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray")
            )
            fig.update_layout(
                title="Weekly Throughput",
                height=400,
                xaxis=dict(visible=False),
                yaxis=dict(visible=False)
            )
            return fig.to_json()
        
        fig = go.Figure(data=[
            go.Bar(
                x=historical.dates[:len(historical.throughput)],
                y=historical.throughput,
                marker_color='rgba(102, 234, 126, 0.7)',
                marker_line_color='rgba(102, 234, 126, 1)',
                marker_line_width=1
            )
        ])
        
        # Add average line
        if historical.throughput:
            avg_throughput = np.mean(historical.throughput)
            fig.add_hline(
                y=avg_throughput,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Avg: {avg_throughput:.1f} issues/week"
            )
        
        fig.update_layout(
            title="Weekly Throughput",
            xaxis_title="Week",
            yaxis_title="Issues Completed",
            showlegend=False,
            height=400
        )
        
        return fig.to_json()
    
    def _format_percentiles(self, results: SimulationResult) -> Dict[str, float]:
        return {
            f"p{int(k*100)}": v 
            for k, v in results.percentiles.items()
        }
    
    def _calculate_summary_stats(self, results: SimulationResult, 
                                velocity_metrics: VelocityMetrics,
                                config: SimulationConfig) -> Dict:
        today = datetime.now()
        summary = {}
        
        # Map confidence levels to labels, including 70% if present
        confidence_mapping = {
            0.5: ("50% (Most Likely)", "confidence-high"),
            0.7: ("70% (Probable)", "confidence-medium"),
            0.85: ("85% (Confident)", "confidence-medium"),
            0.95: ("95% (Conservative)", "confidence-low")
        }
        
        # Track seen sprint values to avoid duplicates
        seen_sprints = set()
        
        # Group by sprint count to handle duplicates
        sprint_to_confs = {}
        for conf, sprints in results.percentiles.items():
            sprint_count = int(sprints)
            if sprint_count not in sprint_to_confs:
                sprint_to_confs[sprint_count] = []
            sprint_to_confs[sprint_count].append(conf)
        
        # For each unique sprint count, use the lowest confidence level
        for sprint_count in sorted(sprint_to_confs.keys()):
            confs = sprint_to_confs[sprint_count]
            lowest_conf = min(confs)
            highest_conf = max(confs)
            
            if lowest_conf in confidence_mapping:
                label, css_class = confidence_mapping[lowest_conf]
                days = int(sprint_count * config.sprint_duration_days)
                date = today + timedelta(days=days)
                
                # If multiple confidence levels map to same sprints, show range
                if len(confs) > 1 and highest_conf != lowest_conf:
                    prob_range = f"{int(lowest_conf * 100)}-{int(highest_conf * 100)}"
                else:
                    prob_range = f"{int(lowest_conf * 100)}"
                
                summary[label] = {
                    "sprints": sprint_count,
                    "date": date.strftime("%Y-%m-%d"),
                    "probability": prob_range,
                    "class": css_class
                }
        
        return summary