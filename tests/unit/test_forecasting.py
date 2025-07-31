"""Tests for forecasting model abstraction"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from src.application.forecasting_use_cases import (
    CompareForecastModelsUseCase,
    GenerateForecastUseCase,
)
from src.domain.forecasting import (
    ForecastingModel,
    ForecastResult,
    ModelConfiguration,
    ModelInfo,
    ModelType,
    MonteCarloConfiguration,
    PredictionInterval,
)
from src.domain.value_objects import VelocityMetrics
from src.infrastructure.forecasting_model_factory import DefaultModelFactory
from src.infrastructure.monte_carlo_model import MonteCarloModel


class TestModelConfiguration:
    def test_base_configuration_defaults(self):
        config = ModelConfiguration()
        assert config.confidence_levels == [0.5, 0.7, 0.85, 0.95]
        assert config.sprint_duration_days == 14

    def test_base_configuration_validation(self):
        # Valid config
        config = ModelConfiguration()
        errors = config.validate()
        assert len(errors) == 0

        # Invalid confidence levels
        config = ModelConfiguration(confidence_levels=[])
        errors = config.validate()
        assert "At least one confidence level required" in errors

        config = ModelConfiguration(confidence_levels=[1.5, -0.1])
        errors = config.validate()
        assert "Confidence levels must be between 0 and 1" in errors

        # Invalid sprint duration
        config = ModelConfiguration(sprint_duration_days=0)
        errors = config.validate()
        assert "Sprint duration must be positive" in errors

    def test_monte_carlo_configuration(self):
        config = MonteCarloConfiguration(num_simulations=5000, variance_multiplier=1.5)
        assert config.num_simulations == 5000
        assert config.variance_multiplier == 1.5
        assert config.use_historical_variance is True

    def test_monte_carlo_configuration_validation(self):
        # Too few simulations
        config = MonteCarloConfiguration(num_simulations=50)
        errors = config.validate()
        assert "Number of simulations should be at least 100" in errors

        # Invalid variance multiplier
        config = MonteCarloConfiguration(variance_multiplier=-1)
        errors = config.validate()
        assert "Variance multiplier must be positive" in errors


class TestPredictionInterval:
    def test_prediction_interval_creation(self):
        interval = PredictionInterval(
            confidence_level=0.85, lower_bound=2.0, predicted_value=3.0, upper_bound=5.0
        )
        assert interval.confidence_level == 0.85
        assert interval.lower_bound == 2.0
        assert interval.predicted_value == 3.0
        assert interval.upper_bound == 5.0

    def test_range_width(self):
        interval = PredictionInterval(
            confidence_level=0.85, lower_bound=2.0, predicted_value=3.0, upper_bound=5.0
        )
        assert interval.range_width == 3.0


class TestForecastResult:
    def test_forecast_result_creation(self):
        intervals = [
            PredictionInterval(0.5, 2.0, 3.0, 4.0),
            PredictionInterval(0.85, 2.0, 4.0, 6.0),
        ]
        result = ForecastResult(
            prediction_intervals=intervals,
            expected_sprints=3.5,
            expected_completion_date=datetime.now() + timedelta(days=49),
            model_type=ModelType.MONTE_CARLO,
            sample_predictions=[2, 3, 3, 4, 5],
        )
        assert len(result.prediction_intervals) == 2
        assert result.expected_sprints == 3.5
        assert result.model_type == ModelType.MONTE_CARLO

    def test_get_prediction_at_confidence(self):
        intervals = [
            PredictionInterval(0.5, 2.0, 3.0, 4.0),
            PredictionInterval(0.85, 2.0, 4.0, 6.0),
        ]
        result = ForecastResult(
            prediction_intervals=intervals,
            expected_sprints=3.5,
            expected_completion_date=datetime.now(),
        )

        interval = result.get_prediction_at_confidence(0.5)
        assert interval is not None
        assert interval.predicted_value == 3.0

        interval = result.get_prediction_at_confidence(0.85)
        assert interval is not None
        assert interval.predicted_value == 4.0

        interval = result.get_prediction_at_confidence(0.95)
        assert interval is None

    def test_get_percentile(self):
        intervals = [
            PredictionInterval(0.5, 2.0, 3.0, 4.0),
            PredictionInterval(0.85, 2.0, 4.0, 6.0),
        ]
        result = ForecastResult(
            prediction_intervals=intervals,
            expected_sprints=3.5,
            expected_completion_date=datetime.now(),
        )

        assert result.get_percentile(0.5) == 3.0
        assert result.get_percentile(0.85) == 4.0
        assert result.get_percentile(0.95) is None


class TestMonteCarloModel:
    def test_model_info(self):
        model = MonteCarloModel()
        info = model.get_model_info()

        assert info.model_type == ModelType.MONTE_CARLO
        assert info.name == "Monte Carlo Simulation"
        assert info.supports_probability_distribution is True
        assert info.required_historical_periods == 3
        assert info.configuration_class == MonteCarloConfiguration

    def test_validate_inputs(self):
        model = MonteCarloModel()
        velocity_metrics = VelocityMetrics(
            average=20.0,
            median=18.0,
            std_dev=5.0,
            min_value=10.0,
            max_value=30.0,
            trend=0.5,
        )

        # Valid inputs
        errors = model.validate_inputs(100.0, velocity_metrics)
        assert len(errors) == 0

        # Invalid remaining work
        errors = model.validate_inputs(-10.0, velocity_metrics)
        assert "Remaining work must be positive" in errors

        # Invalid velocity
        velocity_metrics = VelocityMetrics(0, 0, 0, 0, 0, 0)
        errors = model.validate_inputs(100.0, velocity_metrics)
        assert "Average velocity must be positive" in errors

    def test_forecast_basic(self):
        model = MonteCarloModel()
        velocity_metrics = VelocityMetrics(
            average=20.0,
            median=18.0,
            std_dev=5.0,
            min_value=10.0,
            max_value=30.0,
            trend=0.5,
        )
        config = MonteCarloConfiguration(
            num_simulations=1000, confidence_levels=[0.5, 0.85]
        )

        result = model.forecast(100.0, velocity_metrics, config)

        assert result.model_type == ModelType.MONTE_CARLO
        assert len(result.prediction_intervals) == 2
        assert result.expected_sprints > 0
        assert result.expected_completion_date > datetime.now()
        assert len(result.sample_predictions) == 1000
        assert result.probability_distribution is not None

    def test_forecast_without_variance(self):
        model = MonteCarloModel()
        velocity_metrics = VelocityMetrics(
            average=20.0,
            median=20.0,
            std_dev=0.0,
            min_value=20.0,
            max_value=20.0,
            trend=0.0,
        )
        config = MonteCarloConfiguration(
            num_simulations=100, use_historical_variance=False
        )

        result = model.forecast(100.0, velocity_metrics, config)

        # Without variance, all simulations should yield same result
        assert result.expected_sprints == 5.0  # 100 / 20


class TestDefaultModelFactory:
    def test_create_monte_carlo_model(self):
        factory = DefaultModelFactory()
        model = factory.create(ModelType.MONTE_CARLO)
        assert isinstance(model, MonteCarloModel)

    def test_create_unknown_model(self):
        factory = DefaultModelFactory()
        with pytest.raises(ValueError, match="Unknown model type"):
            factory.create(ModelType.PERT)  # Not implemented yet

    def test_get_available_models(self):
        factory = DefaultModelFactory()
        models = factory.get_available_models()
        assert len(models) >= 1
        assert any(m.model_type == ModelType.MONTE_CARLO for m in models)

    def test_get_default_model(self):
        factory = DefaultModelFactory()
        model = factory.get_default_model()
        assert isinstance(model, MonteCarloModel)

    def test_get_default_config(self):
        factory = DefaultModelFactory()
        config = factory.get_default_config(ModelType.MONTE_CARLO)
        assert isinstance(config, MonteCarloConfiguration)

    def test_register_model(self):
        factory = DefaultModelFactory()

        # Create a mock model class
        MockModel = Mock(spec=ForecastingModel)
        mock_instance = Mock(spec=ForecastingModel)
        MockModel.return_value = mock_instance

        # Register it
        factory.register_model(ModelType.PERT, MockModel)

        # Should be able to create it now
        model = factory.create(ModelType.PERT)
        assert model == mock_instance


class TestGenerateForecastUseCase:
    def test_execute_success(self):
        # Mock model
        mock_model = Mock(spec=ForecastingModel)
        mock_model.validate_inputs.return_value = []
        mock_model.get_model_info.return_value = ModelInfo(
            model_type=ModelType.MONTE_CARLO,
            name="Test Model",
            description="Test",
            supports_probability_distribution=True,
            required_historical_periods=3,
            configuration_class=ModelConfiguration,
        )

        mock_result = ForecastResult(
            prediction_intervals=[],
            expected_sprints=3.0,
            expected_completion_date=datetime.now(),
        )
        mock_model.forecast.return_value = mock_result

        # Execute use case
        use_case = GenerateForecastUseCase(mock_model)
        velocity_metrics = VelocityMetrics(20, 18, 5, 10, 30, 0.5)
        config = ModelConfiguration()

        result = use_case.execute(100.0, velocity_metrics, config)

        assert result == mock_result
        mock_model.validate_inputs.assert_called_once_with(100.0, velocity_metrics)
        mock_model.forecast.assert_called_once_with(100.0, velocity_metrics, config)

    def test_execute_invalid_inputs(self):
        # Mock model with validation errors
        mock_model = Mock(spec=ForecastingModel)
        mock_model.validate_inputs.return_value = ["Invalid input"]

        use_case = GenerateForecastUseCase(mock_model)
        velocity_metrics = VelocityMetrics(0, 0, 0, 0, 0, 0)
        config = ModelConfiguration()

        with pytest.raises(ValueError, match="Invalid inputs for forecasting"):
            use_case.execute(100.0, velocity_metrics, config)

    def test_execute_invalid_config(self):
        # Mock model
        mock_model = Mock(spec=ForecastingModel)
        mock_model.validate_inputs.return_value = []

        use_case = GenerateForecastUseCase(mock_model)
        velocity_metrics = VelocityMetrics(20, 18, 5, 10, 30, 0.5)
        config = ModelConfiguration(sprint_duration_days=-1)

        with pytest.raises(ValueError, match="Invalid configuration"):
            use_case.execute(100.0, velocity_metrics, config)


class TestCompareForecastModelsUseCase:
    def test_compare_all_models(self):
        # Mock factory
        mock_factory = Mock(spec=DefaultModelFactory)

        # Mock model info
        model_info = ModelInfo(
            model_type=ModelType.MONTE_CARLO,
            name="Monte Carlo",
            description="Test",
            supports_probability_distribution=True,
            required_historical_periods=3,
            configuration_class=MonteCarloConfiguration,
        )
        mock_factory.get_available_models.return_value = [model_info]

        # Mock model and result
        mock_model = Mock(spec=ForecastingModel)
        mock_model.validate_inputs.return_value = []
        mock_model.get_model_info.return_value = model_info

        mock_result = ForecastResult(
            prediction_intervals=[],
            expected_sprints=3.0,
            expected_completion_date=datetime.now(),
        )
        mock_model.forecast.return_value = mock_result

        mock_factory.create.return_value = mock_model
        mock_factory.get_default_config.return_value = MonteCarloConfiguration()

        # Execute use case
        use_case = CompareForecastModelsUseCase(mock_factory)
        velocity_metrics = VelocityMetrics(20, 18, 5, 10, 30, 0.5)

        results = use_case.execute(100.0, velocity_metrics)

        assert ModelType.MONTE_CARLO in results
        assert results[ModelType.MONTE_CARLO] == mock_result

    def test_compare_specific_models(self):
        # Mock factory
        mock_factory = Mock(spec=DefaultModelFactory)

        # Mock model
        mock_model = Mock(spec=ForecastingModel)
        mock_result = ForecastResult(
            prediction_intervals=[],
            expected_sprints=3.0,
            expected_completion_date=datetime.now(),
        )

        # Create a mock that handles the chained calls
        mock_use_case = Mock()
        mock_use_case.execute.return_value = mock_result

        mock_factory.create.return_value = mock_model
        mock_factory.get_default_config.return_value = MonteCarloConfiguration()

        # Patch GenerateForecastUseCase
        with patch(
            "src.application.forecasting_use_cases.GenerateForecastUseCase",
            return_value=mock_use_case,
        ):
            use_case = CompareForecastModelsUseCase(mock_factory)
            velocity_metrics = VelocityMetrics(20, 18, 5, 10, 30, 0.5)

            results = use_case.execute(100.0, velocity_metrics, [ModelType.MONTE_CARLO])

            assert ModelType.MONTE_CARLO in results
            assert results[ModelType.MONTE_CARLO] == mock_result

    def test_compare_handles_errors(self):
        # Mock factory that raises error
        mock_factory = Mock(spec=DefaultModelFactory)
        mock_factory.create.side_effect = Exception("Model creation failed")

        use_case = CompareForecastModelsUseCase(mock_factory)
        velocity_metrics = VelocityMetrics(20, 18, 5, 10, 30, 0.5)

        results = use_case.execute(100.0, velocity_metrics, [ModelType.MONTE_CARLO])

        # Should handle error gracefully and return empty results
        assert len(results) == 0
