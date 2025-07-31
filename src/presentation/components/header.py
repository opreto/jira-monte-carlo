"""Header component for reports"""

from typing import Dict, Any, Optional
from datetime import datetime

from .base import Component


class HeaderComponent(Component):
    """Header component for Sprint Radar reports"""
    
    def get_template(self) -> str:
        """Get header template"""
        return """
<header class="header">
    <div class="header-content">
        <div class="header-main">
            <h1 class="header-title">{{ title }}</h1>
            {% if subtitle %}
            <h2 class="header-subtitle">{{ subtitle }}</h2>
            {% endif %}
        </div>
        <div class="header-meta">
            {% if project_name %}
            <div class="header-project">
                <span class="meta-label">Project:</span>
                <span class="meta-value">{{ project_name }}</span>
            </div>
            {% endif %}
            <div class="header-date">
                <span class="meta-label">Generated:</span>
                <span class="meta-value">{{ generated_date }}</span>
            </div>
            {% if theme_name %}
            <div class="header-theme">
                <span class="meta-label">Theme:</span>
                <span class="meta-value">{{ theme_name }}</span>
            </div>
            {% endif %}
        </div>
    </div>
    {% if has_navigation %}
    <nav class="header-nav">
        {% for item in navigation_items %}
        <a href="#{{ item.id }}" class="nav-link">{{ item.label }}</a>
        {% endfor %}
    </nav>
    {% endif %}
</header>
        """
    
    def get_context(
        self,
        title: str,
        subtitle: Optional[str] = None,
        project_name: Optional[str] = None,
        theme_name: str = "opreto",
        generated_date: Optional[str] = None,
        navigation_items: Optional[list] = None
    ) -> Dict[str, Any]:
        """Get header context
        
        Args:
            title: Main title
            subtitle: Optional subtitle
            project_name: Optional project name
            theme_name: Theme name
            generated_date: Generation date (defaults to now)
            navigation_items: Optional navigation items
            
        Returns:
            Context dictionary
        """
        if not generated_date:
            generated_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return {
            'title': title,
            'subtitle': subtitle,
            'project_name': project_name,
            'theme_name': theme_name,
            'generated_date': generated_date,
            'has_navigation': bool(navigation_items),
            'navigation_items': navigation_items or []
        }
    
    def get_styles(self) -> str:
        """Get header-specific styles"""
        return """
.header {
    background: var(--header-bg, #ffffff);
    border-bottom: 1px solid var(--border-color, #e5e5e5);
    padding: 2rem 0;
    margin-bottom: 2rem;
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 2rem;
}

.header-main {
    flex: 1;
}

.header-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--text-primary, #1a1a1a);
    margin: 0 0 0.5rem 0;
}

.header-subtitle {
    font-size: 1.25rem;
    font-weight: 400;
    color: var(--text-secondary, #666666);
    margin: 0;
}

.header-meta {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    min-width: 200px;
}

.header-meta > div {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
}

.meta-label {
    font-weight: 600;
    color: var(--text-secondary, #666666);
}

.meta-value {
    color: var(--text-primary, #1a1a1a);
}

.header-nav {
    display: flex;
    gap: 1.5rem;
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid var(--border-color, #e5e5e5);
}

.nav-link {
    color: var(--link-color, #3b82f6);
    text-decoration: none;
    font-weight: 500;
    transition: color 0.2s;
}

.nav-link:hover {
    color: var(--link-hover-color, #2563eb);
    text-decoration: underline;
}

@media (max-width: 768px) {
    .header-content {
        flex-direction: column;
    }
    
    .header-meta {
        width: 100%;
    }
    
    .header-nav {
        flex-wrap: wrap;
    }
}
        """