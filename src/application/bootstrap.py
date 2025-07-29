"""Bootstrap module for dependency injection and application initialization"""
from pathlib import Path
from typing import Optional

from ..domain.data_sources import DataSourceFactory
from ..domain.forecasting import ForecastingModelFactory
from ..infrastructure.csv_analyzer import SmartCSVParser
from ..infrastructure.csv_parser import JiraCSVParser
from ..infrastructure.data_source_factory import DefaultDataSourceFactory
from ..infrastructure.forecasting_model_factory import DefaultModelFactory
from ..infrastructure.repositories import (
    EnhancedSprintExtractor,
    FileConfigRepository,
    InMemoryIssueRepository,
    InMemorySprintRepository,
)
from ..infrastructure.theme_repository import FileThemeRepository
from ..presentation.style_generator import StyleGenerator
from .csv_adapters import EnhancedSprintExtractorAdapter
from .csv_processing_factory import CSVProcessingFactory
from .clean_style_service import CleanStyleService
from .style_service_factory import StyleServiceFactory


class ApplicationBootstrap:
    """
    Bootstrap class to wire up all dependencies following clean architecture.
    
    This class is the only place where infrastructure components are imported
    and wired together. All other parts of the application should use the
    abstractions provided by this bootstrap process.
    """
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".jira-monte-carlo"
        self._csv_processing_factory = None
        self._style_service = None
        self._forecasting_factory = None
        self._data_source_factory = None
    
    def get_csv_processing_factory(self) -> CSVProcessingFactory:
        """Get or create CSV processing factory with all implementations registered"""
        if self._csv_processing_factory is None:
            factory = CSVProcessingFactory()
            
            # Register parsers
            factory.register_parser("jira", JiraCSVParser, set_as_default=True)
            # Future: factory.register_parser("linear", LinearCSVParser)
            
            # Register analyzers
            factory.register_analyzer("smart", SmartCSVParser, set_as_default=True)
            
            # Register extractors
            # Note: We use the adapter to make infrastructure comply with interface
            factory.register_extractor("enhanced", EnhancedSprintExtractorAdapter, set_as_default=True)
            
            self._csv_processing_factory = factory
        
        return self._csv_processing_factory
    
    def get_style_service(self) -> CleanStyleService:
        """Get or create style service with proper dependencies"""
        if self._style_service is None:
            factory = StyleServiceFactory()
            factory.register_theme_repository(FileThemeRepository)
            factory.register_style_generator(StyleGenerator)
            self._style_service = factory.create(self.config_dir)
        
        return self._style_service
    
    def get_forecasting_factory(self) -> ForecastingModelFactory:
        """Get or create forecasting model factory"""
        if self._forecasting_factory is None:
            self._forecasting_factory = DefaultModelFactory()
        
        return self._forecasting_factory
    
    def get_data_source_factory(self) -> DataSourceFactory:
        """Get or create data source factory"""
        if self._data_source_factory is None:
            self._data_source_factory = DefaultDataSourceFactory()
        
        return self._data_source_factory
    
    def create_config_repository(self):
        """Create configuration repository"""
        return FileConfigRepository(self.config_dir)
    
    def create_issue_repository(self):
        """Create issue repository"""
        return InMemoryIssueRepository()
    
    def create_sprint_repository(self):
        """Create sprint repository"""
        return InMemorySprintRepository()
    
    @staticmethod
    def create_default() -> "ApplicationBootstrap":
        """Create bootstrap with default configuration"""
        return ApplicationBootstrap()