"""Domain entities for styling and theming"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Color:
    """Value object representing a color"""

    hex: str
    rgb: Optional[str] = None
    name: Optional[str] = None

    def to_rgba(self, alpha: float = 1.0) -> str:
        """Convert to rgba format for CSS"""
        if self.rgb:
            return f"rgba({self.rgb}, {alpha})"
        # Convert hex to rgba
        hex_code = self.hex.lstrip("#")
        r = int(hex_code[0:2], 16)
        g = int(hex_code[2:4], 16)
        b = int(hex_code[4:6], 16)
        return f"rgba({r}, {g}, {b}, {alpha})"


@dataclass(frozen=True)
class Typography:
    """Value object for typography settings"""

    font_family: str
    font_size: str
    font_weight: str = "normal"
    line_height: str = "1.6"
    letter_spacing: Optional[str] = None


@dataclass(frozen=True)
class ChartColors:
    """Value object for chart color scheme following BI best practices"""

    # Semantic colors for different confidence levels and metrics
    high_confidence: Color  # Green - positive/safe/high confidence
    medium_confidence: Color  # Amber/Yellow - caution/medium confidence
    low_confidence: Color  # Red - risk/low confidence
    neutral: Color  # Blue/Gray - neutral/informational

    # Data visualization colors (colorblind-friendly palette)
    data1: Color  # Primary data series
    data2: Color  # Secondary data series
    data3: Color  # Tertiary data series
    data4: Color  # Additional series
    data5: Color  # Additional series

    # Gradient colors for heatmaps/distributions
    gradient_start: Color
    gradient_mid: Color
    gradient_end: Color


@dataclass(frozen=True)
class ColorPalette:
    """Value object for color palette"""

    primary: Color
    primary_dark: Color
    secondary: Color
    accent: Color
    background: Color
    surface: Color
    text_primary: Color
    text_secondary: Color
    success: Color
    warning: Color
    error: Color
    info: Color
    chart_colors: Optional[ChartColors] = None


@dataclass(frozen=True)
class TypographySystem:
    """Value object for typography system"""

    heading1: Typography
    heading2: Typography
    heading3: Typography
    body: Typography
    caption: Typography
    button: Typography


@dataclass(frozen=True)
class Spacing:
    """Value object for spacing system"""

    xs: str = "0.25rem"
    sm: str = "0.5rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"


@dataclass(frozen=True)
class Shadows:
    """Value object for shadow system"""

    sm: str = "0 1px 2px rgba(0,0,0,0.05)"
    md: str = "0 2px 4px rgba(0,0,0,0.1)"
    lg: str = "0 4px 6px rgba(0,0,0,0.1)"
    xl: str = "0 8px 12px rgba(0,0,0,0.15)"


@dataclass(frozen=True)
class Borders:
    """Value object for border system"""

    radius_sm: str = "4px"
    radius_md: str = "8px"
    radius_lg: str = "12px"
    radius_full: str = "9999px"
    width: str = "1px"
    color: str = "#dee2e6"


@dataclass(frozen=True)
class Theme:
    """Complete theme configuration"""

    name: str
    colors: ColorPalette
    typography: TypographySystem
    spacing: Spacing
    shadows: Shadows
    borders: Borders
    custom_css: Optional[str] = None


class ThemeRepository:
    """Repository interface for themes"""

    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name"""
        raise NotImplementedError

    def get_default_theme(self) -> Theme:
        """Get default theme"""
        raise NotImplementedError

    def save_theme(self, theme: Theme) -> None:
        """Save a theme"""
        raise NotImplementedError
