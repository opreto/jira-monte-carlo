"""Use cases for forecasting using the model abstraction"""

import logging
from typing import Optional

from ..domain.forecasting import (
    ForecastingModel,
    ForecastingModelFactory,
    ForecastResult,
    ModelConfiguration,
    ModelType,
)
from ..domain.repositories import IssueRepository
from ..domain.value_objects import VelocityMetrics

logger = logging.getLogger(__name__)


class GenerateForecastUseCase:
    """Generate forecast using configurable forecasting model"""

    def __init__(self, forecasting_model: ForecastingModel, issue_repo: Optional[IssueRepository] = None):
        """
        Initialize with a specific forecasting model

        Args:
            forecasting_model: The model to use for forecasting
            issue_repo: Optional repository for additional context
        """
        self.forecasting_model = forecasting_model
        self.issue_repo = issue_repo

    def execute(
        self, remaining_work: float, velocity_metrics: VelocityMetrics, config: ModelConfiguration
    ) -> ForecastResult:
        """
        Generate forecast for remaining work

        Args:
            remaining_work: Amount of work remaining
            velocity_metrics: Historical velocity statistics
            config: Model configuration

        Returns:
            ForecastResult with predictions
        """
        # Validate inputs
        errors = self.forecasting_model.validate_inputs(remaining_work, velocity_metrics)
        if errors:
            raise ValueError(f"Invalid inputs for forecasting: {'; '.join(errors)}")

        # Validate configuration
        config_errors = config.validate()
        if config_errors:
            raise ValueError(f"Invalid configuration: {'; '.join(config_errors)}")

        # Log forecasting details
        model_info = self.forecasting_model.get_model_info()
        logger.info(
            f"Generating forecast using {model_info.name} "
            f"for {remaining_work:.1f} units of work "
            f"with velocity avg={velocity_metrics.average:.1f}"
        )

        # Generate forecast
        result = self.forecasting_model.forecast(remaining_work, velocity_metrics, config)

        # Log summary results
        logger.info(f"Forecast complete: expected completion in " f"{result.expected_sprints:.1f} sprints")

        return result


class CompareForecastModelsUseCase:
    """Compare forecasts from multiple models"""

    def __init__(self, model_factory: ForecastingModelFactory):
        self.model_factory = model_factory

    def execute(
        self, remaining_work: float, velocity_metrics: VelocityMetrics, model_types: Optional[list[ModelType]] = None
    ) -> dict[ModelType, ForecastResult]:
        """
        Run multiple models and compare results

        Args:
            remaining_work: Amount of work remaining
            velocity_metrics: Historical velocity statistics
            model_types: List of models to compare (None = all available)

        Returns:
            Dictionary mapping model type to forecast result
        """
        results = {}

        # Get models to compare
        if model_types is None:
            available_models = self.model_factory.get_available_models()
            model_types = [info.model_type for info in available_models]

        # Run each model
        for model_type in model_types:
            try:
                # Create model with default config
                model = self.model_factory.create(model_type)
                config = self.model_factory.get_default_config(model_type)

                # Generate forecast
                use_case = GenerateForecastUseCase(model)
                result = use_case.execute(remaining_work, velocity_metrics, config)
                results[model_type] = result

            except Exception as e:
                logger.error(f"Failed to run {model_type.value} model: {str(e)}")
                continue

        return results
