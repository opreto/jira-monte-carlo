"""Footer component for reports"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from .base import Component


class FooterComponent(Component):
    """Footer component for Sprint Radar reports"""

    def get_template(self) -> str:
        """Get footer template"""
        return """
<footer class="footer">
    <div class="footer-content">
        <div class="footer-main">
            <p class="footer-text">{{ footer_text }}</p>
            {% if methodology_description %}
            <p class="footer-methodology">
                <span class="methodology-label">Methodology:</span>
                {{ methodology_description }}
            </p>
            {% endif %}
            {% if simulation_count %}
            <p class="footer-simulations">
                <span class="simulations-label">Simulations:</span>
                {{ simulation_count }} iterations
            </p>
            {% endif %}
        </div>
        {% if has_links %}
        <div class="footer-links">
            {% for link in links %}
            <a href="{{ link.url }}" class="footer-link" {% if link.external %}target="_blank" rel="noopener"{% endif %}>
                {{ link.label }}
            </a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
    {% if has_copyright %}
    <div class="footer-copyright">
        <p>&copy; {{ copyright_year }} {{ copyright_holder }}. All rights reserved.</p>
    </div>
    {% endif %}
</footer>
        """

    def get_context(
        self,
        footer_text: str = "Sprint Radar - Agile Analytics Platform",
        methodology_description: Optional[str] = None,
        simulation_count: Optional[str] = None,
        links: Optional[List[Dict[str, Any]]] = None,
        copyright_holder: str = "Opreto",
        copyright_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get footer context

        Args:
            footer_text: Main footer text
            methodology_description: Optional methodology description
            simulation_count: Optional simulation count
            links: Optional list of footer links
            copyright_holder: Copyright holder name
            copyright_year: Copyright year (defaults to current year)

        Returns:
            Context dictionary
        """
        if copyright_year is None:
            copyright_year = datetime.now().year

        return {
            "footer_text": footer_text,
            "methodology_description": methodology_description,
            "simulation_count": simulation_count,
            "has_links": bool(links),
            "links": links or [],
            "has_copyright": True,
            "copyright_year": copyright_year,
            "copyright_holder": copyright_holder,
        }

    def get_styles(self) -> str:
        """Get footer-specific styles"""
        return """
.footer {
    margin-top: 4rem;
    padding-top: 2rem;
    border-top: 1px solid var(--border-color, #e5e5e5);
    background: var(--footer-bg, #f9fafb);
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 2rem;
    padding: 2rem;
}

.footer-main {
    flex: 1;
}

.footer-text {
    font-size: 1rem;
    color: var(--text-primary, #1a1a1a);
    margin: 0 0 1rem 0;
    font-weight: 500;
}

.footer-methodology,
.footer-simulations {
    font-size: 0.875rem;
    color: var(--text-secondary, #666666);
    margin: 0.5rem 0;
}

.methodology-label,
.simulations-label {
    font-weight: 600;
    margin-right: 0.5rem;
}

.footer-links {
    display: flex;
    gap: 1.5rem;
    align-items: center;
}

.footer-link {
    color: var(--link-color, #3b82f6);
    text-decoration: none;
    font-size: 0.875rem;
    font-weight: 500;
    transition: color 0.2s;
}

.footer-link:hover {
    color: var(--link-hover-color, #2563eb);
    text-decoration: underline;
}

.footer-copyright {
    background: var(--footer-copyright-bg, #f3f4f6);
    padding: 1rem 2rem;
    text-align: center;
    border-top: 1px solid var(--border-color, #e5e5e5);
}

.footer-copyright p {
    margin: 0;
    font-size: 0.875rem;
    color: var(--text-secondary, #666666);
}

@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
    }
    
    .footer-links {
        flex-wrap: wrap;
    }
}
        """
