"""Domain interfaces and entities for forecasting models"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .value_objects import VelocityMetrics


class ModelType(Enum):
    """Supported forecasting model types"""

    MONTE_CARLO = "monte_carlo"
    PERT = "pert"
    LINEAR_REGRESSION = "linear_regression"
    MACHINE_LEARNING = "machine_learning"
    BAYESIAN = "bayesian"


@dataclass
class PredictionInterval:
    """Represents a prediction at a specific confidence level"""

    confidence_level: float  # 0.0 to 1.0
    lower_bound: float  # In sprints
    predicted_value: float  # In sprints
    upper_bound: float  # In sprints

    @property
    def range_width(self) -> float:
        """Width of the prediction interval"""
        return self.upper_bound - self.lower_bound


@dataclass
class ModelConfiguration:
    """Base configuration for all forecasting models"""

    confidence_levels: List[float] = field(default_factory=lambda: [0.5, 0.7, 0.85, 0.95])
    sprint_duration_days: int = 14

    def validate(self) -> List[str]:
        """Validate configuration and return list of errors"""
        errors = []
        if not self.confidence_levels:
            errors.append("At least one confidence level required")
        if any(cl < 0 or cl > 1 for cl in self.confidence_levels):
            errors.append("Confidence levels must be between 0 and 1")
        if self.sprint_duration_days <= 0:
            errors.append("Sprint duration must be positive")
        return errors


@dataclass
class MonteCarloConfiguration(ModelConfiguration):
    """Configuration specific to Monte Carlo simulation"""

    num_simulations: int = 10000
    use_historical_variance: bool = True
    variance_multiplier: float = 1.0  # For sensitivity analysis

    def validate(self) -> List[str]:
        errors = super().validate()
        if self.num_simulations < 100:
            errors.append("Number of simulations should be at least 100")
        if self.variance_multiplier <= 0:
            errors.append("Variance multiplier must be positive")
        return errors


@dataclass
class ForecastResult:
    """Unified result from any forecasting model"""

    # Core predictions
    prediction_intervals: List[PredictionInterval]
    expected_sprints: float
    expected_completion_date: datetime

    # Optional probability distribution
    probability_distribution: Optional[Dict[int, float]] = None  # sprints -> probability

    # Model-specific metadata
    model_type: ModelType = ModelType.MONTE_CARLO
    model_metadata: Dict[str, Any] = field(default_factory=dict)

    # Raw data for visualization (limited sample)
    sample_predictions: List[float] = field(default_factory=list)  # In sprints

    def get_prediction_at_confidence(self, confidence: float) -> Optional[PredictionInterval]:
        """Get prediction interval for specific confidence level"""
        for interval in self.prediction_intervals:
            if abs(interval.confidence_level - confidence) < 0.001:
                return interval
        return None

    def get_percentile(self, confidence: float) -> Optional[float]:
        """Get predicted sprints at confidence level (for backward compatibility)"""
        interval = self.get_prediction_at_confidence(confidence)
        return interval.predicted_value if interval else None


@dataclass
class ModelInfo:
    """Information about a forecasting model"""

    model_type: ModelType
    name: str
    description: str
    supports_probability_distribution: bool
    required_historical_periods: int  # Minimum historical data points needed
    configuration_class: type
    # Additional metadata for reports
    report_title: str = field(default="")  # e.g., "Monte Carlo Simulation Report"
    report_subtitle: str = field(default="")  # e.g., "Statistical forecasting using Monte Carlo method"
    methodology_description: str = field(default="")  # Brief description of how the model works

    def __post_init__(self):
        """Set default report metadata if not provided"""
        if not self.report_title:
            self.report_title = f"{self.name} Report"
        if not self.report_subtitle:
            self.report_subtitle = f"Forecasting using {self.name}"


class ForecastingModel(ABC):
    """Abstract interface for all forecasting models"""

    @abstractmethod
    def forecast(
        self, remaining_work: float, velocity_metrics: VelocityMetrics, config: ModelConfiguration
    ) -> ForecastResult:
        """
        Generate forecast for remaining work given velocity metrics

        Args:
            remaining_work: Amount of work remaining (story points, issues, etc.)
            velocity_metrics: Historical velocity statistics
            config: Model-specific configuration

        Returns:
            ForecastResult with predictions
        """
        pass

    @abstractmethod
    def get_model_info(self) -> ModelInfo:
        """Get information about this model"""
        pass

    @abstractmethod
    def validate_inputs(self, remaining_work: float, velocity_metrics: VelocityMetrics) -> List[str]:
        """
        Validate inputs are suitable for this model

        Returns:
            List of validation error messages (empty if valid)
        """
        pass

    def supports_confidence_level(self, confidence: float) -> bool:
        """Check if model supports a specific confidence level"""
        return True  # Most models support arbitrary confidence levels


class ForecastingModelFactory(ABC):
    """Factory for creating forecasting model instances"""

    @abstractmethod
    def create(self, model_type: ModelType, config: Optional[ModelConfiguration] = None) -> ForecastingModel:
        """Create a forecasting model instance"""
        pass

    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available forecasting models"""
        pass

    @abstractmethod
    def get_default_model(self) -> ForecastingModel:
        """Get the default forecasting model"""
        pass
