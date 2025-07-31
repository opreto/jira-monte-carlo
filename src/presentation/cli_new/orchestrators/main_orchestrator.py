"""Main orchestrator for CLI commands"""

from typing import Optional, List
from rich.console import Console
import logging

from ..commands import Command, CommandContext, CommandResult, CompositeCommand
from ..commands.import_data import ImportDataCommand
from ..commands.forecast import ForecastCommand
from ..commands.report import ReportCommand
from ..container import CLIContainer

logger = logging.getLogger(__name__)


class MainOrchestrator:
    """Orchestrates the execution of CLI commands"""
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize orchestrator
        
        Args:
            console: Rich console for output
        """
        self.console = console or Console()
        self.container = CLIContainer(console)
        self._commands = self._initialize_commands()
    
    def _initialize_commands(self) -> dict:
        """Initialize all available commands
        
        Returns:
            Dictionary of command instances
        """
        return {
            'import': ImportDataCommand(self.console),
            'forecast': ForecastCommand(self.console),
            'report': ReportCommand(self.console)
        }
    
    def execute_full_workflow(self, args) -> CommandResult:
        """Execute the full workflow: import -> forecast -> report
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Combined result from all commands
        """
        # Create composite command for full workflow
        workflow = CompositeCommand(
            name="full_workflow",
            description="Complete Sprint Radar workflow"
        )
        
        # Add commands in order
        workflow.add_command(self._commands['import'])
        workflow.add_command(self._commands['forecast'])
        workflow.add_command(self._commands['report'])
        
        # Create context
        context = self.container.create_command_context(args)
        
        # Execute workflow
        return workflow.execute(context)
    
    def execute_import_only(self, args) -> CommandResult:
        """Execute only the import step
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Import command result
        """
        context = self.container.create_command_context(args)
        return self._commands['import'].execute(context)
    
    def execute_analysis_only(self, args) -> CommandResult:
        """Execute import and analysis without forecasting
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Analysis result
        """
        # Set analyze_only flag
        args.analyze_only = True
        
        context = self.container.create_command_context(args)
        return self._commands['import'].execute(context)
    
    def execute_multi_project(self, args, csv_paths: List[str]) -> CommandResult:
        """Execute multi-project workflow
        
        Args:
            args: Parsed command line arguments
            csv_paths: List of CSV file paths
            
        Returns:
            Multi-project result
        """
        # This will be implemented with a specialized orchestrator
        return CommandResult(
            success=False,
            message="Multi-project orchestration not yet implemented"
        )
    
    def execute_scenario_comparison(self, args) -> CommandResult:
        """Execute scenario comparison workflow
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Scenario comparison result
        """
        # Create workflow for scenario comparison
        workflow = CompositeCommand(
            name="scenario_workflow",
            description="Velocity scenario comparison"
        )
        
        # Import data
        workflow.add_command(self._commands['import'])
        
        # Run baseline forecast
        baseline_forecast = ForecastCommand(self.console)
        baseline_forecast.name = "baseline_forecast"
        workflow.add_command(baseline_forecast)
        
        # Apply velocity adjustments and run adjusted forecast
        # This would require additional commands for velocity adjustment
        
        # Generate comparison report
        workflow.add_command(self._commands['report'])
        
        context = self.container.create_command_context(args)
        return workflow.execute(context)
    
    def execute_command(self, command_name: str, args) -> CommandResult:
        """Execute a specific command by name
        
        Args:
            command_name: Name of the command to execute
            args: Parsed command line arguments
            
        Returns:
            Command result
        """
        if command_name not in self._commands:
            return CommandResult(
                success=False,
                message=f"Unknown command: {command_name}"
            )
        
        context = self.container.create_command_context(args)
        return self._commands[command_name].execute(context)