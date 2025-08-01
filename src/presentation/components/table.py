"""Table component for rendering data tables"""

from typing import Dict, Any, List, Optional

from .base import Component
from ..models.view_models import TableRowViewModel


class TableComponent(Component):
    """Component for rendering data tables"""

    def get_template(self) -> str:
        """Get table template"""
        return """
<div class="table-container">
    {% if title %}
    <h3 class="table-title">{{ title }}</h3>
    {% endif %}
    {% if description %}
    <p class="table-description">{{ description }}</p>
    {% endif %}
    <div class="table-wrapper">
        <table class="data-table {{ table_class }}">
            {% if has_header %}
            <thead>
                <tr class="table-header-row">
                    {% for header in headers %}
                    <th class="table-header-cell">{{ header }}</th>
                    {% endfor %}
                </tr>
            </thead>
            {% endif %}
            <tbody>
                {% for row in rows %}
                <tr class="table-row {% if row.row_class %}table-row--{{ row.row_class }}{% endif %}">
                    {% for cell in row.cells %}
                    <td class="table-cell">
                        {% if row.clickable and row.link %}
                        <a href="{{ row.link }}" class="table-link">{{ cell }}</a>
                        {% else %}
                        {{ cell }}
                        {% endif %}
                    </td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
        """

    def get_context(
        self,
        rows: List[TableRowViewModel],
        title: Optional[str] = None,
        description: Optional[str] = None,
        headers: Optional[List[str]] = None,
        table_class: str = "",
        striped: bool = True,
        hover: bool = True,
    ) -> Dict[str, Any]:
        """Get table context

        Args:
            rows: List of table row view models
            title: Optional table title
            description: Optional table description
            headers: Optional header row (can also be first row in rows)
            table_class: Additional CSS classes
            striped: Whether to stripe rows
            hover: Whether to highlight on hover

        Returns:
            Context dictionary
        """
        # Check if first row is header
        has_header = bool(headers)
        if not has_header and rows and rows[0].is_header:
            headers = rows[0].cells
            has_header = True
            rows = rows[1:]  # Remove header from rows

        # Build table classes
        classes = [table_class]
        if striped:
            classes.append("table--striped")
        if hover:
            classes.append("table--hover")

        return {
            "title": title,
            "description": description,
            "rows": rows,
            "headers": headers,
            "has_header": has_header,
            "table_class": " ".join(classes).strip(),
        }

    def get_styles(self) -> str:
        """Get table styles"""
        return """
.table-container {
    background: var(--card-bg, #ffffff);
    border: 1px solid var(--border-color, #e5e5e5);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 2rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
    margin: 0 0 0.5rem 0;
}

.table-description {
    font-size: 0.875rem;
    color: var(--text-secondary, #666666);
    margin: 0 0 1rem 0;
}

.table-wrapper {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.875rem;
}

.table-header-row {
    background: var(--table-header-bg, #f9fafb);
    border-bottom: 2px solid var(--border-color, #e5e5e5);
}

.table-header-cell {
    padding: 0.75rem 1rem;
    text-align: left;
    font-weight: 600;
    color: var(--text-primary, #1a1a1a);
    white-space: nowrap;
}

.table-row {
    border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.table-cell {
    padding: 0.75rem 1rem;
    color: var(--text-primary, #1a1a1a);
}

.table-link {
    color: var(--link-color, #3b82f6);
    text-decoration: none;
    font-weight: 500;
}

.table-link:hover {
    color: var(--link-hover-color, #2563eb);
    text-decoration: underline;
}

/* Striped rows */
.table--striped .table-row:nth-child(even) {
    background: var(--table-stripe-bg, #f9fafb);
}

/* Hover effect */
.table--hover .table-row:hover {
    background: var(--table-hover-bg, #f3f4f6);
}

/* Row variants */
.table-row--optimistic {
    background: var(--optimistic-bg, #d1fae5);
}

.table-row--optimistic:hover {
    background: var(--optimistic-hover-bg, #a7f3d0);
}

.table-row--likely {
    background: var(--likely-bg, #dbeafe);
}

.table-row--likely:hover {
    background: var(--likely-hover-bg, #bfdbfe);
}

.table-row--conservative {
    background: var(--conservative-bg, #fed7aa);
}

.table-row--conservative:hover {
    background: var(--conservative-hover-bg, #fdba74);
}

.table-row--very-conservative {
    background: var(--very-conservative-bg, #fee2e2);
}

.table-row--very-conservative:hover {
    background: var(--very-conservative-hover-bg, #fecaca);
}

.table-row--risk-high {
    background: var(--risk-high-bg, #fee2e2);
    font-weight: 500;
}

.table-row--risk-high:hover {
    background: var(--risk-high-hover-bg, #fecaca);
}

/* Responsive */
@media (max-width: 768px) {
    .table-container {
        padding: 1rem;
    }
    
    .table-header-cell,
    .table-cell {
        padding: 0.5rem 0.75rem;
        font-size: 0.8125rem;
    }
}

/* Scrollbar styling */
.table-wrapper::-webkit-scrollbar {
    height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
    background: var(--scrollbar-track, #f1f1f1);
    border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb {
    background: var(--scrollbar-thumb, #888);
    border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
    background: var(--scrollbar-thumb-hover, #555);
}
        """


class SummaryTableComponent(TableComponent):
    """Specialized table component for forecast summaries"""

    def get_template(self) -> str:
        """Get summary table template with special formatting"""
        return """
<div class="summary-table-container">
    <h3 class="summary-table-title">{{ title }}</h3>
    {% if description %}
    <p class="summary-table-description">{{ description }}</p>
    {% endif %}
    <div class="table-wrapper">
        <table class="summary-table">
            <thead>
                <tr class="summary-header-row">
                    {% for header in headers %}
                    <th class="summary-header-cell">{{ header }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in rows %}
                <tr class="summary-row summary-row--{{ row.row_class }}">
                    {% for cell in row.cells %}
                    <td class="summary-cell">{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
    {% if footnote %}
    <p class="summary-footnote">{{ footnote }}</p>
    {% endif %}
</div>
        """

    def get_context(
        self,
        rows: List[TableRowViewModel],
        title: str = "Forecast Summary",
        description: Optional[str] = None,
        footnote: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get summary table context

        Args:
            rows: Table rows
            title: Table title
            description: Optional description
            footnote: Optional footnote

        Returns:
            Context dictionary
        """
        # Default headers for summary table
        headers = [
            "Confidence Level",
            "Sprints to Complete",
            "Completion Date",
            "Probability",
        ]

        return {
            "title": title,
            "description": description,
            "rows": rows,
            "headers": headers,
            "footnote": footnote,
        }

    def get_styles(self) -> str:
        """Get summary table specific styles"""
        return (
            super().get_styles()
            + """

.summary-table-container {
    background: var(--card-bg, #ffffff);
    border: 2px solid var(--primary-color, #3b82f6);
    border-radius: 8px;
    padding: 2rem;
    margin: 2rem 0;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.summary-table-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text-primary, #1a1a1a);
    margin: 0 0 0.5rem 0;
    text-align: center;
}

.summary-table-description {
    font-size: 1rem;
    color: var(--text-secondary, #666666);
    margin: 0 0 1.5rem 0;
    text-align: center;
}

.summary-table {
    width: 100%;
    border-collapse: collapse;
}

.summary-header-row {
    background: var(--primary-color, #3b82f6);
    color: white;
}

.summary-header-cell {
    padding: 1rem;
    text-align: left;
    font-weight: 600;
}

.summary-row {
    transition: all 0.2s;
}

.summary-cell {
    padding: 1rem;
    font-size: 0.9375rem;
    border-bottom: 1px solid var(--border-color, #e5e5e5);
}

.summary-footnote {
    font-size: 0.875rem;
    color: var(--text-secondary, #666666);
    margin: 1rem 0 0 0;
    font-style: italic;
    text-align: center;
}
        """
        )
