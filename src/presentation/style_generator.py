"""Style generator for HTML reports"""
from typing import Optional
from ..domain.styles import Theme


class StyleGenerator:
    """Generate CSS styles from theme"""
    
    def __init__(self, theme: Theme):
        self.theme = theme
    
    def generate_css(self) -> str:
        """Generate complete CSS from theme"""
        css_parts = [
            self._generate_root_variables(),
            self._generate_base_styles(),
            self._generate_typography_styles(),
            self._generate_component_styles(),
            self._generate_utility_styles(),
            self._generate_chart_styles()
        ]
        
        # Add custom CSS if provided
        if self.theme.custom_css:
            css_parts.append(self.theme.custom_css)
        
        return "\n\n".join(css_parts)
    
    def _generate_root_variables(self) -> str:
        """Generate CSS custom properties"""
        return f"""
:root {{
    /* Colors */
    --color-primary: {self.theme.colors.primary.hex};
    --color-primary-dark: {self.theme.colors.primary_dark.hex};
    --color-secondary: {self.theme.colors.secondary.hex};
    --color-accent: {self.theme.colors.accent.hex};
    --color-background: {self.theme.colors.background.hex};
    --color-surface: {self.theme.colors.surface.hex};
    --color-text-primary: {self.theme.colors.text_primary.hex};
    --color-text-secondary: {self.theme.colors.text_secondary.hex};
    --color-success: {self.theme.colors.success.hex};
    --color-warning: {self.theme.colors.warning.hex};
    --color-error: {self.theme.colors.error.hex};
    --color-info: {self.theme.colors.info.hex};
    
    /* RGB values for opacity */
    --color-primary-rgb: {self.theme.colors.primary.rgb or '102, 126, 234'};
    --color-secondary-rgb: {self.theme.colors.secondary.rgb or '78, 205, 196'};
    --color-accent-rgb: {self.theme.colors.accent.rgb or '255, 107, 107'};
    
    /* Spacing */
    --spacing-xs: {self.theme.spacing.xs};
    --spacing-sm: {self.theme.spacing.sm};
    --spacing-md: {self.theme.spacing.md};
    --spacing-lg: {self.theme.spacing.lg};
    --spacing-xl: {self.theme.spacing.xl};
    --spacing-xxl: {self.theme.spacing.xxl};
    
    /* Shadows */
    --shadow-sm: {self.theme.shadows.sm};
    --shadow-md: {self.theme.shadows.md};
    --shadow-lg: {self.theme.shadows.lg};
    --shadow-xl: {self.theme.shadows.xl};
    
    /* Borders */
    --border-radius-sm: {self.theme.borders.radius_sm};
    --border-radius-md: {self.theme.borders.radius_md};
    --border-radius-lg: {self.theme.borders.radius_lg};
    --border-radius-full: {self.theme.borders.radius_full};
    --border-width: {self.theme.borders.width};
    --border-color: {self.theme.borders.color};
}}"""
    
    def _generate_base_styles(self) -> str:
        """Generate base HTML styles"""
        return f"""
body {{
    font-family: {self.theme.typography.body.font_family};
    font-size: {self.theme.typography.body.font_size};
    line-height: {self.theme.typography.body.line_height};
    color: var(--color-text-primary);
    background-color: var(--color-background);
    margin: 0;
    padding: 0;
}}

.container {{
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-lg);
}}"""
    
    def _generate_typography_styles(self) -> str:
        """Generate typography styles"""
        return f"""
h1 {{
    font-family: {self.theme.typography.heading1.font_family};
    font-size: {self.theme.typography.heading1.font_size};
    font-weight: {self.theme.typography.heading1.font_weight};
    line-height: {self.theme.typography.heading1.line_height};
    letter-spacing: {self.theme.typography.heading1.letter_spacing or 'normal'};
    margin: 0 0 var(--spacing-md) 0;
    color: var(--color-text-primary);
}}

h2 {{
    font-family: {self.theme.typography.heading2.font_family};
    font-size: {self.theme.typography.heading2.font_size};
    font-weight: {self.theme.typography.heading2.font_weight};
    line-height: {self.theme.typography.heading2.line_height};
    letter-spacing: {self.theme.typography.heading2.letter_spacing or 'normal'};
    margin: 0 0 var(--spacing-md) 0;
    color: var(--color-text-primary);
}}

h3 {{
    font-family: {self.theme.typography.heading3.font_family};
    font-size: {self.theme.typography.heading3.font_size};
    font-weight: {self.theme.typography.heading3.font_weight};
    line-height: {self.theme.typography.heading3.line_height};
    margin: 0 0 var(--spacing-sm) 0;
    color: var(--color-text-primary);
}}

.caption {{
    font-family: {self.theme.typography.caption.font_family};
    font-size: {self.theme.typography.caption.font_size};
    font-weight: {self.theme.typography.caption.font_weight};
    color: var(--color-text-secondary);
}}

.button {{
    font-family: {self.theme.typography.button.font_family};
    font-size: {self.theme.typography.button.font_size};
    font-weight: {self.theme.typography.button.font_weight};
    letter-spacing: {self.theme.typography.button.letter_spacing or 'normal'};
}}"""
    
    def _generate_component_styles(self) -> str:
        """Generate component styles"""
        return """
/* Header */
.header {
    background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
    color: white;
    padding: var(--spacing-xl) var(--spacing-lg);
    border-radius: var(--border-radius-lg);
    margin-bottom: var(--spacing-xl);
    box-shadow: var(--shadow-lg);
}

.header h1 {
    color: white;
    margin-bottom: var(--spacing-sm);
}

.header .subtitle {
    opacity: 0.9;
    font-size: 1.1rem;
}

/* Metrics Grid */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.metric-card {
    background: var(--color-surface);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-md);
    text-align: center;
    border: var(--border-width) solid var(--border-color);
}

.metric-card .value {
    font-size: 2.5rem;
    font-weight: bold;
    color: var(--color-primary);
    margin: var(--spacing-sm) 0;
}

.metric-card .label {
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Tables */
.data-table {
    background: var(--color-surface);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-md);
    overflow: hidden;
    margin-bottom: var(--spacing-xl);
}

.data-table h2 {
    margin: 0;
    padding: var(--spacing-lg);
    background: var(--color-surface);
    border-bottom: var(--border-width) solid var(--border-color);
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: var(--spacing-md) var(--spacing-lg);
    text-align: left;
    border-bottom: var(--border-width) solid var(--border-color);
}

th {
    background: var(--color-surface);
    font-weight: 600;
    color: var(--color-text-primary);
}

tr:hover {
    background: rgba(var(--color-primary-rgb), 0.05);
}

tr:last-child td {
    border-bottom: none;
}

/* Links */
a {
    color: var(--color-primary);
    text-decoration: none;
    font-weight: 500;
}

a:hover {
    text-decoration: underline;
}

/* Charts */
.chart-container {
    background: var(--color-surface);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-md);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.chart-container h2 {
    margin: 0 0 var(--spacing-md) 0;
    color: var(--color-text-primary);
}

/* Footer */
.footer {
    text-align: center;
    color: var(--color-text-secondary);
    margin-top: var(--spacing-xxl);
    padding-top: var(--spacing-xl);
    border-top: var(--border-width) solid var(--border-color);
}

/* Confidence Levels */
.confidence-high {
    background-color: var(--color-success);
    color: #155724;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-sm);
}

.confidence-medium {
    background-color: var(--color-warning);
    color: #856404;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-sm);
}

.confidence-low {
    background-color: var(--color-error);
    color: #721c24;
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--border-radius-sm);
}"""
    
    def _generate_utility_styles(self) -> str:
        """Generate utility styles"""
        return """
/* Utility Classes */
.text-primary { color: var(--color-text-primary); }
.text-secondary { color: var(--color-text-secondary); }
.text-center { text-align: center; }
.text-right { text-align: right; }

.mt-sm { margin-top: var(--spacing-sm); }
.mt-md { margin-top: var(--spacing-md); }
.mt-lg { margin-top: var(--spacing-lg); }
.mb-sm { margin-bottom: var(--spacing-sm); }
.mb-md { margin-bottom: var(--spacing-md); }
.mb-lg { margin-bottom: var(--spacing-lg); }

.p-sm { padding: var(--spacing-sm); }
.p-md { padding: var(--spacing-md); }
.p-lg { padding: var(--spacing-lg); }"""
    
    def _generate_chart_styles(self) -> str:
        """Generate chart-specific styles"""
        return """
/* Chart color schemes */
.chart-primary { color: var(--color-primary); }
.chart-secondary { color: var(--color-secondary); }
.chart-accent { color: var(--color-accent); }

/* Plotly overrides */
.plotly .main-svg {
    border-radius: var(--border-radius-sm);
}"""
    
    def get_chart_colors(self) -> dict:
        """Get chart color configuration"""
        return {
            "primary": self.theme.colors.primary.hex,
            "primary_rgba": lambda alpha: self.theme.colors.primary.to_rgba(alpha),
            "secondary": self.theme.colors.secondary.hex,
            "secondary_rgba": lambda alpha: self.theme.colors.secondary.to_rgba(alpha),
            "accent": self.theme.colors.accent.hex,
            "accent_rgba": lambda alpha: self.theme.colors.accent.to_rgba(alpha),
            "success": self.theme.colors.success.hex,
            "warning": self.theme.colors.warning.hex,
            "error": self.theme.colors.error.hex,
            "palette": [
                self.theme.colors.primary.rgb or "102, 126, 234",
                self.theme.colors.secondary.rgb or "78, 205, 196",
                self.theme.colors.accent.rgb or "255, 107, 107",
                "103, 126, 234",  # Additional colors
                "255, 193, 7",
                "255, 87, 34",
                "76, 175, 80",
                "156, 39, 176"
            ]
        }