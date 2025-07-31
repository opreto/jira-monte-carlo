"""Factory for creating style service with proper dependency injection"""

from pathlib import Path
from typing import Optional

from ..domain.style_generation import StyleGenerator
from ..domain.styles import ThemeRepository
from .clean_style_service import CleanStyleService


class StyleServiceFactory:
    """Factory for creating style service instances with clean architecture"""

    def __init__(self):
        self._theme_repository_class = None
        self._style_generator_class = None

    def register_theme_repository(self, repository_class: type):
        """Register the theme repository implementation to use"""
        if not issubclass(repository_class, ThemeRepository):
            raise TypeError(
                f"{repository_class} must implement ThemeRepository interface"
            )
        self._theme_repository_class = repository_class

    def register_style_generator(self, generator_class: type):
        """Register the style generator implementation to use"""
        if not issubclass(generator_class, StyleGenerator):
            raise TypeError(
                f"{generator_class} must implement StyleGenerator interface"
            )
        self._style_generator_class = generator_class

    def create(self, config_dir: Optional[Path] = None) -> CleanStyleService:
        """
        Create a style service instance with proper dependencies.

        Args:
            config_dir: Configuration directory path

        Returns:
            CleanStyleService instance

        Raises:
            RuntimeError: If dependencies not registered
        """
        if not self._theme_repository_class:
            raise RuntimeError(
                "Theme repository not registered. Call register_theme_repository first."
            )
        if not self._style_generator_class:
            raise RuntimeError(
                "Style generator not registered. Call register_style_generator first."
            )

        # Create instances
        if config_dir is None:
            config_dir = Path.home() / ".sprint-radar"

        theme_repository = self._theme_repository_class(config_dir)
        style_generator = self._style_generator_class()

        return CleanStyleService(theme_repository, style_generator)
