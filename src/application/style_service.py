"""Application service for managing styles and themes"""
from pathlib import Path
from typing import Optional

from ..domain.styles import Theme, ThemeRepository
from ..infrastructure.theme_repository import FileThemeRepository
from ..presentation.style_generator import StyleGenerator


class StyleService:
    """Service for managing application styling"""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            config_dir = Path.home() / ".jira-monte-carlo"
        self.theme_repository: ThemeRepository = FileThemeRepository(config_dir)
        self._current_theme: Optional[Theme] = None
        self._style_generator: Optional[StyleGenerator] = None

    def get_theme(self, theme_name: Optional[str] = None) -> Theme:
        """Get theme by name or default"""
        if theme_name:
            theme = self.theme_repository.get_theme(theme_name)
            if theme:
                self._current_theme = theme
                self._style_generator = StyleGenerator(theme)
                return theme

        # Fallback to default
        theme = self.theme_repository.get_default_theme()
        self._current_theme = theme
        self._style_generator = StyleGenerator(theme)
        return theme

    def get_style_generator(self, theme_name: Optional[str] = None) -> StyleGenerator:
        """Get style generator for theme"""
        if theme_name or not self._style_generator:
            self.get_theme(theme_name)
        return self._style_generator

    def generate_css(self, theme_name: Optional[str] = None) -> str:
        """Generate CSS for theme"""
        generator = self.get_style_generator(theme_name)
        return generator.generate_css()

    def get_chart_colors(self, theme_name: Optional[str] = None) -> dict:
        """Get chart colors for theme"""
        generator = self.get_style_generator(theme_name)
        return generator.get_chart_colors()

    def save_custom_theme(self, theme: Theme) -> None:
        """Save a custom theme"""
        self.theme_repository.save_theme(theme)

    def list_available_themes(self) -> list[str]:
        """List all available theme names"""
        # For now, return hardcoded list
        # Could be enhanced to scan themes file
        return ["default", "opreto"]
