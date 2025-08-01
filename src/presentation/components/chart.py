"""Chart component for rendering Plotly charts"""

import json
from typing import Dict, Any, Optional, List

from .base import Component
from ..models.view_models import ChartViewModel
from ..utils.responsive_charts import ResponsiveChartConfig


class ChartComponent(Component):
    """Component for rendering Plotly charts"""

    def get_template(self) -> str:
        """Get chart template"""
        return """
<div class="chart-container" id="chart-{{ chart_id }}">
    <div class="chart-header">
        <h3 class="chart-title">{{ title }}</h3>
        {% if description %}
        <p class="chart-description">{{ description }}</p>
        {% endif %}
    </div>
    <div class="chart-content">
        <div id="{{ chart_id }}" class="plotly-chart"></div>
    </div>
    {% if insights %}
    <div class="chart-insights">
        <h4 class="insights-title">Key Insights</h4>
        <ul class="insights-list">
            {% for insight in insights %}
            <li>{{ insight }}</li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</div>
<script>
    (function() {
        var data = {{ data_json|safe }};
        var layout = {{ layout_json|safe }};
        var config = {{ config_json|safe }};
        
        // Apply responsive layout adjustments
        const viewportWidth = window.innerWidth;
        if (viewportWidth < 768) {
            layout.margin = { t: 30, l: 40, r: 10, b: 40 };
            layout.font = layout.font || {};
            layout.font.size = 12;
            if (layout.showlegend !== false) {
                layout.showlegend = false;
            }
            if (layout.xaxis && layout.xaxis.title) {
                layout.xaxis.tickangle = -45;
            }
        } else if (viewportWidth >= 1920) {
            layout.margin = { t: 50, l: 80, r: 30, b: 80 };
            layout.font = layout.font || {};
            layout.font.size = 16;
        }
        
        Plotly.newPlot('{{ chart_id }}', data, layout, config);
    })();
</script>
        """

    def get_context(
        self,
        chart_id: str,
        title: str,
        description: Optional[str] = None,
        data: Dict[str, Any] = None,
        layout: Dict[str, Any] = None,
        insights: Optional[List[str]] = None,
        responsive: bool = True,
        show_toolbar: bool = True,
        chart_type: str = "bar",
    ) -> Dict[str, Any]:
        """Get chart context

        Args:
            chart_id: Unique chart identifier
            title: Chart title
            description: Optional chart description
            data: Plotly data configuration
            layout: Plotly layout configuration
            insights: Optional list of insights
            responsive: Whether chart should be responsive
            show_toolbar: Whether to show Plotly toolbar
            chart_type: Type of chart for responsive height calculation

        Returns:
            Context dictionary
        """
        # Ensure data is in array format for Plotly
        if data and not isinstance(data, list):
            data = [data]

        # Get responsive config
        config = ResponsiveChartConfig.get_responsive_config()
        if show_toolbar:
            config["displayModeBar"] = True
        else:
            config["displayModeBar"] = False

        return {
            "chart_id": chart_id,
            "title": title,
            "description": description,
            "data_json": json.dumps(data or {}),
            "layout_json": json.dumps(layout or {}),
            "config_json": json.dumps(config),
            "insights": insights,
            "responsive": responsive,
            "show_toolbar": show_toolbar,
        }

    @classmethod
    def from_view_model(cls, view_model: ChartViewModel) -> "ChartComponent":
        """Create component from view model

        Args:
            view_model: Chart view model

        Returns:
            Chart component
        """
        component = cls()
        # Create a pre-rendered context that will be used by render()
        data = view_model.data
        if not isinstance(data, list):
            data = [data]

        component._rendered_context = {
            "chart_id": view_model.chart_id,
            "title": view_model.title,
            "description": view_model.description,
            "data_json": json.dumps(data),
            "layout_json": json.dumps(view_model.layout or {}),
            "insights": view_model.insights,
            "responsive": view_model.responsive,
            "show_toolbar": view_model.interactive,
        }
        return component

    def render(self, **kwargs) -> str:
        """Render the component, using pre-rendered context if available"""
        if hasattr(self, "_rendered_context"):
            # Use pre-rendered context from from_view_model
            template_str = self.get_template()
            template = self._environment.from_string(template_str)
            return template.render(**self._rendered_context)

        # Otherwise use normal rendering
        return super().render(**kwargs)

    def get_styles(self) -> str:
        """Get chart styles"""
        return """
/* Chart insights section */
.chart-insights {
    border-top: 1px solid var(--border-color, #e5e5e5);
    padding-block-start: var(--space-s);
    margin-block-start: var(--space-m);
}

.insights-title {
    font-size: var(--step-1);
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
    margin-block-end: var(--space-xs);
}

.insights-list {
    margin: 0;
    padding-inline-start: var(--space-m);
}

.insights-list li {
    font-size: var(--step--1);
    color: var(--text-secondary, #666666);
    margin-block-end: var(--space-2xs);
}

.insights-list li:last-child {
    margin-block-end: 0;
}
        """


class ChartGridComponent(Component):
    """Component for rendering a grid of charts"""

    def __init__(self, charts: List[ChartComponent], columns: int = 2):
        """Initialize with charts

        Args:
            charts: List of chart components
            columns: Number of columns in grid
        """
        super().__init__()
        self.charts = charts
        self.columns = columns

    def get_template(self) -> str:
        """Get chart grid template"""
        return """
<div class="chart-grid">
    {% for chart_html in charts %}
    {{ chart_html|safe }}
    {% endfor %}
</div>
        """

    def get_context(self, **kwargs) -> Dict[str, Any]:
        """Get grid context with rendered charts"""
        return {
            "charts": [chart.render() for chart in self.charts],
            "columns": self.columns,
        }

    def get_styles(self) -> str:
        """Get grid styles plus chart styles"""
        # Chart grid styles are now in responsive.css
        # Just return chart styles if available
        if self.charts:
            return self.charts[0].get_styles()
        return ""
