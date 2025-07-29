"""Chart generation for process health metrics"""

import logging
from typing import Dict, List

import plotly.graph_objects as go

from ..domain.process_health import (
    AgingAnalysis,
    AgingCategory,
    BlockedItemsAnalysis,
    HealthScoreComponent,
    SprintHealthAnalysis,
    WIPAnalysis,
    WIPStatus,
)


logger = logging.getLogger(__name__)


class ProcessHealthChartGenerator:
    """Generate charts for process health metrics"""

    def __init__(self, chart_colors: Dict[str, str]):
        self.chart_colors = chart_colors

    def _get_color_with_alpha(self, color_key: str, alpha: float) -> str:
        """Get color with alpha, handling missing rgba functions"""
        # Map old color names to new ones
        color_mapping = {"success": "high_confidence", "warning": "medium_confidence", "error": "low_confidence"}

        # Try mapped color first
        mapped_key = color_mapping.get(color_key, color_key)
        rgba_key = f"{mapped_key}_rgba"

        if rgba_key in self.chart_colors and callable(self.chart_colors[rgba_key]):
            return self.chart_colors[rgba_key](alpha)
        elif mapped_key in self.chart_colors:
            # Convert hex to rgba manually
            hex_color = self.chart_colors[mapped_key]
            if hex_color.startswith("#"):
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                return f"rgba({r},{g},{b},{alpha})"

        # Try original key
        rgba_key = f"{color_key}_rgba"
        if rgba_key in self.chart_colors and callable(self.chart_colors[rgba_key]):
            return self.chart_colors[rgba_key](alpha)
        elif color_key in self.chart_colors:
            # Convert hex to rgba manually
            hex_color = self.chart_colors[color_key]
            if hex_color.startswith("#"):
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                return f"rgba({r},{g},{b},{alpha})"

        # Fallback colors
        fallbacks = {
            "success": f"rgba(0,168,107,{alpha})",
            "warning": f"rgba(255,165,0,{alpha})",
            "error": f"rgba(220,20,60,{alpha})",
        }
        return fallbacks.get(color_key, f"rgba(128,128,128,{alpha})")

    def create_aging_distribution_chart(self, aging_analysis: AgingAnalysis) -> str:
        """Create bar chart showing aging work items distribution"""
        categories = [
            AgingCategory.FRESH,
            AgingCategory.NORMAL,
            AgingCategory.AGING,
            AgingCategory.STALE,
            AgingCategory.ABANDONED,
        ]

        labels = [cat.value.capitalize() for cat in categories]
        counts = [len(aging_analysis.items_by_category.get(cat, [])) for cat in categories]

        # Calculate story points sum for each category
        points_sums = []
        for cat in categories:
            items = aging_analysis.items_by_category.get(cat, [])
            total_points = sum(item.story_points for item in items if item.story_points is not None)
            points_sums.append(total_points)

        # Color gradient from green to red
        colors = [
            self.chart_colors.get("success", self.chart_colors.get("high_confidence", "#00A86B")),  # Fresh
            self._get_color_with_alpha("success", 0.7),  # Normal
            self.chart_colors.get("warning", self.chart_colors.get("medium_confidence", "#FFA500")),  # Aging
            self._get_color_with_alpha("warning", 0.7),  # Stale
            self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C")),  # Abandoned
        ]

        fig = go.Figure()

        # Create custom data for tooltips
        customdata = [[points] for points in points_sums]

        fig.add_trace(
            go.Bar(
                x=labels,
                y=counts,
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=[str(c) if c > 0 else "" for c in counts],
                textposition="outside",
                customdata=customdata,
                hovertemplate="<b>%{x}</b><br>Items: %{y}<br>Story Points: %{customdata[0]:.0f}<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="<b>Aging Work Items Distribution</b>",
                font=dict(size=22),
            ),
            xaxis_title="<b>Age Category</b>",
            yaxis_title="<b>Number of Items</b>",
            height=400,
            showlegend=False,
            yaxis=dict(
                range=[0, max(counts) * 1.2] if counts else [0, 1],
            ),
            paper_bgcolor="white",
            plot_bgcolor="rgba(248,249,250,0.8)",
        )

        return fig.to_json()

    def create_aging_by_status_chart(self, aging_analysis: AgingAnalysis) -> str:
        """Create horizontal bar chart showing average age by status"""
        statuses = list(aging_analysis.average_age_by_status.keys())
        ages = list(aging_analysis.average_age_by_status.values())

        # Sort by age
        sorted_data = sorted(zip(statuses, ages), key=lambda x: x[1], reverse=True)
        statuses, ages = zip(*sorted_data) if sorted_data else ([], [])

        # Color based on age relative to the data distribution
        colors = []
        if aging_analysis.thresholds:
            # Use dynamic thresholds
            thresholds = aging_analysis.thresholds
            for age in ages:
                if age <= thresholds["fresh"]:
                    colors.append(self.chart_colors.get("success", self.chart_colors.get("high_confidence", "#00A86B")))
                elif age <= thresholds["normal"]:
                    colors.append(self._get_color_with_alpha("success", 0.7))
                elif age <= thresholds["aging"]:
                    colors.append(
                        self.chart_colors.get("warning", self.chart_colors.get("medium_confidence", "#FFA500"))
                    )
                elif age <= thresholds["stale"]:
                    colors.append(self._get_color_with_alpha("warning", 0.7))
                else:
                    colors.append(self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C")))
        else:
            # Fallback to fixed thresholds
            for age in ages:
                if age <= 7:
                    colors.append(self.chart_colors.get("success", self.chart_colors.get("high_confidence", "#00A86B")))
                elif age <= 14:
                    colors.append(self._get_color_with_alpha("success", 0.7))
                elif age <= 30:
                    colors.append(
                        self.chart_colors.get("warning", self.chart_colors.get("medium_confidence", "#FFA500"))
                    )
                else:
                    colors.append(self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C")))

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=statuses,
                x=ages,
                orientation="h",
                marker=dict(color=colors, line=dict(color="white", width=1)),
                text=[f"{age:.0f} days" for age in ages],
                textposition="outside",
                hovertemplate="<b>%{y}</b><br>Average Age: %{x:.1f} days<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="<b>Average Age by Status</b>",
                font=dict(size=22),
            ),
            xaxis_title="<b>Average Age (days)</b>",
            yaxis_title="",
            height=400 + (len(statuses) * 30),  # Dynamic height
            showlegend=False,
            xaxis=dict(
                range=[0, max(ages) * 1.2] if ages else [0, 1],
            ),
            paper_bgcolor="white",
            plot_bgcolor="rgba(248,249,250,0.8)",
            margin=dict(l=150),  # More space for status names
        )

        return fig.to_json()

    def create_wip_by_status_chart(self, wip_analysis: WIPAnalysis) -> str:
        """Create bar chart showing WIP by status with limits"""
        statuses = [WIPStatus.TODO, WIPStatus.IN_PROGRESS, WIPStatus.REVIEW, WIPStatus.BLOCKED]

        counts = [len(wip_analysis.items_by_status.get(status, [])) for status in statuses]
        labels = [status.value.replace("_", " ").title() for status in statuses]

        # Calculate story points sum for each status
        points_sums = []
        for status in statuses:
            items = wip_analysis.items_by_status.get(status, [])
            total_points = sum(item.story_points for item in items if item.story_points is not None)
            points_sums.append(total_points)

        fig = go.Figure()

        # Create custom data for tooltips
        customdata = [[points] for points in points_sums]

        # Add bars for current WIP
        fig.add_trace(
            go.Bar(
                name="Current WIP",
                x=labels,
                y=counts,
                marker_color=self.chart_colors["data1"],
                text=[str(c) for c in counts],
                textposition="outside",
                customdata=customdata,
                hovertemplate="<b>%{x}</b><br>Items: %{y}<br>Story Points: %{customdata[0]:.0f}<extra></extra>",
            )
        )

        # Add WIP limits if available
        if wip_analysis.wip_limits:
            limit_values = []
            for status in statuses:
                limit = wip_analysis.wip_limits.get(status, None)
                limit_values.append(limit if limit is not None else 0)

            # Add limit lines
            for i, (label, limit) in enumerate(zip(labels, limit_values)):
                if limit > 0:
                    fig.add_shape(
                        type="line",
                        x0=i - 0.4,
                        x1=i + 0.4,
                        y0=limit,
                        y1=limit,
                        line=dict(
                            color=self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C")),
                            width=3,
                            dash="dash",
                        ),
                    )

                    # Add limit label
                    fig.add_annotation(
                        x=i,
                        y=limit,
                        text=f"Limit: {limit}",
                        showarrow=False,
                        yshift=10,
                        font=dict(
                            color=self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C")),
                            size=12,
                        ),
                    )

        fig.update_layout(
            title=dict(
                text="<b>Work In Progress by Status</b>",
                font=dict(size=22),
            ),
            xaxis_title="<b>Status</b>",
            yaxis_title="<b>Number of Items</b>",
            height=450,
            showlegend=False,
            yaxis=dict(
                range=[0, max(counts + list(wip_analysis.wip_limits.values())) * 1.3] if counts else [0, 1],
            ),
            paper_bgcolor="white",
            plot_bgcolor="rgba(248,249,250,0.8)",
        )

        return fig.to_json()

    def create_sprint_health_trend_chart(self, sprint_health: SprintHealthAnalysis) -> str:
        """Create line chart showing sprint completion rate trend"""
        sprint_names = [sm.sprint_name for sm in sprint_health.sprint_metrics]
        completion_rates = [sm.completion_rate * 100 for sm in sprint_health.sprint_metrics]

        fig = go.Figure()

        # Add completion rate line
        fig.add_trace(
            go.Scatter(
                x=sprint_names,
                y=completion_rates,
                mode="lines+markers",
                name="Completion Rate",
                line=dict(
                    color=self.chart_colors["data1"],
                    width=3,
                ),
                marker=dict(
                    size=8,
                    color=self.chart_colors["data1"],
                ),
                hovertemplate="<b>%{x}</b><br>Completion: %{y:.1f}%<extra></extra>",
            )
        )

        # Add average line
        avg_rate = sprint_health.average_completion_rate * 100
        fig.add_hline(
            y=avg_rate,
            line_dash="dash",
            line_color=self.chart_colors["neutral"],
            annotation_text=f"Average: {avg_rate:.1f}%",
            annotation_position="right",
        )

        # Add ideal line at 100%
        fig.add_hline(
            y=100,
            line_dash="dot",
            line_color=self._get_color_with_alpha("success", 0.5),
            annotation_text="Target: 100%",
            annotation_position="left",
        )

        fig.update_layout(
            title=dict(
                text="<b>Sprint Completion Rate Trend</b>",
                font=dict(size=22),
            ),
            xaxis_title="<b>Sprint</b>",
            yaxis_title="<b>Completion Rate (%)</b>",
            height=450,
            showlegend=False,
            yaxis=dict(
                range=[0, 120],
                tickformat=".0f",
            ),
            xaxis=dict(
                tickangle=-45,
            ),
            paper_bgcolor="white",
            plot_bgcolor="rgba(248,249,250,0.8)",
        )

        return fig.to_json()

    def create_sprint_scope_change_chart(self, sprint_health: SprintHealthAnalysis) -> str:
        """Create bar chart showing scope changes per sprint"""
        sprint_names = [sm.sprint_name for sm in sprint_health.sprint_metrics]
        added_points = [sm.added_points for sm in sprint_health.sprint_metrics]
        removed_points = [-sm.removed_points for sm in sprint_health.sprint_metrics]  # Negative for visualization

        fig = go.Figure()

        # Added scope
        fig.add_trace(
            go.Bar(
                name="Scope Added",
                x=sprint_names,
                y=added_points,
                marker_color=self.chart_colors["warning"],
                hovertemplate="<b>%{x}</b><br>Added: %{y:.0f} points<extra></extra>",
            )
        )

        # Removed scope
        fig.add_trace(
            go.Bar(
                name="Scope Removed",
                x=sprint_names,
                y=removed_points,
                marker_color=self.chart_colors.get("info", "#17a2b8"),
                hovertemplate="<b>%{x}</b><br>Removed: %{y:.0f} points<extra></extra>",
            )
        )

        fig.update_layout(
            title=dict(
                text="<b>Sprint Scope Changes</b>",
                font=dict(size=22),
            ),
            xaxis_title="<b>Sprint</b>",
            yaxis_title="<b>Story Points</b>",
            height=450,
            barmode="relative",
            xaxis=dict(
                tickangle=-45,
            ),
            paper_bgcolor="white",
            plot_bgcolor="rgba(248,249,250,0.8)",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )

        return fig.to_json()

    def create_blocked_items_severity_chart(self, blocked_analysis: BlockedItemsAnalysis) -> str:
        """Create pie chart showing blocked items by severity"""
        severity_groups = blocked_analysis.items_by_severity

        labels = ["Low (≤2 days)", "Medium (3-5 days)", "High (>5 days)"]
        values = [
            len(severity_groups.get("low", [])),
            len(severity_groups.get("medium", [])),
            len(severity_groups.get("high", [])),
        ]

        colors = [
            self._get_color_with_alpha("success", 0.7),
            self.chart_colors["warning"],
            self.chart_colors["error"],
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=colors,
                    line=dict(color="white", width=2),
                ),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Items: %{value}<br>%{percent}<extra></extra>",
            )
        )

        # Add center annotation
        total_blocked = sum(values)
        fig.add_annotation(
            text=f"<b>{total_blocked}</b><br>Blocked Items",
            x=0.5,
            y=0.5,
            font=dict(size=16),
            showarrow=False,
        )

        fig.update_layout(
            title=dict(
                text="<b>Blocked Items by Severity</b>",
                font=dict(size=22),
            ),
            height=450,
            showlegend=True,
            paper_bgcolor="white",
            margin=dict(t=100, b=50, l=50, r=150),
        )

        return fig.to_json()

    def create_process_health_score_gauge(self, health_score: float) -> str:
        """Create gauge chart for overall process health score"""
        # Determine color based on score
        if health_score >= 0.8:
            color = self.chart_colors.get("success", self.chart_colors.get("high_confidence", "#00A86B"))
            status = "Healthy"
        elif health_score >= 0.6:
            color = self.chart_colors.get("warning", self.chart_colors.get("medium_confidence", "#FFA500"))
            status = "Fair"
        else:
            color = self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C"))
            status = "Needs Attention"

        fig = go.Figure()

        fig.add_trace(
            go.Indicator(
                mode="gauge+number+delta",
                value=health_score * 100,
                title={"text": f"<b>Process Health Score</b><br><span style='font-size:0.8em'>{status}</span>"},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickwidth": 1},
                    "bar": {"color": color},
                    "bgcolor": "white",
                    "borderwidth": 2,
                    "bordercolor": "gray",
                    "steps": [
                        {"range": [0, 60], "color": self._get_color_with_alpha("error", 0.1)},
                        {"range": [60, 80], "color": self._get_color_with_alpha("warning", 0.1)},
                        {"range": [80, 100], "color": self._get_color_with_alpha("success", 0.1)},
                    ],
                    "threshold": {
                        "line": {"color": "black", "width": 4},
                        "thickness": 0.75,
                        "value": 80,
                    },
                },
                number={"suffix": "%", "font": {"size": 40}},
            )
        )

        fig.update_layout(
            height=350,
            paper_bgcolor="white",
            font={"color": "black", "family": "Arial"},
        )

        return fig.to_json()

    def create_health_score_breakdown_chart(self, components: List["HealthScoreComponent"]) -> str:
        """Create horizontal bar chart showing health score component breakdown"""
        if not components:
            # Return valid empty chart JSON
            return '{"data": [], "layout": {}}'

        names = [c.name for c in components]
        scores = [c.score * 100 for c in components]

        # Color based on score
        colors = []
        for score in scores:
            if score >= 80:
                colors.append(self.chart_colors.get("success", self.chart_colors.get("high_confidence", "#00A86B")))
            elif score >= 60:
                colors.append(self.chart_colors.get("warning", self.chart_colors.get("medium_confidence", "#FFA500")))
            else:
                colors.append(self.chart_colors.get("error", self.chart_colors.get("low_confidence", "#DC143C")))

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=names,
                x=scores,
                orientation="h",
                marker=dict(color=colors, line=dict(color="white", width=2)),
                text=[f"{s:.0f}%" for s in scores],
                textposition="inside",
                textfont=dict(color="white", size=14, weight="bold"),
                hovertemplate="<b>%{y}</b><br>Score: %{x:.0f}%<extra></extra>",
            )
        )

        # Add average line
        avg_score = sum(scores) / len(scores)
        fig.add_vline(
            x=avg_score,
            line_dash="dash",
            line_color=self.chart_colors["neutral"],
            annotation_text=f"Overall: {avg_score:.0f}%",
            annotation_position="top",
        )

        fig.update_layout(
            title=dict(
                text="<b>Health Score Components</b>",
                font=dict(size=20),
            ),
            showlegend=False,
            xaxis=dict(
                range=[0, 100],
                title="Score (%)",
                showgrid=True,
                gridcolor="rgba(128,128,128,0.1)",
            ),
            yaxis=dict(
                title="",
            ),
            height=300,
            margin=dict(l=150, r=50, t=60, b=50),
            paper_bgcolor="white",
            plot_bgcolor="rgba(248,249,250,0.8)",
        )

        return fig.to_json()
