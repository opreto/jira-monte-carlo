"""Factory for creating CSV processing components with clean architecture"""

from typing import Dict, List, Optional, Type

from ..domain.csv_processing import CSVAnalyzer, CSVParser, SprintExtractor
from ..domain.exceptions import ConfigurationError


class CSVProcessingFactory:
    """
    Factory for creating CSV processing components.

    This factory maintains the dependency inversion principle by allowing
    infrastructure components to be registered without the application layer
    knowing about their concrete implementations.
    """

    def __init__(self):
        self._parsers: Dict[str, Type[CSVParser]] = {}
        self._analyzers: Dict[str, Type[CSVAnalyzer]] = {}
        self._extractors: Dict[str, Type[SprintExtractor]] = {}
        self._default_parser: Optional[str] = None
        self._default_analyzer: Optional[str] = None
        self._default_extractor: Optional[str] = None

    def register_parser(self, name: str, parser_class: Type[CSVParser], set_as_default: bool = False) -> None:
        """
        Register a CSV parser implementation.

        Args:
            name: Identifier for this parser
            parser_class: Class implementing CSVParser interface
            set_as_default: Whether to set as default parser
        """
        if not issubclass(parser_class, CSVParser):
            raise TypeError(f"{parser_class} must implement CSVParser interface")

        self._parsers[name] = parser_class
        if set_as_default or self._default_parser is None:
            self._default_parser = name

    def register_analyzer(self, name: str, analyzer_class: Type[CSVAnalyzer], set_as_default: bool = False) -> None:
        """
        Register a CSV analyzer implementation.

        Args:
            name: Identifier for this analyzer
            analyzer_class: Class implementing CSVAnalyzer interface
            set_as_default: Whether to set as default analyzer
        """
        if not issubclass(analyzer_class, CSVAnalyzer):
            raise TypeError(f"{analyzer_class} must implement CSVAnalyzer interface")

        self._analyzers[name] = analyzer_class
        if set_as_default or self._default_analyzer is None:
            self._default_analyzer = name

    def register_extractor(
        self,
        name: str,
        extractor_class: Type[SprintExtractor],
        set_as_default: bool = False,
    ) -> None:
        """
        Register a sprint extractor implementation.

        Args:
            name: Identifier for this extractor
            extractor_class: Class implementing SprintExtractor interface
            set_as_default: Whether to set as default extractor
        """
        if not issubclass(extractor_class, SprintExtractor):
            raise TypeError(f"{extractor_class} must implement SprintExtractor interface")

        self._extractors[name] = extractor_class
        if set_as_default or self._default_extractor is None:
            self._default_extractor = name

    def create_parser(self, name: Optional[str] = None, **kwargs) -> CSVParser:
        """
        Create a CSV parser instance.

        Args:
            name: Parser identifier, uses default if not specified
            **kwargs: Additional arguments to pass to the parser constructor

        Returns:
            CSVParser instance

        Raises:
            ConfigurationError: If parser not found
        """
        parser_name = name or self._default_parser
        if not parser_name:
            raise ConfigurationError("No CSV parser registered")

        if parser_name not in self._parsers:
            raise ConfigurationError(f"CSV parser '{parser_name}' not found. Available: {list(self._parsers.keys())}")

        return self._parsers[parser_name](**kwargs)

    def create_analyzer(self, name: Optional[str] = None, **kwargs) -> CSVAnalyzer:
        """
        Create a CSV analyzer instance.

        Args:
            name: Analyzer identifier, uses default if not specified
            **kwargs: Additional arguments to pass to the analyzer constructor

        Returns:
            CSVAnalyzer instance

        Raises:
            ConfigurationError: If analyzer not found
        """
        analyzer_name = name or self._default_analyzer
        if not analyzer_name:
            raise ConfigurationError("No CSV analyzer registered")

        if analyzer_name not in self._analyzers:
            raise ConfigurationError(
                f"CSV analyzer '{analyzer_name}' not found. Available: {list(self._analyzers.keys())}"
            )

        return self._analyzers[analyzer_name](**kwargs)

    def create_extractor(self, name: Optional[str] = None, **kwargs) -> SprintExtractor:
        """
        Create a sprint extractor instance.

        Args:
            name: Extractor identifier, uses default if not specified
            **kwargs: Additional arguments to pass to the extractor constructor

        Returns:
            SprintExtractor instance

        Raises:
            ConfigurationError: If extractor not found
        """
        extractor_name = name or self._default_extractor
        if not extractor_name:
            raise ConfigurationError("No sprint extractor registered")

        if extractor_name not in self._extractors:
            raise ConfigurationError(
                f"Sprint extractor '{extractor_name}' not found. Available: {list(self._extractors.keys())}"
            )

        return self._extractors[extractor_name](**kwargs)

    def get_available_parsers(self) -> List[str]:
        """Get list of registered parser names"""
        return list(self._parsers.keys())

    def get_available_analyzers(self) -> List[str]:
        """Get list of registered analyzer names"""
        return list(self._analyzers.keys())

    def get_available_extractors(self) -> List[str]:
        """Get list of registered extractor names"""
        return list(self._extractors.keys())
