"""Chart component for rendering Plotly charts"""

import json
from typing import Dict, Any, Optional, List

from .base import Component
from ..models.view_models import ChartViewModel


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
        var config = {
            responsive: {{ responsive|lower }},
            displayModeBar: {{ show_toolbar|lower }},
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
        };
        
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

        Returns:
            Context dictionary
        """
        # Ensure data is in array format for Plotly
        if data and not isinstance(data, list):
            data = [data]

        return {
            "chart_id": chart_id,
            "title": title,
            "description": description,
            "data_json": json.dumps(data or {}),
            "layout_json": json.dumps(layout or {}),
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
.chart-container {
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--border-color, #e5e5e5);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.chart-header {
    margin-bottom: 1rem;
}

.chart-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
    margin: 0 0 0.5rem 0;
}

.chart-description {
    font-size: 0.875rem;
    color: var(--text-secondary, #666666);
    margin: 0;
}

.chart-content {
    margin-bottom: 1rem;
}

.plotly-chart {
    width: 100%;
    min-height: 400px;
}

.chart-insights {
    border-top: 1px solid var(--border-color, #e5e5e5);
    padding-top: 1rem;
}

.insights-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
    margin: 0 0 0.5rem 0;
}

.insights-list {
    margin: 0;
    padding-left: 1.5rem;
}

.insights-list li {
    font-size: 0.875rem;
    color: var(--text-secondary, #666666);
    margin-bottom: 0.25rem;
}

.insights-list li:last-child {
    margin-bottom: 0;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    .chart-container {
        padding: 1rem;
    }
    
    .plotly-chart {
        min-height: 300px;
    }
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
<div class="chart-grid chart-grid--cols-{{ columns }}">
    {% for chart_html in charts %}
    <div class="chart-grid__item">
        {{ chart_html|safe }}
    </div>
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
        grid_styles = """
.chart-grid {
    display: grid;
    gap: 2rem;
    margin-bottom: 2rem;
}

.chart-grid--cols-1 {
    grid-template-columns: 1fr;
}

.chart-grid--cols-2 {
    grid-template-columns: repeat(2, 1fr);
}

.chart-grid--cols-3 {
    grid-template-columns: repeat(3, 1fr);
}

.chart-grid__item {
    min-width: 0; /* Prevent grid blowout */
}

@media (max-width: 1024px) {
    .chart-grid--cols-3 {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .chart-grid--cols-2,
    .chart-grid--cols-3 {
        grid-template-columns: 1fr;
    }
}
        """
        # Include chart styles
        if self.charts:
            return grid_styles + "\n" + self.charts[0].get_styles()
        return grid_styles
