"""Clean architecture compliant style service"""
from typing import Any, Dict, Optional

from ..domain.style_generation import StyleGenerator
from ..domain.styles import Theme, ThemeRepository


class CleanStyleService:
    """Service for managing application styling with dependency injection"""

    def __init__(self, theme_repository: ThemeRepository, style_generator: StyleGenerator):
        """Initialize with injected dependencies

        Args:
            theme_repository: Repository for managing themes
            style_generator: Generator for creating styles from themes
        """
        self.theme_repository = theme_repository
        self.style_generator = style_generator
        self._current_theme: Optional[Theme] = None

    def get_theme(self, theme_name: Optional[str] = None) -> Theme:
        """Get theme by name or default"""
        if theme_name:
            theme = self.theme_repository.get_theme(theme_name)
            if theme:
                self._current_theme = theme
                return theme

        # Fallback to default
        theme = self.theme_repository.get_default_theme()
        self._current_theme = theme
        return theme

    def generate_css(self, theme_name: Optional[str] = None) -> str:
        """Generate CSS for theme"""
        theme = self.get_theme(theme_name) if theme_name else self._current_theme
        if not theme:
            theme = self.get_theme()
        return self.style_generator.generate_css(theme)

    def get_chart_colors(self, theme_name: Optional[str] = None) -> Dict[str, str]:
        """Get chart colors for theme"""
        theme = self.get_theme(theme_name) if theme_name else self._current_theme
        if not theme:
            theme = self.get_theme()
        return self.style_generator.generate_colors(theme)

    def get_chart_config(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """Get chart configuration for theme"""
        theme = self.get_theme(theme_name) if theme_name else self._current_theme
        if not theme:
            theme = self.get_theme()
        return self.style_generator.generate_chart_config(theme)

    def save_custom_theme(self, theme: Theme) -> None:
        """Save a custom theme"""
        self.theme_repository.save_theme(theme)

    def list_available_themes(self) -> list[str]:
        """List all available theme names"""
        return self.theme_repository.list_themes()
