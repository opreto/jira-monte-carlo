"""Application layer factories for dependency injection"""

from pathlib import Path
from typing import Optional, Type

from ..domain.csv_processing import CSVAnalyzer, CSVParser, SprintExtractor
from ..domain.style_generation import StyleGenerator
from ..domain.styles import ThemeRepository


class CSVProcessingFactory:
    """Factory for creating CSV processing components"""

    def __init__(self):
        self._parsers: dict[str, Type[CSVParser]] = {}
        self._analyzers: dict[str, Type[CSVAnalyzer]] = {}
        self._extractors: dict[str, Type[SprintExtractor]] = {}

    def register_parser(self, name: str, parser_class: Type[CSVParser]):
        """Register a CSV parser implementation"""
        self._parsers[name] = parser_class

    def register_analyzer(self, name: str, analyzer_class: Type[CSVAnalyzer]):
        """Register a CSV analyzer implementation"""
        self._analyzers[name] = analyzer_class

    def register_extractor(self, name: str, extractor_class: Type[SprintExtractor]):
        """Register a sprint extractor implementation"""
        self._extractors[name] = extractor_class

    def create_parser(self, name: str = "default") -> CSVParser:
        """Create a CSV parser instance"""
        parser_class = self._parsers.get(name)
        if not parser_class:
            raise ValueError(f"No parser registered for '{name}'")
        return parser_class()

    def create_analyzer(self, name: str = "default") -> CSVAnalyzer:
        """Create a CSV analyzer instance"""
        analyzer_class = self._analyzers.get(name)
        if not analyzer_class:
            raise ValueError(f"No analyzer registered for '{name}'")
        return analyzer_class()

    def create_extractor(self, name: str = "default") -> SprintExtractor:
        """Create a sprint extractor instance"""
        extractor_class = self._extractors.get(name)
        if not extractor_class:
            raise ValueError(f"No extractor registered for '{name}'")
        return extractor_class()


class StyleServiceFactory:
    """Factory for creating style service with proper dependencies"""

    def __init__(self):
        self._theme_repository_class: Optional[Type[ThemeRepository]] = None
        self._style_generator_class: Optional[Type[StyleGenerator]] = None

    def register_theme_repository(self, repo_class: Type[ThemeRepository]):
        """Register theme repository implementation"""
        self._theme_repository_class = repo_class

    def register_style_generator(self, generator_class: Type[StyleGenerator]):
        """Register style generator implementation"""
        self._style_generator_class = generator_class

    def create_theme_repository(self, config_dir: Optional[Path] = None) -> ThemeRepository:
        """Create theme repository instance"""
        if not self._theme_repository_class:
            raise ValueError("No theme repository registered")

        if config_dir is None:
            config_dir = Path.home() / ".jira-monte-carlo"

        return self._theme_repository_class(config_dir)

    def create_style_generator(self) -> StyleGenerator:
        """Create style generator instance"""
        if not self._style_generator_class:
            raise ValueError("No style generator registered")

        return self._style_generator_class()


# Global factory instances
csv_processing_factory = CSVProcessingFactory()
style_service_factory = StyleServiceFactory()
