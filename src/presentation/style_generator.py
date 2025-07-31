"""Style generator for HTML reports"""

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
            self._generate_chart_styles(),
            self._generate_scenario_styles(),
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
    --color-primary-rgb: {self.theme.colors.primary.rgb or "102, 126, 234"};
    --color-secondary-rgb: {self.theme.colors.secondary.rgb or "78, 205, 196"};
    --color-accent-rgb: {self.theme.colors.accent.rgb or "255, 107, 107"};
    
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
    letter-spacing: {self.theme.typography.heading1.letter_spacing or "normal"};
    margin: 0 0 var(--spacing-md) 0;
    color: var(--color-text-primary);
}}

h2 {{
    font-family: {self.theme.typography.heading2.font_family};
    font-size: {self.theme.typography.heading2.font_size};
    font-weight: {self.theme.typography.heading2.font_weight};
    line-height: {self.theme.typography.heading2.line_height};
    letter-spacing: {self.theme.typography.heading2.letter_spacing or "normal"};
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
    letter-spacing: {self.theme.typography.button.letter_spacing or "normal"};
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
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Chart descriptions */
.chart-description {
    font-size: 0.9rem;
    color: var(--color-text-secondary);
    line-height: 1.6;
    margin-bottom: var(--spacing-md);
    padding: var(--spacing-sm) var(--spacing-md);
    background: rgba(var(--color-primary-rgb), 0.05);
    border-radius: var(--border-radius-sm);
    border-left: 3px solid var(--color-primary);
}

.chart-description strong {
    color: var(--color-text-primary);
    font-weight: 600;
}

/* Chart toggle buttons */
.chart-toggle {
    display: inline-flex;
    gap: 0;
    border-radius: var(--border-radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.toggle-btn {
    background: var(--color-background);
    border: var(--border-width) solid var(--border-color);
    color: var(--color-text-secondary);
    padding: var(--spacing-sm) var(--spacing-md);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-size: var(--font-size-sm);
    font-weight: 500;
}

.toggle-btn:first-child {
    border-right: none;
    border-radius: var(--border-radius-md) 0 0 var(--border-radius-md);
}

.toggle-btn:last-child {
    border-radius: 0 var(--border-radius-md) var(--border-radius-md) 0;
}

.toggle-btn:hover {
    background: rgba(var(--color-primary-rgb), 0.1);
    color: var(--color-primary);
}

.toggle-btn.active {
    background: var(--color-primary);
    color: white;
    border-color: var(--color-primary);
}

.toggle-btn svg {
    width: 16px;
    height: 16px;
}

/* Chart transition animation */
.chart-transition {
    transition: opacity 0.3s ease;
    min-height: 450px;  /* Prevent layout shift during transitions */
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
}

/* Tooltip */
.tooltip {
    position: relative;
    display: inline-block;
    cursor: help;
}

.tooltip-icon {
    color: var(--color-primary);
    font-weight: bold;
    margin-left: 0.25rem;
    font-size: 1.1rem;
    cursor: help;
    display: inline-block;
    width: 20px;
    height: 20px;
    line-height: 20px;
    text-align: center;
    border-radius: 50%;
    background-color: rgba(var(--color-primary-rgb), 0.1);
    border: 1px solid var(--color-primary);
}

.tooltip-text {
    visibility: hidden;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    background-color: var(--color-surface);
    color: var(--color-text-primary);
    text-align: left;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--border-radius-sm);
    box-shadow: var(--shadow-md);
    min-width: 250px;
    white-space: normal;
    opacity: 0;
    transition: opacity 0.3s;
    border: 1px solid var(--border-color);
}

.tooltip:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}

.tooltip-text::after {
    content: "";
    position: absolute;
    top: 100%;
    left: 50%;
    margin-left: -5px;
    border-width: 5px;
    border-style: solid;
    border-color: var(--color-surface) transparent transparent transparent;
}

/* JQL Query Display */
.jql-query-container {
    background: var(--color-surface);
    border-radius: var(--border-radius-md);
    box-shadow: var(--shadow-md);
    padding: var(--spacing-lg);
    margin-bottom: var(--spacing-xl);
}

.jql-query-container h3 {
    margin-top: 0;
    margin-bottom: var(--spacing-sm);
    color: var(--color-text-secondary);
    font-size: 0.9rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.jql-query {
    background-color: var(--color-background);
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    padding: var(--spacing-md);
    overflow-x: auto;
    margin: 0;
}

.jql-query code {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.9rem;
    line-height: 1.5;
    color: var(--color-text-primary);
    white-space: pre-wrap;
    word-break: break-word;
}

/* Expandable Issue Details */
.issue-details {
    margin-top: var(--spacing-sm);
}

.issue-details summary {
    outline: none;
    user-select: none;
    transition: color 0.2s;
}

.issue-details summary:hover {
    color: var(--color-primary-dark);
}

.issue-details summary::-webkit-details-marker {
    display: none;
}

.issue-details[open] summary {
    margin-bottom: var(--spacing-sm);
}

.issue-list {
    border: 1px solid var(--border-color);
    border-radius: var(--border-radius-sm);
    background-color: var(--color-background);
    padding: var(--spacing-sm);
}

.issue-list table {
    font-family: var(--font-family-body);
}

.issue-list th {
    font-weight: 600;
    color: var(--color-text-secondary);
    text-transform: uppercase;
    font-size: 0.75rem;
    letter-spacing: 0.5px;
}

.issue-list tr:hover {
    background-color: var(--color-surface);
}

.status-badge {
    display: inline-block;
    font-weight: 500;
    text-transform: uppercase;
    font-size: 0.7rem;
    letter-spacing: 0.5px;
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

    def _generate_scenario_styles(self) -> str:
        """Generate styles for velocity scenario banners"""
        return """
/* Scenario Banner Styles */
.scenario-banner {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border: 2px solid #0284c7;
    border-radius: 12px;
    padding: 20px;
    margin: 20px 0;
    position: relative;
    overflow: hidden;
}

.scenario-banner::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.2) 0%, transparent 70%);
    transform: rotate(45deg);
}

.scenario-banner h3 {
    color: #0369a1;
    margin: 0 0 10px 0;
    font-size: 1.3em;
    position: relative;
    z-index: 1;
}

.scenario-banner p {
    margin: 5px 0;
    color: #075985;
    position: relative;
    z-index: 1;
}

.scenario-banner strong {
    color: #0c4a6e;
}

.scenario-link {
    display: inline-block;
    margin-top: 10px;
    padding: 8px 16px;
    background: #0284c7;
    color: white;
    text-decoration: none;
    border-radius: 6px;
    transition: all 0.3s ease;
    position: relative;
    z-index: 1;
}

.scenario-link:hover {
    background: #0369a1;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.3);
}

.baseline-banner {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border-color: #16a34a;
}

.baseline-banner h3 {
    color: #15803d;
}

.baseline-banner p {
    color: #166534;
}

.baseline-banner .scenario-link {
    background: #16a34a;
}

.baseline-banner .scenario-link:hover {
    background: #15803d;
    box-shadow: 0 4px 12px rgba(22, 163, 74, 0.3);
}

.adjusted-banner {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-color: #f59e0b;
}

.adjusted-banner h3 {
    color: #d97706;
}

.adjusted-banner p {
    color: #92400e;
}

.adjusted-banner .scenario-link {
    background: #f59e0b;
}

.adjusted-banner .scenario-link:hover {
    background: #d97706;
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
}

/* Combined Report Styles */
.combined-banner {
    background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
    border-color: #6b7280;
    position: sticky;
    top: 0;
    z-index: 100;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
.combined-banner h3 {
    color: #374151;
}
.scenario-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}
.scenario-toggle {
    display: flex;
    gap: 20px;
}
.toggle-label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    background: #e5e7eb;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    font-weight: 500;
}
.toggle-label:hover {
    background: #d1d5db;
}
.toggle-label input[type="radio"] {
    cursor: pointer;
}
.toggle-label:has(input[type="radio"]:checked) {
    background: #3b82f6;
    color: white;
}
.scenario-description {
    padding: 15px;
    background: rgba(59, 130, 246, 0.05);
    border-radius: 8px;
    border-left: 4px solid #3b82f6;
}
.baseline-notice {
    padding: 15px;
    background: rgba(34, 197, 94, 0.05);
    border-radius: 8px;
    border-left: 4px solid #22c55e;
}

/* Sticky behavior improvements */
@media (min-width: 768px) {
    .combined-banner {
        margin: 0 -20px 20px -20px;
        padding: 20px 40px;
        border-radius: 0;
    }
}

/* Mobile responsive toggle */
@media (max-width: 767px) {
    .scenario-header {
        flex-direction: column;
        gap: 10px;
    }
    .scenario-toggle {
        width: 100%;
        justify-content: center;
    }
    .toggle-label {
        flex: 1;
        justify-content: center;
    }
}

/* Ensure content doesn't jump when sticky */
.report-container {
    scroll-padding-top: 200px;
}
"""

    def get_chart_colors(self) -> dict:
        """Get chart color configuration with BI best practices"""
        if self.theme.colors.chart_colors:
            cc = self.theme.colors.chart_colors
            return {
                # Semantic colors for confidence levels (RGB convention)
                "high_confidence": cc.high_confidence.hex,  # Green = Good/Safe
                "medium_confidence": cc.medium_confidence.hex,  # Amber = Caution
                "low_confidence": cc.low_confidence.hex,  # Red = Risk/Warning
                "neutral": cc.neutral.hex,  # Blue/Gray = Neutral info
                # RGBA functions for transparency
                "high_confidence_rgba": lambda alpha: cc.high_confidence.to_rgba(alpha),
                "medium_confidence_rgba": lambda alpha: cc.medium_confidence.to_rgba(alpha),
                "low_confidence_rgba": lambda alpha: cc.low_confidence.to_rgba(alpha),
                "neutral_rgba": lambda alpha: cc.neutral.to_rgba(alpha),
                # Data visualization colors
                "data1": cc.data1.hex,
                "data2": cc.data2.hex,
                "data3": cc.data3.hex,
                "data4": cc.data4.hex,
                "data5": cc.data5.hex,
                # Gradient colors for distributions
                "gradient_start": cc.gradient_start.hex,
                "gradient_mid": cc.gradient_mid.hex,
                "gradient_end": cc.gradient_end.hex,
                # Legacy compatibility
                "primary": cc.data1.hex,
                "primary_rgba": lambda alpha: cc.data1.to_rgba(alpha),
                "secondary": cc.data2.hex,
                "secondary_rgba": lambda alpha: cc.data2.to_rgba(alpha),
                "accent": cc.data3.hex,
                "accent_rgba": lambda alpha: cc.data3.to_rgba(alpha),
                "success": cc.high_confidence.hex,
                "success_rgba": lambda alpha: cc.high_confidence.to_rgba(alpha),
                "warning": cc.medium_confidence.hex,
                "warning_rgba": lambda alpha: cc.medium_confidence.to_rgba(alpha),
                "error": cc.low_confidence.hex,
                # Add rgba functions for data colors
                "data1_rgba": lambda alpha: cc.data1.to_rgba(alpha),
                "data2_rgba": lambda alpha: cc.data2.to_rgba(alpha),
                "data3_rgba": lambda alpha: cc.data3.to_rgba(alpha),
                "data4_rgba": lambda alpha: cc.data4.to_rgba(alpha),
                "data5_rgba": lambda alpha: cc.data5.to_rgba(alpha),
            }
        else:
            # Fallback for themes without chart colors
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
                "high_confidence": self.theme.colors.success.hex,
                "medium_confidence": self.theme.colors.warning.hex,
                "low_confidence": self.theme.colors.error.hex,
                "neutral": self.theme.colors.info.hex,
            }
