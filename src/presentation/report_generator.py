import statistics
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import plotly.graph_objects as go

from ..application.style_service import StyleService
from ..domain.entities import SimulationConfig, SimulationResult
from ..domain.forecasting import ModelInfo
from ..domain.value_objects import HistoricalData, VelocityMetrics
from .templates import ReportTemplates


class HTMLReportGenerator:
    def __init__(self, style_service: Optional[StyleService] = None, theme_name: Optional[str] = None):
        self.style_service = style_service or StyleService()
        self.theme_name = theme_name
        self.style_generator = self.style_service.get_style_generator(theme_name)
        self.chart_colors = self.style_generator.get_chart_colors()
        self.base_template = ReportTemplates.get_base_template()
        self.report_template = ReportTemplates.get_single_report_template()

    def generate(
        self,
        simulation_results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        historical_data: HistoricalData,
        remaining_work: float,
        config: SimulationConfig,
        output_path: Path,
        project_name: Optional[str] = None,
        model_info: Optional["ModelInfo"] = None,
    ) -> Path:
        # Generate charts - handle None simulation_results
        charts = {}
        if simulation_results:
            charts["probability_distribution"] = self._create_probability_chart(simulation_results, config)
            charts["forecast_timeline"] = self._create_forecast_timeline(simulation_results)
            charts["confidence_intervals"] = self._create_confidence_chart(simulation_results)
        else:
            # Create empty charts
            empty_fig = go.Figure()
            empty_fig.update_layout(
                title="No Simulation Data Available",
                annotations=[
                    {
                        "text": "Insufficient data for simulation",
                        "xref": "paper",
                        "yref": "paper",
                        "x": 0.5,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 16},
                    }
                ],
            )
            empty_json = empty_fig.to_json()
            charts["probability_distribution"] = empty_json
            charts["forecast_timeline"] = empty_json
            charts["confidence_intervals"] = empty_json

        # Velocity trend can still be shown even without simulation
        if velocity_metrics and historical_data:
            charts["velocity_trend"] = self._create_velocity_trend_chart(historical_data, velocity_metrics)
        else:
            empty_fig = go.Figure()
            empty_fig.update_layout(title="No Velocity Data Available")
            charts["velocity_trend"] = empty_fig.to_json()

        # Prepare data for template
        context = {
            "generation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_name": project_name,
            "remaining_work": remaining_work,
            "velocity_field": config.velocity_field,
            "num_simulations": config.num_simulations,
            "velocity_metrics": velocity_metrics,
            "simulation_results": simulation_results,
            "charts": charts,
            "percentiles": self._format_percentiles(simulation_results),
            "summary_stats": self._calculate_summary_stats(simulation_results, velocity_metrics, config),
            "model_info": model_info,
        }

        # Render HTML
        html_content = self._generate_html(context)

        # Save to file
        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path

    def _generate_html(self, context: dict) -> str:
        """Generate HTML with styles and content"""
        # Generate content from report template
        content = self.report_template.render(**context)

        # Generate complete HTML with styles
        styles = self.style_generator.generate_css()

        # Use model-specific title if available
        model_info = context.get("model_info")
        if model_info and hasattr(model_info, "report_title"):
            title = model_info.report_title
        else:
            title = "Statistical Forecasting Report"

        return self.base_template.render(title=title, styles=styles, content=content)

    def _create_probability_chart(self, results: SimulationResult, config: SimulationConfig) -> str:
        # Use the sprint counts directly if available
        if hasattr(results, "completion_sprints") and results.completion_sprints:
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

        # Create modern bar chart with gradient and glass effect
        fig = go.Figure(
            data=[
                go.Bar(
                    x=sprints_sorted,
                    y=probabilities,
                    name="Probability Distribution",
                    marker=dict(
                        color=probabilities,
                        colorscale=[
                            [0, self.chart_colors["primary_rgba"](0.3)],
                            [0.5, self.chart_colors["primary_rgba"](0.7)],
                            [1, self.chart_colors["primary"]],
                        ],
                        line=dict(color="rgba(255,255,255,0.8)", width=2),
                    ),
                    text=[f"{p:.1%}" for p in probabilities],
                    textposition="outside",
                    textfont=dict(size=12, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
                    hovertemplate="<b>%{x} sprints</b><br>Probability: %{y:.1%}<extra></extra>",
                )
            ]
        )

        # Add percentile lines
        for confidence, sprints in results.percentiles.items():
            fig.add_vline(
                x=sprints,
                line_dash="dash",
                line_color=self.chart_colors["low_confidence_rgba"](0.8),
                line_width=3,
                annotation_text=f"<b>{confidence*100:.0f}%</b>",
                annotation_position="top right",
                annotation_font=dict(size=14, color=self.chart_colors["low_confidence"]),
            )

        fig.update_layout(
            title=dict(
                text="<b>Sprints to Complete - Probability Distribution</b>",
                font=dict(size=22, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
            ),
            xaxis_title=dict(text="<b>Sprints to Complete</b>", font=dict(size=14)),
            yaxis_title=dict(text="<b>Probability</b>", font=dict(size=14)),
            showlegend=False,
            height=500,
            xaxis=dict(
                tickmode="linear",
                tick0=min(sprints_sorted) if sprints_sorted else 0,
                dtick=1,
                range=[min(sprints_sorted) - 0.5, max(sprints_sorted) + 0.5] if sprints_sorted else [0, 10],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="rgba(128,128,128,0.2)",
            ),
            yaxis=dict(
                tickformat=".1%",
                range=[0, max(probabilities) * 1.2] if probabilities else [0, 1],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="rgba(128,128,128,0.2)",
            ),
            bargap=0.2,
            margin=dict(t=100, b=80, l=80, r=60),
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                bordercolor="rgba(0,0,0,0.1)",
            ),
        )

        return fig.to_json()

    def _create_velocity_trend_chart(self, historical: HistoricalData, metrics: VelocityMetrics) -> str:
        if not historical.velocities:
            return go.Figure().to_json()

        fig = go.Figure()

        # Use sprint names if available, otherwise use dates
        x_values = historical.sprint_names if historical.sprint_names else historical.dates
        hover_template = (
            "<b>%{x}</b><br>Velocity: %{y:.1f}<extra></extra>" 
            if historical.sprint_names 
            else "<b>%{x|%b %Y}</b><br>Velocity: %{y:.1f}<extra></extra>"
        )

        # Historical velocities with modern styling
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=historical.velocities,
                mode="lines+markers",
                name="Historical Velocity",
                line=dict(
                    color=self.chart_colors["data1"],
                    width=3,
                    shape="spline",
                ),
                marker=dict(
                    size=10, color=self.chart_colors["data1"], line=dict(color="white", width=2), symbol="circle"
                ),
                fill="tozeroy",
                fillcolor=self.chart_colors["data1_rgba"](0.1),
                hovertemplate=hover_template,
            )
        )

        # Average line with better styling
        fig.add_hline(
            y=metrics.average,
            line_dash="dash",
            line_color=self.chart_colors["success_rgba"](0.8),
            line_width=3,
            annotation_text=f"<b>Average: {metrics.average:.1f}</b>",
            annotation_position="right",
            annotation_font=dict(size=12, color=self.chart_colors["success"]),
        )

        # Trend line
        if len(historical.velocities) >= 2:
            x_numeric = list(range(len(historical.dates)))
            # Simple linear regression
            x_mean = sum(x_numeric) / len(x_numeric)
            y_mean = sum(historical.velocities) / len(historical.velocities)

            numerator = sum(
                (x_numeric[i] - x_mean) * (historical.velocities[i] - y_mean) for i in range(len(x_numeric))
            )
            denominator = sum((x_numeric[i] - x_mean) ** 2 for i in range(len(x_numeric)))

            if denominator != 0:
                slope = numerator / denominator
                intercept = y_mean - slope * x_mean
                trend_line = [slope * x + intercept for x in x_numeric]
            else:
                trend_line = [y_mean] * len(x_numeric)

            fig.add_trace(
                go.Scatter(
                    x=x_values,
                    y=trend_line,
                    mode="lines",
                    name="Trend",
                    line=dict(color=self.chart_colors["warning_rgba"](0.8), width=3, dash="dot"),
                    hovertemplate="<b>Trend</b><br>Value: %{y:.1f}<extra></extra>",
                )
            )

        fig.update_layout(
            title=dict(
                text="<b>Historical Velocity Trend</b>",
                font=dict(size=22, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
            ),
            xaxis_title=dict(text="<b>Sprint</b>" if historical.sprint_names else "<b>Date</b>", font=dict(size=14)),
            yaxis_title=dict(text="<b>Velocity (Story Points)</b>", font=dict(size=14)),
            height=450,
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="rgba(128,128,128,0.2)",
            ),
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                bordercolor="rgba(0,0,0,0.1)",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                bgcolor="rgba(255,255,255,0.8)",
                bordercolor="rgba(0,0,0,0.1)",
                borderwidth=1,
            ),
            margin=dict(t=100, b=80, l=80, r=60),
        )

        return fig.to_json()

    def _create_cycle_time_chart(self, historical: HistoricalData) -> str:
        if not historical.cycle_times:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="Cycle time data not available<br>(Requires resolved date information)",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray"),
            )
            fig.update_layout(
                title="Cycle Time Distribution", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False)
            )
            return fig.to_json()

        fig = go.Figure(
            data=[
                go.Histogram(
                    x=historical.cycle_times,
                    nbinsx=30,
                    name="Cycle Time Distribution",
                    marker=dict(
                        color=self.chart_colors["accent_rgba"](0.8),
                        line=dict(color="white", width=2),
                        pattern_shape="\\",
                        pattern_solidity=0.1,
                    ),
                    hovertemplate="<b>%{x} days</b><br>Count: %{y}<extra></extra>",
                )
            ]
        )

        # Add average line with modern styling
        avg_cycle_time = statistics.mean(historical.cycle_times)
        fig.add_vline(
            x=avg_cycle_time,
            line_dash="dash",
            line_color=self.chart_colors["success_rgba"](0.8),
            line_width=3,
            annotation_text=f"<b>Avg: {avg_cycle_time:.1f} days</b>",
            annotation_position="top right",
            annotation_font=dict(size=12, color=self.chart_colors["success"]),
        )

        fig.update_layout(
            title=dict(
                text="<b>Cycle Time Distribution</b>",
                font=dict(size=22, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
            ),
            xaxis_title=dict(text="<b>Days</b>", font=dict(size=14)),
            yaxis_title=dict(text="<b>Frequency</b>", font=dict(size=14)),
            showlegend=False,
            height=450,
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=False,
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="rgba(128,128,128,0.2)",
            ),
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                bordercolor="rgba(0,0,0,0.1)",
            ),
            bargap=0.1,
            margin=dict(t=100, b=80, l=80, r=60),
        )

        return fig.to_json()

    def _create_forecast_timeline(self, results: SimulationResult) -> str:
        # Create a timeline showing confidence levels
        today = datetime.now()

        # Get sprint counts and convert to days for timeline
        # min_sprints = min(results.percentiles.values())
        max_sprints = max(results.percentiles.values())

        # Use sprint duration from config (passed through SimulationResult)
        sprint_duration = 14  # Default, should be passed from config
        if hasattr(results, "sprint_duration_days"):
            sprint_duration = results.sprint_duration_days

        max_days = max_sprints * sprint_duration

        # Create timeline with weeks
        timeline_dates = []
        current_date = today
        while (current_date - today).days <= max_days + sprint_duration:
            timeline_dates.append(current_date)
            current_date += timedelta(days=7)  # Weekly increments

        fig = go.Figure()

        # Add modern timeline with gradient
        fig.add_trace(
            go.Scatter(
                x=timeline_dates,
                y=[0] * len(timeline_dates),
                mode="lines",
                line=dict(color="rgba(200,200,200,0.5)", width=4, shape="spline"),
                showlegend=False,
                hoverinfo="skip",
            )
        )

        # Group confidence levels by sprint count
        sprint_groups = {}
        for confidence, sprints in results.percentiles.items():
            if sprints not in sprint_groups:
                sprint_groups[sprints] = []
            sprint_groups[sprints].append(confidence)

        # Sort groups by sprint count
        sorted_groups = sorted(sprint_groups.items())

        # Add confidence markers
        for sprints, confidences in sorted_groups:
            days = sprints * sprint_duration
            date = today + timedelta(days=int(days))

            # Sort confidences for this sprint count
            confidences.sort()

            # Determine color based on highest confidence in group
            highest_confidence = confidences[-1]
            if highest_confidence <= 0.5:
                color = self.chart_colors["high_confidence"]
            elif highest_confidence <= 0.85:
                color = self.chart_colors["medium_confidence"]
            else:
                color = self.chart_colors["low_confidence"]

            # Create label showing all confidence levels for this sprint count
            if len(confidences) == 1:
                label = f"{confidences[0]*100:.0f}%<br>{sprints:.0f} sprints"
            else:
                confidence_text = ", ".join([f"{c*100:.0f}%" for c in confidences])
                label = f"{confidence_text}<br>{sprints:.0f} sprints"

            fig.add_trace(
                go.Scatter(
                    x=[date],
                    y=[0],
                    mode="markers+text",
                    marker=dict(size=24, color=color, symbol="diamond", line=dict(color="white", width=2)),
                    text=[f"<b>{label}</b>"],
                    textposition="top center",
                    textfont=dict(size=12, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
                    showlegend=False,
                    name=f"{confidence_text if len(confidences) > 1 else f'{confidences[0]*100:.0f}%'} Confidence",
                    hovertemplate="<b>%{x|%b %d, %Y}</b><br>" + label.replace("<br>", "<br>") + "<extra></extra>",
                )
            )

        # Add today marker with glow effect
        fig.add_trace(
            go.Scatter(
                x=[today],
                y=[0],
                mode="markers+text",
                marker=dict(
                    size=20, color=self.chart_colors["primary"], symbol="star", line=dict(color="white", width=3)
                ),
                text=["<b>Today</b>"],
                textposition="bottom center",
                textfont=dict(size=14, color=self.chart_colors["primary"]),
                showlegend=False,
                hovertemplate="<b>Today</b><br>%{x|%b %d, %Y}<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="<b>Forecast Timeline</b>",
                font=dict(size=22, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
            ),
            xaxis_title=dict(text="<b>Date</b>", font=dict(size=14)),
            yaxis=dict(visible=False, range=[-0.6, 0.6]),
            height=350,
            xaxis=dict(
                tickformat="%b %d",
                tickangle=-45,
                range=[today - timedelta(days=7), today + timedelta(days=max_days + sprint_duration)],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=False,
            ),
            hovermode="closest",
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                bordercolor="rgba(0,0,0,0.1)",
            ),
            margin=dict(t=100, b=80, l=60, r=60),
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
            # Use semantic colors based on confidence levels
            if c <= 0.5:
                colors.append(self.chart_colors["high_confidence"])  # Green - High confidence
            elif c <= 0.7:
                colors.append(self.chart_colors["high_confidence"])  # Still green for 70%
            elif c <= 0.85:
                colors.append(self.chart_colors["medium_confidence"])  # Amber - Medium confidence
            else:
                colors.append(self.chart_colors["low_confidence"])  # Red - Low confidence

        fig = go.Figure(
            data=[
                go.Bar(
                    x=labels,
                    y=sprints,
                    marker=dict(
                        color=colors,
                        line=dict(color="white", width=2),
                    ),
                    text=[f"<b>{s:.0f} sprints</b>" for s in sprints],
                    textposition="auto",
                    textfont=dict(size=14, color="white"),
                    hovertemplate="<b>%{x} Confidence</b><br>Sprints: %{y:.0f}<extra></extra>",
                )
            ]
        )

        fig.update_layout(
            title=dict(
                text="<b>Sprints to Complete by Confidence Level</b>",
                font=dict(size=22, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
            ),
            xaxis_title=dict(text="<b>Confidence Level</b>", font=dict(size=14)),
            yaxis_title=dict(text="<b>Sprints</b>", font=dict(size=14)),
            showlegend=False,
            height=450,
            yaxis=dict(
                tickmode="linear",
                tick0=0,
                dtick=1,
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor="rgba(128,128,128,0.2)",
            ),
            xaxis=dict(
                showgrid=False,
            ),
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            font=dict(family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif", size=12),
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                bordercolor="rgba(0,0,0,0.1)",
            ),
            bargap=0.3,
            margin=dict(t=100, b=80, l=80, r=60),
        )

        return fig.to_json()

    def _create_throughput_chart(self, historical: HistoricalData) -> str:
        if not historical.throughput or not historical.dates:
            # Create empty chart with message
            fig = go.Figure()
            fig.add_annotation(
                text="Throughput data not available<br>(Requires resolved date information)",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="gray"),
            )
            fig.update_layout(
                title="Weekly Throughput", height=400, xaxis=dict(visible=False), yaxis=dict(visible=False)
            )
            return fig.to_json()

        fig = go.Figure(
            data=[
                go.Bar(
                    x=historical.dates[: len(historical.throughput)],
                    y=historical.throughput,
                    marker_color=self.chart_colors["secondary_rgba"](0.7),
                    marker_line_color=self.chart_colors["secondary"],
                    marker_line_width=1,
                )
            ]
        )

        # Add average line
        if historical.throughput:
            avg_throughput = statistics.mean(historical.throughput)
            fig.add_hline(
                y=avg_throughput,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Avg: {avg_throughput:.1f} issues/week",
            )

        fig.update_layout(
            title="Weekly Throughput", xaxis_title="Week", yaxis_title="Issues Completed", showlegend=False, height=400
        )

        return fig.to_json()

    def _format_percentiles(self, results: SimulationResult) -> Dict[str, float]:
        if not results:
            return {"p50": 0, "p85": 0}
        return {f"p{int(k*100)}": v for k, v in results.percentiles.items()}

    def _calculate_summary_stats(
        self, results: SimulationResult, velocity_metrics: VelocityMetrics, config: SimulationConfig
    ) -> Dict:
        if not results:
            return {}
        today = datetime.now()
        summary = {}

        # Map confidence levels to labels, including 70% if present
        confidence_mapping = {
            0.5: ("50% (Most Likely)", "confidence-high"),
            0.7: ("70% (Probable)", "confidence-medium"),
            0.85: ("85% (Confident)", "confidence-medium"),
            0.95: ("95% (Conservative)", "confidence-low"),
        }

        # Track seen sprint values to avoid duplicates
        # seen_sprints = set()

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
                    "class": css_class,
                }

        return summary
