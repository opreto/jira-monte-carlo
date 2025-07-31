"""Report generation command for CLI"""

from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from rich.console import Console

from .base import Command, CommandContext, CommandResult


class ReportCommand(Command):
    """Command to generate HTML reports"""
    
    def __init__(self, console: Optional[Console] = None):
        super().__init__(
            name="report",
            description="Generate HTML reports from forecast results"
        )
        self.console = console or Console()
    
    def validate(self, context: CommandContext) -> Optional[str]:
        """Validate report generation arguments"""
        # Check if we have forecast results
        if 'forecast_result' not in context.dependencies:
            return "No forecast results available. Please run forecast command first."
        
        args = context.args
        
        # Validate output path if specified
        if args.output:
            output_path = Path(args.output)
            if output_path.exists() and output_path.is_dir():
                return f"Output path is a directory: {args.output}"
            
            # Check if parent directory exists
            if not output_path.parent.exists():
                return f"Output directory does not exist: {output_path.parent}"
        
        return None
    
    def execute(self, context: CommandContext) -> CommandResult:
        """Execute report generation"""
        args = context.args
        
        # Get dependencies
        report_generator = context.get_dependency('report_generator')
        style_service = context.get_dependency('style_service')
        process_health_use_case = context.get_dependency('process_health_use_case')
        capability_analyzer = context.get_dependency('capability_analyzer')
        
        # Get data from context
        forecast_result = context.dependencies['forecast_result']
        simulation_config = context.dependencies['simulation_config']
        velocity_metrics = context.dependencies['velocity_metrics']
        issues = context.dependencies.get('issues', [])
        sprints = context.dependencies.get('sprints', [])
        remaining_work = context.dependencies.get('remaining_work', 0)
        
        # Determine output path
        if args.output:
            output_path = Path(args.output)
        else:
            # Default to reports directory
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            project_name = args.project_name or "project"
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_name)
            output_path = reports_dir / f"{safe_name}_report_{timestamp}.html"
        
        self.console.print(f"\n[yellow]Generating report: {output_path}[/yellow]")
        
        try:
            # Analyze process health if requested
            process_health_metrics = None
            if not args.no_health:
                self.console.print("[yellow]Analyzing process health metrics...[/yellow]")
                
                # Run all process health analyses
                health_results = self._analyze_process_health(
                    context, issues, sprints, args
                )
                process_health_metrics = health_results
            
            # Analyze reporting capabilities
            self.console.print("[yellow]Analyzing reporting capabilities...[/yellow]")
            capabilities = capability_analyzer.execute(issues, sprints)
            
            # Get charts data
            charts_data = self._prepare_charts_data(forecast_result, velocity_metrics)
            
            # Generate styles
            theme = style_service.get_theme(args.theme or 'opreto')
            styles = style_service.generate_styles(theme)
            
            # Prepare report context
            report_context = {
                'project_name': args.project_name,
                'generation_date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'forecast_result': forecast_result,
                'simulation_config': simulation_config,
                'velocity_metrics': velocity_metrics,
                'remaining_work': remaining_work,
                'velocity_field': args.velocity_field,
                'percentiles': forecast_result.simulation_results[0].percentiles,
                'charts': charts_data,
                'process_health_metrics': process_health_metrics,
                'process_health_charts': {},  # Would be populated by chart generator
                'reporting_capabilities': capabilities,
                'num_simulations': simulation_config.num_simulations,
                'styles': styles,
                'model_info': forecast_result.model_info,
                'summary_stats': self._prepare_summary_stats(forecast_result),
                'jira_url': args.jira_url,
                'jql_query': getattr(args, 'jql_query', None)
            }
            
            # Handle scenario reports if applicable
            if 'velocity_scenarios' in context.dependencies:
                report_context['velocity_scenarios'] = context.dependencies['velocity_scenarios']
                report_context['scenario_comparison'] = context.dependencies.get('scenario_comparison')
            
            # Generate report HTML
            html_content = report_generator.generate(report_context)
            
            # Write to file
            output_path.write_text(html_content, encoding='utf-8')
            
            self.console.print(f"[green]✓ Report generated: {output_path}[/green]")
            
            # Open in browser if requested
            if args.open_browser:
                import webbrowser
                webbrowser.open(f"file://{output_path.absolute()}")
            
            return CommandResult(
                success=True,
                message="Report generated successfully",
                data={
                    'output_path': str(output_path),
                    'report_context': report_context
                }
            )
            
        except Exception as e:
            return CommandResult(
                success=False,
                message=f"Report generation failed: {str(e)}",
                error=e
            )
    
    def _analyze_process_health(
        self, 
        context: CommandContext, 
        issues: list, 
        sprints: list,
        args: Any
    ) -> Dict[str, Any]:
        """Run all process health analyses"""
        results = {}
        
        # Get health analysis use cases
        aging_use_case = context.get_dependency('aging_use_case')
        wip_use_case = context.get_dependency('wip_use_case')
        sprint_health_use_case = context.get_dependency('sprint_health_use_case')
        blocked_use_case = context.get_dependency('blocked_use_case')
        lead_time_use_case = context.get_dependency('lead_time_use_case')
        
        # Run analyses
        try:
            results['aging_analysis'] = aging_use_case.execute(
                stale_threshold_days=args.stale_days,
                abandoned_threshold_days=args.abandoned_days
            )
        except Exception as e:
            self._logger.warning(f"Aging analysis failed: {e}")
        
        try:
            results['wip_analysis'] = wip_use_case.execute(
                wip_limits={}  # Would come from config
            )
        except Exception as e:
            self._logger.warning(f"WIP analysis failed: {e}")
        
        try:
            results['sprint_health'] = sprint_health_use_case.execute()
        except Exception as e:
            self._logger.warning(f"Sprint health analysis failed: {e}")
        
        try:
            results['blocked_items'] = blocked_use_case.execute()
        except Exception as e:
            self._logger.warning(f"Blocked items analysis failed: {e}")
        
        try:
            results['lead_time_analysis'] = lead_time_use_case.execute()
        except Exception as e:
            self._logger.warning(f"Lead time analysis failed: {e}")
        
        # Calculate overall health score
        results['health_score'] = self._calculate_health_score(results)
        results['health_score_breakdown'] = self._prepare_health_breakdown(results)
        
        return results
    
    def _prepare_charts_data(self, forecast_result, velocity_metrics) -> Dict[str, Any]:
        """Prepare data for charts"""
        # This would normally be done by chart generators
        # Simplified version for now
        return {
            'probability_distribution': {},
            'confidence_intervals': {},
            'velocity_trend': {},
            'forecast_timeline': {},
            'story_size_breakdown': {
                'pie': {},
                'bar': {}
            }
        }
    
    def _prepare_summary_stats(self, forecast_result) -> Dict[str, Any]:
        """Prepare summary statistics for report"""
        sim_result = forecast_result.simulation_results[0]
        
        return {
            '50% Confidence': {
                'sprints': sim_result.percentiles.get(0.5, 0),
                'date': 'TBD',  # Would calculate actual date
                'probability': 50,
                'class': 'optimistic'
            },
            '70% Confidence': {
                'sprints': sim_result.percentiles.get(0.7, 0),
                'date': 'TBD',
                'probability': 70,
                'class': 'likely'
            },
            '85% Confidence': {
                'sprints': sim_result.percentiles.get(0.85, 0),
                'date': 'TBD',
                'probability': 85,
                'class': 'conservative'
            },
            '95% Confidence': {
                'sprints': sim_result.percentiles.get(0.95, 0),
                'date': 'TBD',
                'probability': 95,
                'class': 'very-conservative'
            }
        }
    
    def _calculate_health_score(self, health_results: Dict[str, Any]) -> float:
        """Calculate overall health score from individual metrics"""
        # Simplified calculation
        scores = []
        
        if 'aging_analysis' in health_results:
            aging = health_results['aging_analysis']
            # Lower percentage of old items is better
            old_ratio = (aging.stale_count + aging.abandoned_count) / max(aging.total_items, 1)
            scores.append(1.0 - old_ratio)
        
        if 'wip_analysis' in health_results:
            wip = health_results['wip_analysis']
            # Being within WIP limits is good
            wip_score = 1.0 if not wip.items_over_limit else 0.5
            scores.append(wip_score)
        
        if 'sprint_health' in health_results:
            sprint = health_results['sprint_health']
            # Higher completion rate is better
            if hasattr(sprint, 'average_completion_rate'):
                scores.append(sprint.average_completion_rate)
        
        # Return average of all scores
        return sum(scores) / len(scores) if scores else 0.5
    
    def _prepare_health_breakdown(self, health_results: Dict[str, Any]) -> list:
        """Prepare health score breakdown for display"""
        breakdown = []
        
        # Add components based on available data
        if 'aging_analysis' in health_results:
            aging = health_results['aging_analysis']
            breakdown.append({
                'name': 'Work Item Age',
                'score': 1.0 - ((aging.stale_count + aging.abandoned_count) / max(aging.total_items, 1)),
                'description': 'Measures how fresh your work items are',
                'insights': [
                    f"{aging.fresh_count} fresh items (< 7 days)",
                    f"{aging.stale_count} stale items (> 30 days)",
                    f"{aging.abandoned_count} abandoned items (> 90 days)"
                ],
                'recommendations': self._get_aging_recommendations(aging)
            })
        
        return breakdown
    
    def _get_aging_recommendations(self, aging_analysis) -> list:
        """Get recommendations based on aging analysis"""
        recommendations = []
        
        if aging_analysis.abandoned_count > 0:
            recommendations.append(
                f"Review and close {aging_analysis.abandoned_count} abandoned items"
            )
        
        if aging_analysis.stale_count > aging_analysis.total_items * 0.2:
            recommendations.append(
                "Over 20% of items are stale - consider reviewing your backlog"
            )
        
        return recommendations