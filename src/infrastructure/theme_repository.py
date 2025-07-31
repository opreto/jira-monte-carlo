"""Theme repository implementation"""

import json
from pathlib import Path
from typing import Dict, Optional

from ..domain.styles import (
    Borders,
    ChartColors,
    Color,
    ColorPalette,
    Shadows,
    Spacing,
    Theme,
    ThemeRepository,
    Typography,
    TypographySystem,
)


class FileThemeRepository(ThemeRepository):
    """File-based theme repository"""

    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.themes_file = config_dir / "themes.json"
        self._ensure_config_dir()
        self._ensure_default_themes()

    def _ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_default_themes(self):
        """Ensure default themes exist"""
        if not self.themes_file.exists():
            default_themes = {
                "generic": self._serialize_theme(self._create_generic_theme()),
                "opreto": self._serialize_theme(self._create_opreto_theme()),
            }
            self._save_themes(default_themes)

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        themes = self._load_themes()
        theme_data = themes.get(name)
        if theme_data:
            return self._deserialize_theme(name, theme_data)
        return None

    def get_default_theme(self) -> Theme:
        """Get default theme"""
        return self.get_theme("opreto") or self._create_opreto_theme()

    def save_theme(self, theme: Theme) -> None:
        """Save a theme"""
        themes = self._load_themes()
        themes[theme.name] = self._serialize_theme(theme)
        self._save_themes(themes)

    def _load_themes(self) -> Dict:
        """Load themes from file"""
        if self.themes_file.exists():
            with open(self.themes_file, "r") as f:
                return json.load(f)
        return {}

    def _save_themes(self, themes: Dict) -> None:
        """Save themes to file"""
        with open(self.themes_file, "w") as f:
            json.dump(themes, f, indent=2)

    def _create_generic_theme(self) -> Theme:
        """Create generic theme"""
        return Theme(
            name="generic",
            colors=ColorPalette(
                primary=Color(hex="#667eea", rgb="102, 126, 234", name="Purple"),
                primary_dark=Color(
                    hex="#764ba2", rgb="118, 75, 162", name="Dark Purple"
                ),
                secondary=Color(hex="#4ecdc4", rgb="78, 205, 196", name="Teal"),
                accent=Color(hex="#ff6b6b", rgb="255, 107, 107", name="Red"),
                background=Color(hex="#f5f5f5", name="Light Gray"),
                surface=Color(hex="#ffffff", name="White"),
                text_primary=Color(hex="#333333", name="Dark Gray"),
                text_secondary=Color(hex="#666666", name="Gray"),
                success=Color(hex="#d4edda", name="Light Green"),
                warning=Color(hex="#fff3cd", name="Light Yellow"),
                error=Color(hex="#f8d7da", name="Light Red"),
                info=Color(hex="#d1ecf1", name="Light Blue"),
                chart_colors=ChartColors(
                    # Semantic colors for confidence levels
                    high_confidence=Color(
                        hex="#28a745", rgb="40, 167, 69", name="Success Green"
                    ),
                    medium_confidence=Color(
                        hex="#ffc107", rgb="255, 193, 7", name="Warning Amber"
                    ),
                    low_confidence=Color(
                        hex="#dc3545", rgb="220, 53, 69", name="Danger Red"
                    ),
                    neutral=Color(
                        hex="#6c757d", rgb="108, 117, 125", name="Neutral Gray"
                    ),
                    # Data series colors (colorblind-friendly)
                    data1=Color(hex="#667eea", rgb="102, 126, 234", name="Purple"),
                    data2=Color(hex="#4ecdc4", rgb="78, 205, 196", name="Teal"),
                    data3=Color(hex="#ff6b6b", rgb="255, 107, 107", name="Red"),
                    data4=Color(hex="#feca57", rgb="254, 202, 87", name="Yellow"),
                    data5=Color(hex="#48dbfb", rgb="72, 219, 251", name="Light Blue"),
                    # Gradient colors
                    gradient_start=Color(
                        hex="#667eea", rgb="102, 126, 234", name="Purple"
                    ),
                    gradient_mid=Color(
                        hex="#a855f7", rgb="168, 85, 247", name="Mid Purple"
                    ),
                    gradient_end=Color(hex="#ec4899", rgb="236, 72, 153", name="Pink"),
                ),
            ),
            typography=TypographySystem(
                heading1=Typography(
                    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    font_size="2.5rem",
                    font_weight="bold",
                ),
                heading2=Typography(
                    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    font_size="1.5rem",
                    font_weight="600",
                ),
                heading3=Typography(
                    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    font_size="1.25rem",
                    font_weight="600",
                ),
                body=Typography(
                    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    font_size="1rem",
                    line_height="1.6",
                ),
                caption=Typography(
                    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    font_size="0.9rem",
                    font_weight="normal",
                ),
                button=Typography(
                    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
                    font_size="1rem",
                    font_weight="500",
                    letter_spacing="0.5px",
                ),
            ),
            spacing=Spacing(),
            shadows=Shadows(),
            borders=Borders(),
        )

    def _create_opreto_theme(self) -> Theme:
        """Create Opreto theme based on style guide"""
        return Theme(
            name="opreto",
            colors=ColorPalette(
                primary=Color(hex="#03564c", rgb="3, 86, 76", name="Teal"),
                primary_dark=Color(hex="#022d2c", rgb="2, 45, 44", name="Dark Teal"),
                secondary=Color(hex="#6B1229", rgb="107, 18, 41", name="Burgundy"),
                accent=Color(hex="#0E5473", rgb="14, 84, 115", name="Cerulean Blue"),
                background=Color(hex="#FFFFFF", name="White"),
                surface=Color(hex="#F8F9FA", name="Light Surface"),
                text_primary=Color(hex="#022d2c", name="Dark Teal"),
                text_secondary=Color(hex="#495057", name="Gray"),
                success=Color(hex="#D1F2D9", name="Light Green"),
                warning=Color(hex="#FFF3CD", name="Light Yellow"),
                error=Color(hex="#F8D7DA", name="Light Red"),
                info=Color(hex="#D1ECF1", name="Light Blue"),
                chart_colors=ChartColors(
                    # Semantic colors following BI best practices
                    high_confidence=Color(
                        hex="#00A86B", rgb="0, 168, 107", name="Jade Green"
                    ),
                    medium_confidence=Color(
                        hex="#FFA500", rgb="255, 165, 0", name="Orange"
                    ),
                    low_confidence=Color(
                        hex="#DC143C", rgb="220, 20, 60", name="Crimson"
                    ),
                    neutral=Color(hex="#03564c", rgb="3, 86, 76", name="Teal"),
                    # Data series colors (colorblind-friendly, professional)
                    data1=Color(hex="#03564c", rgb="3, 86, 76", name="Primary Teal"),
                    data2=Color(hex="#0E5473", rgb="14, 84, 115", name="Cerulean Blue"),
                    data3=Color(hex="#6B1229", rgb="107, 18, 41", name="Burgundy"),
                    data4=Color(hex="#FF8C00", rgb="255, 140, 0", name="Dark Orange"),
                    data5=Color(hex="#4B0082", rgb="75, 0, 130", name="Indigo"),
                    # Gradient colors for distributions
                    gradient_start=Color(
                        hex="#00A86B", rgb="0, 168, 107", name="Jade Green"
                    ),
                    gradient_mid=Color(hex="#FFA500", rgb="255, 165, 0", name="Orange"),
                    gradient_end=Color(
                        hex="#DC143C", rgb="220, 20, 60", name="Crimson"
                    ),
                ),
            ),
            typography=TypographySystem(
                heading1=Typography(
                    font_family="'Sublima', -apple-system, BlinkMacSystemFont, sans-serif",
                    font_size="3rem",
                    font_weight="700",
                    letter_spacing="-0.02em",
                ),
                heading2=Typography(
                    font_family="'Sublima', -apple-system, BlinkMacSystemFont, sans-serif",
                    font_size="2rem",
                    font_weight="600",
                    letter_spacing="-0.01em",
                ),
                heading3=Typography(
                    font_family="'Sublima', -apple-system, BlinkMacSystemFont, sans-serif",
                    font_size="1.5rem",
                    font_weight="600",
                ),
                body=Typography(
                    font_family="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    font_size="1rem",
                    line_height="1.7",
                    font_weight="400",
                ),
                caption=Typography(
                    font_family="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    font_size="0.875rem",
                    font_weight="400",
                ),
                button=Typography(
                    font_family="'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
                    font_size="1rem",
                    font_weight="500",
                    letter_spacing="0.02em",
                ),
            ),
            spacing=Spacing(
                xs="0.25rem", sm="0.5rem", md="1rem", lg="2rem", xl="3rem", xxl="4rem"
            ),
            shadows=Shadows(
                sm="0 1px 3px rgba(2, 45, 44, 0.08)",
                md="0 2px 6px rgba(2, 45, 44, 0.12)",
                lg="0 4px 12px rgba(2, 45, 44, 0.15)",
                xl="0 8px 24px rgba(2, 45, 44, 0.18)",
            ),
            borders=Borders(
                radius_sm="4px",
                radius_md="8px",
                radius_lg="16px",
                radius_full="9999px",
                width="1px",
                color="#E5E7EB",
            ),
            custom_css="""
/* Opreto Custom Styles */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Hero archetype styling */
.header {
    background: linear-gradient(135deg, #03564c 0%, #022d2c 100%);
    position: relative;
    overflow: hidden;
}

.header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 50%;
    height: 200%;
    background: rgba(255, 255, 255, 0.05);
    transform: rotate(35deg);
}

/* Dynamic elements */
.metric-card {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(2, 45, 44, 0.15);
}

/* Professional yet bold */
.chart-container {
    border-top: 3px solid #03564c;
}

/* Asymmetric design elements */
.projects-table tr:nth-child(odd) {
    background-color: rgba(3, 86, 76, 0.02);
}

/* Collaborative feel */
.project-link {
    color: #03564c;
    position: relative;
    transition: color 0.2s ease;
}

.project-link::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 0;
    height: 2px;
    background-color: #0E5473;
    transition: width 0.3s ease;
}

.project-link:hover::after {
    width: 100%;
}
""",
        )

    def _serialize_theme(self, theme: Theme) -> Dict:
        """Serialize theme to dictionary"""
        return {
            "colors": {
                "primary": {
                    "hex": theme.colors.primary.hex,
                    "rgb": theme.colors.primary.rgb,
                    "name": theme.colors.primary.name,
                },
                "primary_dark": {
                    "hex": theme.colors.primary_dark.hex,
                    "rgb": theme.colors.primary_dark.rgb,
                    "name": theme.colors.primary_dark.name,
                },
                "secondary": {
                    "hex": theme.colors.secondary.hex,
                    "rgb": theme.colors.secondary.rgb,
                    "name": theme.colors.secondary.name,
                },
                "accent": {
                    "hex": theme.colors.accent.hex,
                    "rgb": theme.colors.accent.rgb,
                    "name": theme.colors.accent.name,
                },
                "background": {
                    "hex": theme.colors.background.hex,
                    "rgb": theme.colors.background.rgb,
                    "name": theme.colors.background.name,
                },
                "surface": {
                    "hex": theme.colors.surface.hex,
                    "rgb": theme.colors.surface.rgb,
                    "name": theme.colors.surface.name,
                },
                "text_primary": {
                    "hex": theme.colors.text_primary.hex,
                    "rgb": theme.colors.text_primary.rgb,
                    "name": theme.colors.text_primary.name,
                },
                "text_secondary": {
                    "hex": theme.colors.text_secondary.hex,
                    "rgb": theme.colors.text_secondary.rgb,
                    "name": theme.colors.text_secondary.name,
                },
                "success": {
                    "hex": theme.colors.success.hex,
                    "rgb": theme.colors.success.rgb,
                    "name": theme.colors.success.name,
                },
                "warning": {
                    "hex": theme.colors.warning.hex,
                    "rgb": theme.colors.warning.rgb,
                    "name": theme.colors.warning.name,
                },
                "error": {
                    "hex": theme.colors.error.hex,
                    "rgb": theme.colors.error.rgb,
                    "name": theme.colors.error.name,
                },
                "info": {
                    "hex": theme.colors.info.hex,
                    "rgb": theme.colors.info.rgb,
                    "name": theme.colors.info.name,
                },
            },
            "chart_colors": (
                self._serialize_chart_colors(theme.colors.chart_colors)
                if theme.colors.chart_colors
                else None
            ),
            "typography": {
                "heading1": self._serialize_typography(theme.typography.heading1),
                "heading2": self._serialize_typography(theme.typography.heading2),
                "heading3": self._serialize_typography(theme.typography.heading3),
                "body": self._serialize_typography(theme.typography.body),
                "caption": self._serialize_typography(theme.typography.caption),
                "button": self._serialize_typography(theme.typography.button),
            },
            "spacing": {
                "xs": theme.spacing.xs,
                "sm": theme.spacing.sm,
                "md": theme.spacing.md,
                "lg": theme.spacing.lg,
                "xl": theme.spacing.xl,
                "xxl": theme.spacing.xxl,
            },
            "shadows": {
                "sm": theme.shadows.sm,
                "md": theme.shadows.md,
                "lg": theme.shadows.lg,
                "xl": theme.shadows.xl,
            },
            "borders": {
                "radius_sm": theme.borders.radius_sm,
                "radius_md": theme.borders.radius_md,
                "radius_lg": theme.borders.radius_lg,
                "radius_full": theme.borders.radius_full,
                "width": theme.borders.width,
                "color": theme.borders.color,
            },
            "custom_css": theme.custom_css,
        }

    def _serialize_typography(self, typography: Typography) -> Dict:
        """Serialize typography to dictionary"""
        return {
            "font_family": typography.font_family,
            "font_size": typography.font_size,
            "font_weight": typography.font_weight,
            "line_height": typography.line_height,
            "letter_spacing": typography.letter_spacing,
        }

    def _serialize_chart_colors(self, chart_colors: ChartColors) -> Dict:
        """Serialize chart colors to dictionary"""
        return {
            "high_confidence": {
                "hex": chart_colors.high_confidence.hex,
                "rgb": chart_colors.high_confidence.rgb,
                "name": chart_colors.high_confidence.name,
            },
            "medium_confidence": {
                "hex": chart_colors.medium_confidence.hex,
                "rgb": chart_colors.medium_confidence.rgb,
                "name": chart_colors.medium_confidence.name,
            },
            "low_confidence": {
                "hex": chart_colors.low_confidence.hex,
                "rgb": chart_colors.low_confidence.rgb,
                "name": chart_colors.low_confidence.name,
            },
            "neutral": {
                "hex": chart_colors.neutral.hex,
                "rgb": chart_colors.neutral.rgb,
                "name": chart_colors.neutral.name,
            },
            "data1": {
                "hex": chart_colors.data1.hex,
                "rgb": chart_colors.data1.rgb,
                "name": chart_colors.data1.name,
            },
            "data2": {
                "hex": chart_colors.data2.hex,
                "rgb": chart_colors.data2.rgb,
                "name": chart_colors.data2.name,
            },
            "data3": {
                "hex": chart_colors.data3.hex,
                "rgb": chart_colors.data3.rgb,
                "name": chart_colors.data3.name,
            },
            "data4": {
                "hex": chart_colors.data4.hex,
                "rgb": chart_colors.data4.rgb,
                "name": chart_colors.data4.name,
            },
            "data5": {
                "hex": chart_colors.data5.hex,
                "rgb": chart_colors.data5.rgb,
                "name": chart_colors.data5.name,
            },
            "gradient_start": {
                "hex": chart_colors.gradient_start.hex,
                "rgb": chart_colors.gradient_start.rgb,
                "name": chart_colors.gradient_start.name,
            },
            "gradient_mid": {
                "hex": chart_colors.gradient_mid.hex,
                "rgb": chart_colors.gradient_mid.rgb,
                "name": chart_colors.gradient_mid.name,
            },
            "gradient_end": {
                "hex": chart_colors.gradient_end.hex,
                "rgb": chart_colors.gradient_end.rgb,
                "name": chart_colors.gradient_end.name,
            },
        }

    def _deserialize_theme(self, name: str, data: Dict) -> Theme:
        """Deserialize theme from dictionary"""
        colors_data = data["colors"]

        # Deserialize chart colors if present
        chart_colors = None
        if "chart_colors" in data and data["chart_colors"]:
            chart_data = data["chart_colors"]
            chart_colors = ChartColors(
                high_confidence=Color(**chart_data["high_confidence"]),
                medium_confidence=Color(**chart_data["medium_confidence"]),
                low_confidence=Color(**chart_data["low_confidence"]),
                neutral=Color(**chart_data["neutral"]),
                data1=Color(**chart_data["data1"]),
                data2=Color(**chart_data["data2"]),
                data3=Color(**chart_data["data3"]),
                data4=Color(**chart_data["data4"]),
                data5=Color(**chart_data["data5"]),
                gradient_start=Color(**chart_data["gradient_start"]),
                gradient_mid=Color(**chart_data["gradient_mid"]),
                gradient_end=Color(**chart_data["gradient_end"]),
            )

        colors = ColorPalette(
            primary=Color(**colors_data["primary"]),
            primary_dark=Color(**colors_data["primary_dark"]),
            secondary=Color(**colors_data["secondary"]),
            accent=Color(**colors_data["accent"]),
            background=Color(**colors_data["background"]),
            surface=Color(**colors_data["surface"]),
            text_primary=Color(**colors_data["text_primary"]),
            text_secondary=Color(**colors_data["text_secondary"]),
            success=Color(**colors_data["success"]),
            warning=Color(**colors_data["warning"]),
            error=Color(**colors_data["error"]),
            info=Color(**colors_data["info"]),
            chart_colors=chart_colors,
        )

        typography_data = data["typography"]
        typography = TypographySystem(
            heading1=Typography(**typography_data["heading1"]),
            heading2=Typography(**typography_data["heading2"]),
            heading3=Typography(**typography_data["heading3"]),
            body=Typography(**typography_data["body"]),
            caption=Typography(**typography_data["caption"]),
            button=Typography(**typography_data["button"]),
        )

        spacing = Spacing(**data["spacing"])
        shadows = Shadows(**data["shadows"])
        borders = Borders(**data["borders"])

        return Theme(
            name=name,
            colors=colors,
            typography=typography,
            spacing=spacing,
            shadows=shadows,
            borders=borders,
            custom_css=data.get("custom_css"),
        )
