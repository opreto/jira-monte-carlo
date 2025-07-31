"""Forecast command for CLI"""

from typing import Optional, List
from rich.console import Console
from rich.table import Table

from .base import Command, CommandContext, CommandResult
from ...domain.entities import SimulationConfig
from ...domain.forecasting import ModelType, MonteCarloConfiguration


class ForecastCommand(Command):
    """Command to run forecasting simulations"""
    
    def __init__(self, console: Optional[Console] = None):
        super().__init__(
            name="forecast",
            description="Run Monte Carlo simulations for project forecasting"
        )
        self.console = console or Console()
    
    def validate(self, context: CommandContext) -> Optional[str]:
        """Validate forecast arguments"""
        args = context.args
        
        # Check if we have data to forecast
        if 'issues' not in context.dependencies:
            return "No data imported. Please run import command first."
        
        # Validate remaining work
        if args.remaining_work is not None and args.remaining_work < 0:
            return "Remaining work must be non-negative"
        
        # Validate confidence levels
        if args.confidence_levels:
            for level in args.confidence_levels:
                if not 0 < level < 100:
                    return f"Invalid confidence level: {level}. Must be between 0 and 100."
        
        # Validate number of simulations
        if args.simulations < 100:
            return "Number of simulations must be at least 100"
        
        return None
    
    def execute(self, context: CommandContext) -> CommandResult:
        """Execute forecasting simulation"""
        args = context.args
        
        # Get dependencies
        velocity_use_case = context.get_dependency('velocity_use_case')
        remaining_work_use_case = context.get_dependency('remaining_work_use_case')
        simulation_use_case = context.get_dependency('simulation_use_case')
        forecast_use_case = context.get_dependency('forecast_use_case')
        
        # Get imported data
        issues = context.dependencies.get('issues', [])
        velocity_metrics = context.dependencies.get('velocity_metrics')
        
        # Calculate velocity if not already done
        if not velocity_metrics:
            self.console.print("\n[yellow]Calculating historical velocity...[/yellow]")
            velocity_metrics = velocity_use_case.execute(
                args.lookback_sprints,
                args.velocity_field
            )
            context.dependencies['velocity_metrics'] = velocity_metrics
            
            # Display velocity metrics
            self._show_velocity_metrics(velocity_metrics)
        
        # Calculate remaining work
        self.console.print("\n[yellow]Calculating remaining work...[/yellow]")
        
        if args.remaining_work is not None:
            # Use provided value
            remaining_work = float(args.remaining_work)
            self.console.print(
                f"[green]Using provided remaining work: {remaining_work:.1f} {args.velocity_field}[/green]"
            )
        else:
            # Calculate from data
            remaining_items = remaining_work_use_case.execute(
                done_statuses=args.done_status,
                velocity_field=args.velocity_field
            )
            remaining_work = remaining_items
            self.console.print(
                f"[green]Calculated remaining work: {remaining_work:.1f} {args.velocity_field}[/green]"
            )
        
        # Prepare simulation configuration
        monte_carlo_config = MonteCarloConfiguration(
            num_simulations=args.simulations,
            confidence_levels=args.confidence_levels or [50, 70, 85, 95],
            use_historical_pattern=not args.no_pattern,
            min_velocity_factor=args.min_velocity_factor,
            max_velocity_factor=args.max_velocity_factor
        )
        
        # Create simulation config
        simulation_config = SimulationConfig(
            remaining_work=remaining_work,
            sprint_length=args.sprint_length,
            team_capacity=1.0,  # Not used in current implementation
            confidence_levels=monte_carlo_config.confidence_levels,
            num_simulations=monte_carlo_config.num_simulations
        )
        
        # Run simulation
        self.console.print(
            f"\n[yellow]Running {args.simulations:,} Monte Carlo simulations...[/yellow]"
        )
        
        # Execute forecast
        forecast_result = forecast_use_case.execute(
            project_name=args.project_name or "Project",
            issues=issues,
            historical_data=context.dependencies.get('historical_data'),
            simulation_config=simulation_config,
            velocity_metrics=velocity_metrics,
            model_type=ModelType.MONTE_CARLO,
            monte_carlo_config=monte_carlo_config,
            velocity_scenarios=context.dependencies.get('velocity_scenarios')
        )
        
        # Store results
        context.dependencies['forecast_result'] = forecast_result
        context.dependencies['simulation_config'] = simulation_config
        context.dependencies['remaining_work'] = remaining_work
        
        # Display forecast summary
        self._show_forecast_summary(forecast_result, args.project_name)
        
        return CommandResult(
            success=True,
            message="Forecast completed successfully",
            data={
                'forecast_result': forecast_result,
                'simulation_config': simulation_config,
                'velocity_metrics': velocity_metrics,
                'remaining_work': remaining_work
            }
        )
    
    def _show_velocity_metrics(self, velocity_metrics):
        """Display velocity metrics in a table"""
        table = Table(title="Historical Velocity Analysis")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Average Velocity", f"{velocity_metrics.average:.1f}")
        table.add_row("Median Velocity", f"{velocity_metrics.median:.1f}")
        table.add_row("Standard Deviation", f"{velocity_metrics.std_dev:.1f}")
        table.add_row("Min Velocity", f"{velocity_metrics.min:.1f}")
        table.add_row("Max Velocity", f"{velocity_metrics.max:.1f}")
        table.add_row("Sprint Count", str(velocity_metrics.sprint_count))
        
        if velocity_metrics.trend:
            trend_symbol = "↑" if velocity_metrics.trend > 0 else "↓"
            table.add_row("Trend", f"{trend_symbol} {velocity_metrics.trend:.1%}")
        
        self.console.print(table)
    
    def _show_forecast_summary(self, forecast_result, project_name: Optional[str]):
        """Display forecast summary"""
        self.console.print("\n[bold green]Forecast Summary[/bold green]")
        
        if project_name:
            self.console.print(f"Project: {project_name}")
        
        # Get simulation result
        sim_result = forecast_result.simulation_results.get(ModelType.MONTE_CARLO)
        if not sim_result:
            return
        
        # Display confidence intervals
        table = Table(title="Completion Forecast")
        table.add_column("Confidence Level", style="cyan")
        table.add_column("Sprints", style="yellow")
        table.add_column("Completion Date", style="green")
        
        for confidence, sprints in sim_result.percentiles.items():
            # Calculate date (simplified - would use proper date calculation)
            date_str = f"Sprint +{int(sprints)}"
            table.add_row(
                f"{int(confidence * 100)}%",
                f"{sprints:.0f}",
                date_str
            )
        
        self.console.print(table)