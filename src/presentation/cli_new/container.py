"""Dependency injection container for CLI"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

from rich.console import Console

from ..application.capability_analyzer import AnalyzeCapabilitiesUseCase
from ..application.csv_analysis import AnalyzeCSVStructureUseCase
from ..application.forecasting_use_cases import GenerateForecastUseCase
from ..application.import_data import AnalyzeDataSourceUseCase, ImportDataUseCase
from ..application.multi_project_import import ProcessMultipleDataSourcesUseCase
from ..application.process_health_use_cases import (
    AnalyzeAgingWorkItemsUseCase,
    AnalyzeBlockedItemsUseCase,
    AnalyzeLeadTimeUseCase,
    AnalyzeSprintHealthUseCase,
    AnalyzeWorkInProgressUseCase,
)
from ..application.style_service import StyleService
from ..application.use_cases import (
    AnalyzeHistoricalDataUseCase,
    CalculateRemainingWorkUseCase,
    CalculateVelocityUseCase,
    RunMonteCarloSimulationUseCase,
)
from ..application.velocity_prediction_use_cases import (
    ApplyVelocityAdjustmentsUseCase,
    CreateVelocityScenarioUseCase,
    GenerateScenarioComparisonUseCase,
)
from ..infrastructure.data_source_factory import DefaultDataSourceFactory
from ..infrastructure.forecasting_model_factory import DefaultModelFactory
from ..infrastructure.repositories import (
    FileConfigRepository,
    InMemoryIssueRepository,
    InMemorySprintRepository,
)
from ..report_generator import HTMLReportGenerator
from ..multi_report_generator import MultiProjectReportGenerator

logger = logging.getLogger(__name__)


class CLIContainer:
    """Dependency injection container for CLI application"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize container
        
        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self._instances: Dict[str, Any] = {}
        self._factories: Dict[str, Any] = {}
        
        # Initialize core dependencies
        self._initialize_repositories()
        self._initialize_factories()
        self._initialize_services()
        self._initialize_use_cases()
        self._initialize_generators()
    
    def _initialize_repositories(self):
        """Initialize repository instances"""
        # Use in-memory repositories for now
        self._instances['issue_repo'] = InMemoryIssueRepository()
        self._instances['sprint_repo'] = InMemorySprintRepository()
        self._instances['config_repo'] = FileConfigRepository(Path.home() / ".sprint-radar")
        
        logger.debug("Initialized repositories")
    
    def _initialize_factories(self):
        """Initialize factory instances"""
        self._instances['data_source_factory'] = DefaultDataSourceFactory()
        self._instances['model_factory'] = DefaultModelFactory()
        
        logger.debug("Initialized factories")
    
    def _initialize_services(self):
        """Initialize service instances"""
        # Style service with repository injection
        from ..infrastructure.theme_repository import FileThemeRepository
        theme_repo = FileThemeRepository(Path(__file__).parent.parent / "themes")
        
        from ..infrastructure.style_generator import DefaultStyleGenerator
        style_generator = DefaultStyleGenerator()
        
        self._instances['style_service'] = StyleService(
            theme_repository=theme_repo,
            style_generator=style_generator
        )
        
        logger.debug("Initialized services")
    
    def _initialize_use_cases(self):
        """Initialize use case instances"""
        # Get repositories
        issue_repo = self._instances['issue_repo']
        sprint_repo = self._instances['sprint_repo']
        config_repo = self._instances['config_repo']
        
        # Get factories
        data_source_factory = self._instances['data_source_factory']
        model_factory = self._instances['model_factory']
        
        # Import/Export use cases
        self._instances['import_use_case'] = ImportDataUseCase(
            data_source_factory=data_source_factory,
            issue_repo=issue_repo,
            sprint_repo=sprint_repo,
            config_repo=config_repo
        )
        
        self._instances['analyze_use_case'] = AnalyzeDataSourceUseCase(
            data_source_factory
        )
        
        self._instances['csv_analyze_use_case'] = AnalyzeCSVStructureUseCase()
        
        self._instances['multi_project_use_case'] = ProcessMultipleDataSourcesUseCase(
            data_source_factory=data_source_factory,
            csv_analyzer=self._instances['csv_analyze_use_case']
        )
        
        # Core analysis use cases
        self._instances['velocity_use_case'] = CalculateVelocityUseCase(
            issue_repo, sprint_repo
        )
        
        self._instances['remaining_work_use_case'] = CalculateRemainingWorkUseCase(
            issue_repo
        )
        
        self._instances['historical_data_use_case'] = AnalyzeHistoricalDataUseCase(
            issue_repo, sprint_repo
        )
        
        self._instances['simulation_use_case'] = RunMonteCarloSimulationUseCase()
        
        # Forecasting use cases
        self._instances['forecast_use_case'] = GenerateForecastUseCase(
            model_factory=model_factory,
            simulation_use_case=self._instances['simulation_use_case']
        )
        
        # Velocity prediction use cases
        self._instances['velocity_adjustment_use_case'] = ApplyVelocityAdjustmentsUseCase()
        self._instances['velocity_scenario_use_case'] = CreateVelocityScenarioUseCase()
        self._instances['scenario_comparison_use_case'] = GenerateScenarioComparisonUseCase()
        
        # Process health use cases
        self._instances['aging_use_case'] = AnalyzeAgingWorkItemsUseCase(issue_repo)
        self._instances['wip_use_case'] = AnalyzeWorkInProgressUseCase(issue_repo)
        self._instances['sprint_health_use_case'] = AnalyzeSprintHealthUseCase(
            issue_repo, sprint_repo
        )
        self._instances['blocked_use_case'] = AnalyzeBlockedItemsUseCase(issue_repo)
        self._instances['lead_time_use_case'] = AnalyzeLeadTimeUseCase(issue_repo)
        
        # Capability analyzer
        self._instances['capability_analyzer'] = AnalyzeCapabilitiesUseCase()
        
        logger.debug("Initialized use cases")
    
    def _initialize_generators(self):
        """Initialize report generators"""
        self._instances['report_generator'] = HTMLReportGenerator(
            self._instances['style_service']
        )
        
        self._instances['multi_report_generator'] = MultiProjectReportGenerator(
            style_service=self._instances['style_service'],
            single_report_generator=self._instances['report_generator']
        )
        
        logger.debug("Initialized generators")
    
    def get(self, key: str) -> Any:
        """Get a dependency by key
        
        Args:
            key: Dependency key
            
        Returns:
            Dependency instance
            
        Raises:
            KeyError: If dependency not found
        """
        if key not in self._instances:
            raise KeyError(f"Dependency '{key}' not found in container")
        
        return self._instances[key]
    
    def get_all(self) -> Dict[str, Any]:
        """Get all dependencies
        
        Returns:
            Dictionary of all dependencies
        """
        return self._instances.copy()
    
    def register(self, key: str, instance: Any):
        """Register a custom dependency
        
        Args:
            key: Dependency key
            instance: Dependency instance
        """
        self._instances[key] = instance
        logger.debug(f"Registered custom dependency: {key}")
    
    def create_command_context(self, args: Any) -> 'CommandContext':
        """Create a command context with all dependencies
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Command context
        """
        from .commands import CommandContext
        
        return CommandContext(
            args=args,
            config={},  # Would load from config file
            dependencies=self.get_all()
        )