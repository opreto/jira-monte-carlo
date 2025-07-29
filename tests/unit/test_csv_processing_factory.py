"""Tests for CSV processing factory"""

import pytest

from src.application.csv_processing_factory import CSVProcessingFactory
from src.domain.csv_processing import CSVAnalyzer, CSVParser, SprintExtractor
from src.domain.exceptions import ConfigurationError


class MockParser(CSVParser):
    """Mock parser for testing"""

    def parse(self, df, field_mapping):
        return []


class MockAnalyzer(CSVAnalyzer):
    """Mock analyzer for testing"""

    def analyze_structure(self, file_path):
        return None

    def extract_sprints(self, df, field_mapping):
        return []

    def extract_velocity(self, df, field_mapping, config):
        return None


class MockExtractor(SprintExtractor):
    """Mock extractor for testing"""

    def extract_from_issues(self, issues):
        return []

    def extract_from_dataframe(self, df, sprint_field, velocity_field="Story Points"):
        return []


class NotAParser:
    """Class that doesn't implement CSVParser"""

    pass


class TestCSVProcessingFactory:
    """Test CSV processing factory"""

    def test_register_parser(self):
        """Test registering a parser"""
        factory = CSVProcessingFactory()
        factory.register_parser("test", MockParser)

        assert "test" in factory.get_available_parsers()
        assert factory._default_parser == "test"

    def test_register_invalid_parser(self):
        """Test registering invalid parser raises error"""
        factory = CSVProcessingFactory()

        with pytest.raises(TypeError, match="must implement CSVParser interface"):
            factory.register_parser("invalid", NotAParser)

    def test_create_parser(self):
        """Test creating a parser instance"""
        factory = CSVProcessingFactory()
        factory.register_parser("test", MockParser)

        parser = factory.create_parser()
        assert isinstance(parser, MockParser)

    def test_create_parser_by_name(self):
        """Test creating a parser by name"""
        factory = CSVProcessingFactory()
        factory.register_parser("parser1", MockParser)
        factory.register_parser("parser2", MockParser, set_as_default=True)

        parser = factory.create_parser("parser1")
        assert isinstance(parser, MockParser)

    def test_create_parser_not_registered(self):
        """Test creating parser when none registered"""
        factory = CSVProcessingFactory()

        with pytest.raises(ConfigurationError, match="No CSV parser registered"):
            factory.create_parser()

    def test_create_parser_unknown_name(self):
        """Test creating parser with unknown name"""
        factory = CSVProcessingFactory()
        factory.register_parser("test", MockParser)

        with pytest.raises(ConfigurationError, match="CSV parser 'unknown' not found"):
            factory.create_parser("unknown")

    def test_register_analyzer(self):
        """Test registering an analyzer"""
        factory = CSVProcessingFactory()
        factory.register_analyzer("test", MockAnalyzer)

        assert "test" in factory.get_available_analyzers()
        assert factory._default_analyzer == "test"

    def test_create_analyzer(self):
        """Test creating an analyzer instance"""
        factory = CSVProcessingFactory()
        factory.register_analyzer("test", MockAnalyzer)

        analyzer = factory.create_analyzer()
        assert isinstance(analyzer, MockAnalyzer)

    def test_register_extractor(self):
        """Test registering an extractor"""
        factory = CSVProcessingFactory()
        factory.register_extractor("test", MockExtractor)

        assert "test" in factory.get_available_extractors()
        assert factory._default_extractor == "test"

    def test_create_extractor(self):
        """Test creating an extractor instance"""
        factory = CSVProcessingFactory()
        factory.register_extractor("test", MockExtractor)

        extractor = factory.create_extractor()
        assert isinstance(extractor, MockExtractor)

    def test_multiple_registrations(self):
        """Test registering multiple implementations"""
        factory = CSVProcessingFactory()
        factory.register_parser("parser1", MockParser)
        factory.register_parser("parser2", MockParser, set_as_default=True)

        assert len(factory.get_available_parsers()) == 2
        assert factory._default_parser == "parser2"

    def test_create_with_kwargs(self):
        """Test creating instances with kwargs"""

        class ConfigurableParser(CSVParser):
            def __init__(self, config_value=None):
                self.config_value = config_value

            def parse(self, df, field_mapping):
                return []

        factory = CSVProcessingFactory()
        factory.register_parser("configurable", ConfigurableParser)

        parser = factory.create_parser(config_value="test_value")
        assert parser.config_value == "test_value"
