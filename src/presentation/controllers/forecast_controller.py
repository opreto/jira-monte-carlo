"""Forecast controller for presentation layer"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from .base import Controller
from ..models.requests import ForecastRequest
from ..models.responses import ForecastResponse
from ...domain.entities import SimulationConfig
from ...domain.forecasting import ModelType, MonteCarloConfiguration


class ForecastController(Controller[ForecastRequest, ForecastResponse]):
    """Controller for handling forecast operations"""
    
    def __init__(
        self,
        velocity_use_case,
        remaining_work_use_case,
        forecast_use_case,
        historical_data_use_case
    ):
        """Initialize forecast controller
        
        Args:
            velocity_use_case: Use case for velocity calculation
            remaining_work_use_case: Use case for remaining work calculation
            forecast_use_case: Use case for generating forecasts
            historical_data_use_case: Use case for historical data analysis
        """
        super().__init__("Forecast")
        self.velocity_use_case = velocity_use_case
        self.remaining_work_use_case = remaining_work_use_case
        self.forecast_use_case = forecast_use_case
        self.historical_data_use_case = historical_data_use_case
    
    def handle(self, request: ForecastRequest) -> ForecastResponse:
        """Handle forecast request
        
        Args:
            request: Forecast request model
            
        Returns:
            Forecast response model
        """
        try:
            # Calculate velocity metrics
            velocity_metrics = self.velocity_use_case.execute(
                request.lookback_sprints,
                request.velocity_field
            )
            
            # Calculate or use provided remaining work
            if request.remaining_work is not None:
                remaining_work = request.remaining_work
            else:
                remaining_work = self.remaining_work_use_case.execute(
                    done_statuses=request.done_statuses,
                    velocity_field=request.velocity_field
                )
            
            # Get historical data
            historical_data = self.historical_data_use_case.execute()
            
            # Create simulation configuration
            monte_carlo_config = MonteCarloConfiguration(
                num_simulations=request.simulations,
                confidence_levels=request.confidence_levels,
                use_historical_pattern=request.use_historical_pattern,
                min_velocity_factor=request.min_velocity_factor,
                max_velocity_factor=request.max_velocity_factor
            )
            
            simulation_config = SimulationConfig(
                remaining_work=remaining_work,
                sprint_length=request.sprint_length,
                team_capacity=1.0,
                confidence_levels=request.confidence_levels,
                num_simulations=request.simulations
            )
            
            # Run forecast
            forecast_result = self.forecast_use_case.execute(
                project_name=request.project_name or "Project",
                issues=[],  # Would come from context
                historical_data=historical_data,
                simulation_config=simulation_config,
                velocity_metrics=velocity_metrics,
                model_type=ModelType.MONTE_CARLO,
                monte_carlo_config=monte_carlo_config,
                velocity_scenarios=None
            )
            
            # Extract results
            sim_result = forecast_result.simulation_results[ModelType.MONTE_CARLO]
            
            # Calculate completion dates
            base_date = datetime.now()
            dates = self._calculate_completion_dates(
                sim_result.percentiles,
                request.sprint_length,
                base_date
            )
            
            # Build response
            response = ForecastResponse(
                success=True,
                project_name=request.project_name or "Project",
                remaining_work=remaining_work,
                velocity_field=request.velocity_field,
                percentile_50=int(sim_result.percentiles.get(0.5, 0)),
                percentile_70=int(sim_result.percentiles.get(0.7, 0)),
                percentile_85=int(sim_result.percentiles.get(0.85, 0)),
                percentile_95=int(sim_result.percentiles.get(0.95, 0)),
                completion_date_50=dates.get(50),
                completion_date_70=dates.get(70),
                completion_date_85=dates.get(85),
                completion_date_95=dates.get(95),
                average_velocity=velocity_metrics.average,
                median_velocity=velocity_metrics.median,
                velocity_std_dev=velocity_metrics.std_dev,
                velocity_trend=velocity_metrics.trend,
                simulations_run=request.simulations,
                model_type=ModelType.MONTE_CARLO.value
            )
            
            # Add confidence intervals
            response.confidence_intervals = self._build_confidence_intervals(
                sim_result.percentiles,
                request.sprint_length,
                base_date
            )
            
            # Add insights
            response.risk_assessment = self._assess_risk(
                velocity_metrics,
                sim_result.percentiles
            )
            response.recommendations = self._generate_recommendations(
                velocity_metrics,
                remaining_work,
                sim_result.percentiles
            )
            
            return response
            
        except Exception as e:
            self._logger.error(f"Forecast failed: {str(e)}")
            return ForecastResponse(
                success=False,
                project_name=request.project_name or "Project",
                remaining_work=0.0,
                velocity_field=request.velocity_field,
                percentile_50=0,
                percentile_70=0,
                percentile_85=0,
                percentile_95=0
            )
    
    def _calculate_completion_dates(
        self,
        percentiles: Dict[float, float],
        sprint_length: int,
        base_date: datetime
    ) -> Dict[int, datetime]:
        """Calculate completion dates for each confidence level
        
        Args:
            percentiles: Sprint percentiles
            sprint_length: Length of sprint in days
            base_date: Base date for calculation
            
        Returns:
            Dictionary of confidence level to completion date
        """
        dates = {}
        
        for confidence, sprints in percentiles.items():
            confidence_int = int(confidence * 100)
            days_to_complete = int(sprints * sprint_length)
            completion_date = base_date + timedelta(days=days_to_complete)
            dates[confidence_int] = completion_date
        
        return dates
    
    def _build_confidence_intervals(
        self,
        percentiles: Dict[float, float],
        sprint_length: int,
        base_date: datetime
    ) -> Dict[int, Dict[str, any]]:
        """Build detailed confidence interval information
        
        Args:
            percentiles: Sprint percentiles
            sprint_length: Length of sprint in days
            base_date: Base date for calculation
            
        Returns:
            Confidence interval details
        """
        intervals = {}
        
        for confidence, sprints in percentiles.items():
            confidence_int = int(confidence * 100)
            days = int(sprints * sprint_length)
            date = base_date + timedelta(days=days)
            
            intervals[confidence_int] = {
                'sprints': int(sprints),
                'days': days,
                'date': date.strftime('%Y-%m-%d'),
                'weeks': round(days / 7, 1),
                'months': round(days / 30, 1)
            }
        
        return intervals
    
    def _assess_risk(
        self,
        velocity_metrics,
        percentiles: Dict[float, float]
    ) -> str:
        """Assess project risk based on metrics
        
        Args:
            velocity_metrics: Velocity metrics
            percentiles: Sprint percentiles
            
        Returns:
            Risk assessment message
        """
        # Calculate spread between optimistic and pessimistic
        spread = percentiles.get(0.95, 0) - percentiles.get(0.5, 0)
        relative_spread = spread / percentiles.get(0.5, 1) if percentiles.get(0.5, 0) > 0 else 0
        
        # Assess based on spread and velocity stability
        if relative_spread > 0.5 or velocity_metrics.std_dev > velocity_metrics.average * 0.3:
            return "High uncertainty - Wide spread between optimistic and pessimistic estimates"
        elif relative_spread > 0.3 or velocity_metrics.std_dev > velocity_metrics.average * 0.2:
            return "Moderate uncertainty - Some variability in estimates"
        else:
            return "Low uncertainty - Consistent velocity and narrow estimate range"
    
    def _generate_recommendations(
        self,
        velocity_metrics,
        remaining_work: float,
        percentiles: Dict[float, float]
    ) -> List[str]:
        """Generate recommendations based on analysis
        
        Args:
            velocity_metrics: Velocity metrics
            remaining_work: Remaining work
            percentiles: Sprint percentiles
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check velocity stability
        if velocity_metrics.std_dev > velocity_metrics.average * 0.3:
            recommendations.append(
                "High velocity variability detected. Consider stabilizing team composition and workload."
            )
        
        # Check if trending down
        if velocity_metrics.trend and velocity_metrics.trend < -0.1:
            recommendations.append(
                "Velocity is trending downward. Investigate potential causes such as technical debt or team morale."
            )
        
        # Check remaining work size
        if remaining_work > velocity_metrics.average * 20:
            recommendations.append(
                "Large amount of remaining work. Consider breaking into smaller milestones for better predictability."
            )
        
        # Check estimate spread
        spread = percentiles.get(0.95, 0) - percentiles.get(0.5, 0)
        if spread > 10:
            recommendations.append(
                "Wide estimate range suggests high uncertainty. Focus on reducing unknowns and risks."
            )
        
        return recommendations