"""Factory implementation for forecasting models"""

import logging
from typing import Dict, List, Optional, Type

from ..domain.forecasting import (
    ForecastingModel,
    ForecastingModelFactory,
    ModelConfiguration,
    ModelInfo,
    ModelType,
    MonteCarloConfiguration,
)
from .monte_carlo_model import MonteCarloModel

logger = logging.getLogger(__name__)


class DefaultModelFactory(ForecastingModelFactory):
    """Default implementation of forecasting model factory"""

    def __init__(self):
        # Registry of available models
        self._models: Dict[ModelType, Type[ForecastingModel]] = {
            ModelType.MONTE_CARLO: MonteCarloModel,
            # Future models can be registered here
            # ModelType.PERT: PERTModel,
            # ModelType.LINEAR_REGRESSION: LinearRegressionModel,
        }

        # Default configurations for each model type
        self._default_configs: Dict[ModelType, ModelConfiguration] = {
            ModelType.MONTE_CARLO: MonteCarloConfiguration(),
        }

    def create(
        self, model_type: ModelType, config: Optional[ModelConfiguration] = None
    ) -> ForecastingModel:
        """Create a forecasting model instance"""
        if model_type not in self._models:
            raise ValueError(f"Unknown model type: {model_type}")

        model_class = self._models[model_type]
        model = model_class()

        # Log model creation
        logger.info(f"Created {model_type.value} forecasting model")

        return model

    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available forecasting models"""
        models = []
        for model_type, model_class in self._models.items():
            model_instance = model_class()
            models.append(model_instance.get_model_info())
        return models

    def get_default_model(self) -> ForecastingModel:
        """Get the default forecasting model"""
        return self.create(ModelType.MONTE_CARLO)

    def get_default_config(self, model_type: ModelType) -> ModelConfiguration:
        """Get default configuration for a model type"""
        return self._default_configs.get(model_type, ModelConfiguration())

    def register_model(
        self,
        model_type: ModelType,
        model_class: Type[ForecastingModel],
        default_config: Optional[ModelConfiguration] = None,
    ):
        """Register a new model type (for extensibility)"""
        self._models[model_type] = model_class
        if default_config:
            self._default_configs[model_type] = default_config
        logger.info(f"Registered new model type: {model_type.value}")
