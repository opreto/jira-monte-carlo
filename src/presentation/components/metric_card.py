"""Metric card component for displaying key metrics"""

from typing import Dict, Any, Optional, List

from .base import Component
from ..models.view_models import MetricCardViewModel


class MetricCardComponent(Component):
    """Component for rendering metric cards"""

    def get_template(self) -> str:
        """Get metric card template"""
        return """
<div class="metric-card metric-card--{{ color }}">
    {% if icon %}
    <div class="metric-card__icon">{{ icon }}</div>
    {% endif %}
    <div class="metric-card__content">
        <div class="metric-card__label">{{ label }}</div>
        <div class="metric-card__value">
            {{ value }}
            {% if unit %}<span class="metric-card__unit">{{ unit }}</span>{% endif %}
        </div>
        {% if trend %}
        <div class="metric-card__trend metric-card__trend--{{ trend }}">
            {% if trend == 'up' %}↑{% elif trend == 'down' %}↓{% else %}→{% endif %}
            {% if trend_value %}<span class="trend-value">{{ trend_value }}</span>{% endif %}
        </div>
        {% endif %}
    </div>
</div>
        """

    def get_context(
        self,
        label: str,
        value: str,
        unit: Optional[str] = None,
        trend: Optional[str] = None,
        trend_value: Optional[str] = None,
        color: str = "primary",
        icon: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get metric card context

        Args:
            label: Metric label
            value: Metric value
            unit: Optional unit
            trend: Optional trend ('up', 'down', 'stable')
            trend_value: Optional trend value
            color: Card color theme
            icon: Optional icon

        Returns:
            Context dictionary
        """
        return {
            "label": label,
            "value": value,
            "unit": unit,
            "trend": trend,
            "trend_value": trend_value,
            "color": color,
            "icon": icon,
        }

    @classmethod
    def from_view_model(cls, view_model: MetricCardViewModel) -> "MetricCardComponent":
        """Create component from view model

        Args:
            view_model: Metric card view model

        Returns:
            Metric card component
        """
        component = cls()
        component._rendered_context = {
            "label": view_model.label,
            "value": view_model.value,
            "unit": view_model.unit,
            "trend": view_model.trend,
            "trend_value": view_model.trend_value,
            "color": view_model.color,
            "icon": view_model.icon,
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
        """Get metric card styles"""
        return """
.metric-card {
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--border-color, #e5e5e5);
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metric-card__icon {
    font-size: 2rem;
    margin-bottom: 1rem;
    opacity: 0.8;
}

.metric-card__content {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.metric-card__label {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--text-secondary, #666666);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.metric-card__value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-primary, #1a1a1a);
    line-height: 1.2;
}

.metric-card__unit {
    font-size: 1rem;
    font-weight: 400;
    color: var(--text-secondary, #666666);
    margin-left: 0.25rem;
}

.metric-card__trend {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
}

.metric-card__trend--up {
    color: var(--success-color, #10b981);
}

.metric-card__trend--down {
    color: var(--error-color, #ef4444);
}

.metric-card__trend--stable {
    color: var(--text-secondary, #666666);
}

.trend-value {
    font-weight: 500;
}

/* Color variants */
.metric-card--primary {
    border-color: var(--primary-color, #3b82f6);
}

.metric-card--primary .metric-card__icon,
.metric-card--primary .metric-card__value {
    color: var(--primary-color, #3b82f6);
}

.metric-card--success {
    border-color: var(--success-color, #10b981);
}

.metric-card--success .metric-card__icon,
.metric-card--success .metric-card__value {
    color: var(--success-color, #10b981);
}

.metric-card--warning {
    border-color: var(--warning-color, #f59e0b);
}

.metric-card--warning .metric-card__icon,
.metric-card--warning .metric-card__value {
    color: var(--warning-color, #f59e0b);
}

.metric-card--error {
    border-color: var(--error-color, #ef4444);
}

.metric-card--error .metric-card__icon,
.metric-card--error .metric-card__value {
    color: var(--error-color, #ef4444);
}

.metric-card--info {
    border-color: var(--info-color, #6366f1);
}

.metric-card--info .metric-card__icon,
.metric-card--info .metric-card__value {
    color: var(--info-color, #6366f1);
}
        """


class MetricCardGridComponent(Component):
    """Component for rendering a grid of metric cards"""

    def __init__(self, cards: List[MetricCardComponent]):
        """Initialize with metric cards

        Args:
            cards: List of metric card components
        """
        super().__init__()
        self.cards = cards

    def get_template(self) -> str:
        """Get metric card grid template"""
        return """
<div class="metric-card-grid">
    {% for card_html in cards %}
    {{ card_html|safe }}
    {% endfor %}
</div>
        """

    def get_context(self, **kwargs) -> Dict[str, Any]:
        """Get grid context with rendered cards"""
        return {"cards": [card.render() for card in self.cards]}

    def get_styles(self) -> str:
        """Get grid styles plus card styles"""
        grid_styles = """
.metric-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

@media (max-width: 768px) {
    .metric-card-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
}
        """
        # Include card styles
        if self.cards:
            return grid_styles + "\n" + self.cards[0].get_styles()
        return grid_styles
