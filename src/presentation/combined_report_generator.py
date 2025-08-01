"""Generate combined baseline/adjusted reports for velocity scenarios"""

import json
import logging
from pathlib import Path
from typing import Any, Dict

import plotly.graph_objects as go

from ..domain.entities import SimulationConfig, SimulationResult
from ..domain.forecasting import ModelInfo
from ..domain.value_objects import VelocityMetrics
from ..domain.velocity_adjustments import ScenarioComparison, VelocityScenario
from .report_generator import HTMLReportGenerator
from .templates import ReportTemplates

logger = logging.getLogger(__name__)


class CombinedReportGenerator:
    """Generate a single HTML report with both baseline and adjusted forecasts"""

    def __init__(self, base_generator: HTMLReportGenerator):
        self.base_generator = base_generator
        self.templates = ReportTemplates()

    def generate_combined_report(
        self,
        baseline_results: SimulationResult,
        adjusted_results: SimulationResult,
        scenario: VelocityScenario,
        comparison: ScenarioComparison,
        velocity_metrics: VelocityMetrics,
        historical_data: list,
        remaining_work: float,
        config: SimulationConfig,
        output_path: Path,
        project_name: str,
        model_info: ModelInfo,
        **kwargs,
    ) -> Path:
        """Generate a single report with both baseline and adjusted data"""
        logger.info(f"Generating combined baseline/adjusted report: {output_path}")

        # Prepare data for both scenarios
        baseline_data = self._prepare_chart_data(
            baseline_results,
            velocity_metrics,
            historical_data,
            remaining_work,
            config,
            "baseline",
        )

        adjusted_data = self._prepare_chart_data(
            adjusted_results,
            velocity_metrics,
            historical_data,
            remaining_work,
            config,
            "adjusted",
        )

        # Add summary stats to scenario data
        baseline_data["summary_stats"] = self.base_generator._calculate_summary_stats(
            baseline_results, velocity_metrics, config
        )
        adjusted_data["summary_stats"] = self.base_generator._calculate_summary_stats(
            adjusted_results, velocity_metrics, config
        )

        # Generate the combined report
        scenario_info = {
            "description": scenario.get_summary(),
            "comparison": comparison.get_impact_summary(),
            "adjustments": [adj.get_description() for adj in scenario.adjustments],
            "team_changes": [tc.get_description() for tc in scenario.team_changes],
        }

        # Use the base generator but with modified data
        combined_data = {
            "baseline": baseline_data,
            "adjusted": adjusted_data,
            "scenario": scenario_info,
            "current_view": "adjusted",  # Default to showing adjusted view
        }

        # Normalize the probability distributions in the scenario data
        self._normalize_scenario_data(combined_data)

        # Generate charts for both scenarios
        baseline_charts = self._generate_scenario_charts(
            baseline_results, velocity_metrics, config, "baseline"
        )
        adjusted_charts = self._generate_scenario_charts(
            adjusted_results, velocity_metrics, config, "adjusted"
        )

        # Normalize bar charts to have consistent x-axis values
        self._normalize_scenario_charts(baseline_charts, adjusted_charts)

        # Generate the report with combined data
        # Extract ml_decisions from kwargs if present
        ml_decisions = kwargs.pop("ml_decisions", None)

        # Remove any existing chart data from kwargs to avoid conflicts
        kwargs.pop("baseline_charts_data", None)
        kwargs.pop("adjusted_charts_data", None)

        self.base_generator.generate(
            simulation_results=adjusted_results,  # Use adjusted as primary
            velocity_metrics=velocity_metrics,
            historical_data=historical_data,
            remaining_work=remaining_work,
            config=config,
            output_path=output_path,
            project_name=project_name,
            model_info=model_info,
            combined_scenario_data=json.dumps(combined_data),
            scenario_banner=self._create_combined_banner(scenario, comparison),
            ml_decisions=ml_decisions,
            baseline_charts_data=baseline_charts,
            adjusted_charts_data=adjusted_charts,
            **kwargs,
        )

        return output_path

    def _generate_scenario_charts(
        self,
        results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        config: SimulationConfig,
        label: str,
    ) -> Dict[str, Any]:
        """Generate all charts for a specific scenario"""
        charts = {}

        # Import plotly here to avoid circular imports

        # Probability distribution chart
        prob_chart = self._create_probability_chart(results, config)
        if prob_chart:
            charts["probability_distribution"] = prob_chart

        # Forecast timeline chart
        timeline_chart = self._create_forecast_timeline(results)
        if timeline_chart:
            charts["forecast_timeline"] = timeline_chart

        # Confidence intervals chart
        confidence_chart = self._create_confidence_chart(results)
        if confidence_chart:
            charts["confidence_intervals"] = confidence_chart

        return charts

    def _normalize_bar_chart_data(
        self, baseline_data: list, adjusted_data: list
    ) -> tuple:
        """Normalize bar chart data to have the same x-axis values for smooth transitions

        This ensures both datasets have the same number of bars by adding empty bars
        where needed, preventing jarring layout changes during animation.

        UI Heuristic: Bar Padding Normalization
        ----------------------------------------
        Problem: When switching between baseline and adjusted scenarios, if one has
        more bars than the other (e.g., baseline shows sprints 1-5, adjusted shows
        sprints 1-7), Plotly will animate the chart resize, causing a jarring layout
        jump that disrupts the user's ability to compare values.

        Solution: We normalize both datasets to have the same x-axis values by:
        1. Finding the union of all x-values across both datasets
        2. Adding "ghost" bars with 0 values where data is missing
        3. Preserving the original text labels only for real data points

        This ensures smooth transitions where bars animate from/to zero height
        rather than appearing/disappearing and causing layout reflow.

        Documentation:
        - UX Pattern: /docs/ux-patterns/001-chart-transition-smoothing.md
        - Frontend implementation: packages/report-builder/src/renderer.tsx
        - General UI heuristics: /docs/UI_HEURISTICS.md
        """
        # Extract x values from both datasets
        baseline_x = set()
        adjusted_x = set()

        for trace in baseline_data:
            # Handle both dict and object formats
            if isinstance(trace, dict) and "x" in trace and trace["x"] is not None:
                baseline_x.update(trace["x"])
            elif hasattr(trace, "x") and trace.x is not None:
                baseline_x.update(trace.x)

        for trace in adjusted_data:
            # Handle both dict and object formats
            if isinstance(trace, dict) and "x" in trace and trace["x"] is not None:
                adjusted_x.update(trace["x"])
            elif hasattr(trace, "x") and trace.x is not None:
                adjusted_x.update(trace.x)

        # Get union of all x values
        all_x = sorted(baseline_x.union(adjusted_x))

        if not all_x:
            return baseline_data, adjusted_data

        # Normalize each dataset
        def normalize_trace(trace, all_x_values):
            # Handle dict format (which is what Plotly usually uses)
            if isinstance(trace, dict):
                if "x" not in trace or trace["x"] is None:
                    return trace

                # Create mapping of existing values
                x_to_y = dict(zip(trace["x"], trace["y"]))
                x_to_text = (
                    dict(zip(trace["x"], trace.get("text", [])))
                    if "text" in trace
                    else {}
                )

                # Create normalized arrays
                new_x = all_x_values
                new_y = [x_to_y.get(x, 0) for x in new_x]  # Use 0 for missing values
                new_text = (
                    [x_to_text.get(x, "") for x in new_x] if "text" in trace else None
                )

                # Update trace
                trace["x"] = new_x
                trace["y"] = new_y
                if new_text is not None:
                    trace["text"] = new_text
            # Handle object format (less common)
            else:
                if not hasattr(trace, "x") or trace.x is None:
                    return trace

                # Create mapping of existing values
                x_to_y = dict(zip(trace.x, trace.y))
                x_to_text = (
                    dict(zip(trace.x, trace.text)) if hasattr(trace, "text") else {}
                )

                # Create normalized arrays
                new_x = all_x_values
                new_y = [x_to_y.get(x, 0) for x in new_x]  # Use 0 for missing values
                new_text = (
                    [x_to_text.get(x, "") for x in new_x]
                    if hasattr(trace, "text")
                    else None
                )

                # Update trace
                trace.x = new_x
                trace.y = new_y
                if new_text is not None:
                    trace.text = new_text

            return trace

        # Normalize all traces
        normalized_baseline = [normalize_trace(trace, all_x) for trace in baseline_data]
        normalized_adjusted = [normalize_trace(trace, all_x) for trace in adjusted_data]

        return normalized_baseline, normalized_adjusted

    def _normalize_scenario_charts(
        self, baseline_charts: Dict[str, Any], adjusted_charts: Dict[str, Any]
    ) -> None:
        """Normalize charts between scenarios to ensure smooth transitions

        UI Heuristic: Cross-Scenario Chart Normalization
        ------------------------------------------------
        This method applies normalization to ensure visual consistency when switching
        between baseline and adjusted scenarios. Without this normalization, users
        experience jarring visual changes that make it difficult to compare values.

        Charts normalized:
        - probability_distribution: Sprint completion probability bars
        - confidence_intervals: Confidence level bars (50%, 70%, 85%, 95%)

        The normalization ensures both scenarios display the same x-axis values,
        with missing data points filled with zero values that animate smoothly.
        """
        # Normalize probability distribution charts
        if (
            "probability_distribution" in baseline_charts
            and "probability_distribution" in adjusted_charts
        ):
            baseline_data = baseline_charts["probability_distribution"]["data"]
            adjusted_data = adjusted_charts["probability_distribution"]["data"]

            logger.info(
                f"Before normalization - Baseline x values: {[trace.get('x', []) for trace in baseline_data]}"
            )
            logger.info(
                f"Before normalization - Adjusted x values: {[trace.get('x', []) for trace in adjusted_data]}"
            )

            # Normalize the bar chart data
            normalized_baseline, normalized_adjusted = self._normalize_bar_chart_data(
                baseline_data, adjusted_data
            )

            logger.info(
                f"After normalization - Baseline x values: {[trace.get('x', []) for trace in normalized_baseline]}"
            )
            logger.info(
                f"After normalization - Adjusted x values: {[trace.get('x', []) for trace in normalized_adjusted]}"
            )

            # Update the charts with normalized data
            baseline_charts["probability_distribution"]["data"] = normalized_baseline
            adjusted_charts["probability_distribution"]["data"] = normalized_adjusted

        # Also normalize confidence intervals chart if present
        if (
            "confidence_intervals" in baseline_charts
            and "confidence_intervals" in adjusted_charts
        ):
            baseline_data = baseline_charts["confidence_intervals"]["data"]
            adjusted_data = adjusted_charts["confidence_intervals"]["data"]

            # These are also bar charts, so normalize them
            normalized_baseline, normalized_adjusted = self._normalize_bar_chart_data(
                baseline_data, adjusted_data
            )

            baseline_charts["confidence_intervals"]["data"] = normalized_baseline
            adjusted_charts["confidence_intervals"]["data"] = normalized_adjusted

    def _normalize_scenario_data(self, combined_data: Dict[str, Any]) -> None:
        """Normalize the probability distribution data in scenario data for frontend use

        The frontend JavaScript rebuilds charts from window.scenarioData, so we need
        to normalize this data as well to ensure consistent x-axis values.
        """
        baseline_prob = combined_data["baseline"].get("probability_distribution", [])
        adjusted_prob = combined_data["adjusted"].get("probability_distribution", [])

        if not baseline_prob or not adjusted_prob:
            return

        # Get all unique sprint numbers from both datasets
        baseline_sprints = {item["sprint"] for item in baseline_prob}
        adjusted_sprints = {item["sprint"] for item in adjusted_prob}
        all_sprints = sorted(baseline_sprints.union(adjusted_sprints))

        if not all_sprints:
            return

        # Create lookup dictionaries
        baseline_map = {item["sprint"]: item["probability"] for item in baseline_prob}
        adjusted_map = {item["sprint"]: item["probability"] for item in adjusted_prob}

        # Rebuild normalized distributions
        normalized_baseline_prob = []
        normalized_adjusted_prob = []

        for sprint in all_sprints:
            # Add to baseline (0 if missing)
            normalized_baseline_prob.append(
                {"sprint": sprint, "probability": baseline_map.get(sprint, 0)}
            )

            # Add to adjusted (0 if missing)
            normalized_adjusted_prob.append(
                {"sprint": sprint, "probability": adjusted_map.get(sprint, 0)}
            )

        # Update the data
        combined_data["baseline"]["probability_distribution"] = normalized_baseline_prob
        combined_data["adjusted"]["probability_distribution"] = normalized_adjusted_prob

        logger.info(
            f"Normalized scenario data - Sprint range: {min(all_sprints)} to {max(all_sprints)}"
        )
        logger.info(f"Baseline now has {len(normalized_baseline_prob)} values")
        logger.info(f"Adjusted now has {len(normalized_adjusted_prob)} values")

    def _create_probability_chart(
        self, results: SimulationResult, config: SimulationConfig
    ) -> Dict[str, Any]:
        """Create probability distribution chart for a scenario"""

        # Extract probability data
        completion_sprints = (
            results.completion_sprints[:1000] if results.completion_sprints else []
        )

        if completion_sprints:
            from collections import Counter

            sprint_counts = Counter(int(s) for s in completion_sprints)
            total = len(completion_sprints)

            # Get all sprint numbers and their probabilities
            sprint_numbers = sorted(sprint_counts.keys())
            probabilities = [sprint_counts[s] / total for s in sprint_numbers]

            # Create the bar chart
            fig = go.Figure()

            # Add the main bar trace
            fig.add_trace(
                go.Bar(
                    x=sprint_numbers,
                    y=probabilities,
                    text=[f"{p:.1%}" for p in probabilities],
                    textposition="outside",
                    name="Probability Distribution",
                    marker=dict(
                        color=probabilities,
                        colorscale=[
                            [0, "rgba(3, 86, 76, 0.3)"],
                            [0.5, "rgba(3, 86, 76, 0.7)"],
                            [1, "#03564c"],
                        ],
                        line=dict(color="rgba(255,255,255,0.8)", width=2),
                    ),
                    hovertemplate="<b>%{x} sprints</b><br>Probability: %{y:.1%}<extra></extra>",
                    textfont=dict(
                        family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                        size=12,
                    ),
                )
            )

            # Add confidence level lines
            percentiles = results.percentiles
            confidence_levels = {0.5: "50%", 0.7: "70%", 0.85: "85%", 0.95: "95%"}

            # Add vertical lines for confidence levels
            for p, label in confidence_levels.items():
                if p in percentiles:
                    fig.add_shape(
                        type="line",
                        x0=percentiles[p],
                        x1=percentiles[p],
                        y0=0,
                        y1=1,
                        yref="paper",
                        line=dict(color="rgba(220, 20, 60, 0.8)", width=3, dash="dash"),
                    )
                    fig.add_annotation(
                        x=percentiles[p],
                        y=1,
                        yref="paper",
                        text=f"<b>{label}</b>",
                        showarrow=False,
                        xanchor="left",
                        yanchor="top",
                        font=dict(size=14, color="#DC143C"),
                    )

            # Update layout
            fig.update_layout(
                title=dict(
                    text="<b>Sprints to Complete - Probability Distribution</b>",
                    font=dict(
                        size=22,
                        family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    ),
                ),
                xaxis=dict(
                    title=dict(text="<b>Sprints to Complete</b>", font=dict(size=14)),
                    tickmode="linear",
                    tick0=min(sprint_numbers),
                    dtick=1,
                    range=[min(sprint_numbers) - 0.5, max(sprint_numbers) + 0.5],
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="rgba(128,128,128,0.1)",
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor="rgba(128,128,128,0.2)",
                ),
                yaxis=dict(
                    title=dict(text="<b>Probability</b>", font=dict(size=14)),
                    tickformat=".1%",
                    range=[0, max(probabilities) * 1.2],
                    showgrid=True,
                    gridwidth=1,
                    gridcolor="rgba(128,128,128,0.1)",
                    zeroline=True,
                    zerolinewidth=2,
                    zerolinecolor="rgba(128,128,128,0.2)",
                ),
                margin=dict(t=100, b=80, l=80, r=60),
                font=dict(
                    family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    size=12,
                ),
                hoverlabel=dict(
                    font=dict(
                        size=14,
                        family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                        color="rgba(0,0,0,0.87)",
                    ),
                    bgcolor="white",
                    bordercolor="rgba(0,0,0,0.2)",
                ),
                showlegend=False,
                height=500,
                bargap=0.2,
                plot_bgcolor="rgba(248,249,250,0.8)",
                paper_bgcolor="white",
            )

            # Convert to dict format expected by frontend
            return {"data": fig.to_dict()["data"], "layout": fig.to_dict()["layout"]}

        return None

    def _create_forecast_timeline(self, results: SimulationResult) -> Dict[str, Any]:
        """Create forecast timeline chart for a scenario"""
        from datetime import datetime, timedelta

        fig = go.Figure()

        # Create timeline
        today = datetime.now()
        percentiles = results.percentiles

        # Timeline base
        timeline_dates = [today + timedelta(weeks=i) for i in range(17)]
        fig.add_trace(
            go.Scatter(
                x=timeline_dates,
                y=[0] * len(timeline_dates),
                mode="lines",
                line=dict(color="rgba(200,200,200,0.5)", width=4, shape="spline"),
                hoverinfo="skip",
                showlegend=False,
            )
        )

        # Add confidence markers
        confidence_markers = [
            (0.5, percentiles.get(0.5, 0), "#DC143C", "50%"),
            (0.7, percentiles.get(0.7, 0), "#FFA500", "70%"),
            (0.85, percentiles.get(0.85, 0), "#FFA500", "85%"),
            (0.95, percentiles.get(0.95, 0), "#00A86B", "95%"),
        ]

        # Group 50% and 70% if they're the same
        if percentiles.get(0.5) == percentiles.get(0.7):
            confidence_markers = [
                (0.5, percentiles.get(0.5, 0), "#FFA500", "50%, 70%"),
                (0.85, percentiles.get(0.85, 0), "#FFA500", "85%"),
                (0.95, percentiles.get(0.95, 0), "#00A86B", "95%"),
            ]

        for conf, sprints, color, label in confidence_markers:
            if sprints > 0:
                date = today + timedelta(weeks=sprints * 2)  # Assuming 2-week sprints
                fig.add_trace(
                    go.Scatter(
                        x=[date],
                        y=[0],
                        mode="markers+text",
                        marker=dict(
                            size=24,
                            color=color,
                            symbol="diamond",
                            line=dict(color="white", width=2),
                        ),
                        text=[f"<b>{label}<br>{int(sprints)} sprints</b>"],
                        textposition="top center",
                        textfont=dict(
                            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                            size=12,
                        ),
                        hovertemplate=f"<b>%{{x|%b %d, %Y}}</b><br>{label}<br>{int(sprints)} sprints<extra></extra>",
                        showlegend=False,
                        name=f"{label} Confidence",
                    )
                )

        # Add today marker
        fig.add_trace(
            go.Scatter(
                x=[today],
                y=[0],
                mode="markers+text",
                marker=dict(
                    size=20,
                    color="#03564c",
                    symbol="star",
                    line=dict(color="white", width=3),
                ),
                text=["<b>Today</b>"],
                textposition="bottom center",
                textfont=dict(color="#03564c", size=14),
                hovertemplate="<b>Today</b><br>%{x|%b %d, %Y}<extra></extra>",
                showlegend=False,
            )
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Forecast Timeline</b>",
                font=dict(
                    size=22,
                    family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                ),
            ),
            xaxis=dict(
                title=dict(text="<b>Date</b>", font=dict(size=14)),
                tickformat="%b %d",
                tickangle=-45,
                range=[today - timedelta(days=7), timeline_dates[-1]],
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(128,128,128,0.1)",
                zeroline=False,
            ),
            yaxis=dict(visible=False, range=[-0.6, 0.6]),
            font=dict(
                family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size=12,
            ),
            hoverlabel=dict(
                font=dict(
                    size=14,
                    family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    color="rgba(0,0,0,0.87)",
                ),
                bgcolor="white",
                bordercolor="rgba(0,0,0,0.2)",
            ),
            margin=dict(t=100, b=80, l=60, r=60),
            height=350,
            hovermode="closest",
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
        )

        return {"data": fig.to_dict()["data"], "layout": fig.to_dict()["layout"]}

    def _create_confidence_chart(self, results: SimulationResult) -> Dict[str, Any]:
        """Create confidence intervals chart for a scenario"""

        percentiles = results.percentiles

        # Create bar chart for confidence levels
        confidence_levels = ["50%", "70%", "85%", "95%"]
        sprints = [
            percentiles.get(0.5, 0),
            percentiles.get(0.7, 0),
            percentiles.get(0.85, 0),
            percentiles.get(0.95, 0),
        ]

        # Set colors based on confidence level
        colors = ["#DC143C", "#FFA500", "#FFA500", "#00A86B"]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=confidence_levels,
                y=sprints,
                text=[f"<b>{int(s)} sprints</b>" for s in sprints],
                textposition="auto",
                textfont=dict(color="white", size=14),
                marker=dict(color=colors, line=dict(color="white", width=2)),
                hovertemplate="<b>%{x} Confidence</b><br>Sprints: %{y:.0f}<extra></extra>",
            )
        )

        # Update layout
        fig.update_layout(
            title=dict(
                text="<b>Sprints to Complete by Confidence Level</b>",
                font=dict(
                    size=22,
                    family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                ),
            ),
            xaxis=dict(
                title=dict(text="<b>Confidence Level</b>", font=dict(size=14)),
                showgrid=False,
            ),
            yaxis=dict(
                title=dict(text="<b>Sprints</b>", font=dict(size=14)),
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
            font=dict(
                family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                size=12,
            ),
            hoverlabel=dict(
                font=dict(
                    size=14,
                    family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    color="rgba(0,0,0,0.87)",
                ),
                bgcolor="white",
                bordercolor="rgba(0,0,0,0.2)",
            ),
            margin=dict(t=100, b=80, l=80, r=60),
            showlegend=False,
            height=450,
            plot_bgcolor="rgba(248,249,250,0.8)",
            paper_bgcolor="white",
            bargap=0.3,
        )

        return {"data": fig.to_dict()["data"], "layout": fig.to_dict()["layout"]}

    def _prepare_chart_data(
        self,
        results: SimulationResult,
        velocity_metrics: VelocityMetrics,
        historical_data: list,
        remaining_work: float,
        config: SimulationConfig,
        label: str,
    ) -> Dict[str, Any]:
        """Prepare chart data for a single scenario"""
        # Extract key metrics
        percentiles = results.percentiles
        completion_sprints = (
            results.completion_sprints[:1000] if results.completion_sprints else []
        )

        # Prepare probability distribution data
        prob_data = []

        # First try to reconstruct from completion_sprints if available
        if completion_sprints:
            from collections import Counter

            sprint_counts = Counter(int(s) for s in completion_sprints)
            total = len(completion_sprints)
            for sprint in sorted(sprint_counts.keys()):
                prob = sprint_counts[sprint] / total
                prob_data.append({"sprint": sprint, "probability": prob})
            logger.info(
                f"Reconstructed probability distribution from {len(completion_sprints)} completion sprints"
            )

        # Fallback to original probability_distribution if no completion sprints
        elif (
            hasattr(results, "probability_distribution")
            and results.probability_distribution
        ):
            # Handle both dict and list formats
            if isinstance(results.probability_distribution, dict):
                for sprint, prob in results.probability_distribution.items():
                    prob_data.append({"sprint": sprint, "probability": prob})
                # Sort by sprint number
                prob_data.sort(key=lambda x: x["sprint"])
            else:
                # If it's a list (legacy histogram format), skip it as it's not useful
                logger.warning(
                    "Skipping legacy histogram format probability_distribution"
                )

        # Prepare confidence intervals
        confidence_data = []
        for level, (lower, upper) in results.confidence_intervals.items():
            confidence_data.append(
                {
                    "level": int(level * 100),
                    "lower": lower,
                    "upper": upper,
                    "value": percentiles.get(level, 0),
                }
            )

        # Log what we're preparing
        logger.info(
            f"Preparing {label} data - prob_data length: {len(prob_data)}, confidence_data length: {len(confidence_data)}"
        )
        if hasattr(results, "probability_distribution"):
            logger.info(
                f"{label} has probability_distribution attribute, type: {type(results.probability_distribution)}"
            )
        else:
            logger.warning(f"{label} missing probability_distribution attribute")

        return {
            "label": label,
            "percentiles": {
                "p50": percentiles.get(0.5, 0),
                "p70": percentiles.get(0.7, 0),
                "p85": percentiles.get(0.85, 0),
                "p95": percentiles.get(0.95, 0),
            },
            "completion_sprints": completion_sprints,
            "probability_distribution": prob_data,
            "confidence_intervals": confidence_data,
            "mean_completion": results.mean_completion_date.isoformat()
            if results.mean_completion_date
            else None,
            "std_dev_days": results.std_dev_days,
        }

    def _create_combined_banner(
        self, scenario: VelocityScenario, comparison: ScenarioComparison
    ) -> str:
        """Create banner for combined report with toggle"""
        scenario_desc = scenario.get_summary()
        impact_desc = comparison.get_impact_summary()

        return f"""
        <div class="scenario-banner combined-banner">
            <div class="scenario-header">
                <h3>📊 Velocity Scenario Analysis</h3>
                <div class="scenario-toggle">
                    <label class="toggle-label">
                        <input type="radio" name="scenario-view" value="baseline" 
                               onclick="switchScenario('baseline')">
                        Baseline
                    </label>
                    <label class="toggle-label">
                        <input type="radio" name="scenario-view" value="adjusted" 
                               onclick="switchScenario('adjusted')" checked>
                        Adjusted
                    </label>
                </div>
            </div>
            <div id="scenario-description" class="scenario-description">
                <p><strong>Scenario:</strong> {scenario_desc}</p>
                <p><strong>Impact:</strong> {impact_desc}</p>
            </div>
            <div id="baseline-notice" class="baseline-notice" style="display: none;">
                <p>This is the baseline forecast without any velocity adjustments.</p>
            </div>
        </div>
        """
