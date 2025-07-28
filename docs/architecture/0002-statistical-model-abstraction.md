# LADR-0002: Statistical Model Abstraction

Date: 2025-07-27
Status: ACCEPTED

## Context

The current system is tightly coupled to Monte Carlo simulation as the forecasting method. However, different teams may prefer different statistical approaches:
- Some may want PERT (Program Evaluation and Review Technique)
- Others might prefer simple linear regression
- Machine learning models could provide more sophisticated predictions
- Bayesian inference might be preferred for certain domains

The current implementation has Monte Carlo logic embedded in the use cases, making it difficult to swap forecasting methods.

## Decision

We will create a statistical model abstraction that:

1. Defines a common `ForecastingModel` interface that all models must implement
2. Encapsulates all statistical logic within model implementations
3. Makes the choice of model configurable at runtime
4. Keeps the domain and application layers agnostic to the specific forecasting method

### Architecture

```
Domain Layer:
├── ForecastingModel (interface)
├── ForecastingModelFactory (interface)
├── ForecastResult (unified result type)
├── ModelConfiguration (base config)
└── PredictionInterval (value object)

Infrastructure Layer:
├── MonteCarloModel
├── PERTModel (future)
├── LinearRegressionModel (future)
├── BayesianModel (future)
└── DefaultModelFactory

Application Layer:
├── GenerateForecastUseCase (replaces RunMonteCarloSimulationUseCase)
└── Uses ForecastingModel interface only
```

## Consequences

### Positive

- **Flexibility**: New forecasting models can be added without changing existing code
- **Testability**: Models can be tested in isolation
- **Comparison**: Multiple models can be run and compared
- **Configuration**: Model selection can be configuration-driven
- **Clean separation**: Statistical complexity is isolated from business logic

### Negative

- **Additional abstraction**: More interfaces to maintain
- **Result mapping**: Need to map model-specific outputs to common format
- **Configuration complexity**: More options for users to understand

### Neutral

- **Performance**: Model abstraction has negligible overhead
- **Migration**: Existing Monte Carlo functionality remains unchanged

## Implementation Plan

1. Create `ForecastingModel` interface with methods:
   - `forecast(remaining_work, velocity_metrics, config) -> ForecastResult`
   - `get_model_info() -> ModelInfo`
   - `validate_inputs(remaining_work, velocity_metrics) -> List[ValidationError]`

2. Create `ForecastResult` that unifies different model outputs:
   - Prediction intervals at various confidence levels
   - Probability distributions (if applicable)
   - Model-specific metadata

3. Refactor existing Monte Carlo logic into `MonteCarloModel`

4. Update `GenerateForecastUseCase` to use the abstraction

5. Add model selection to CLI and configuration

## Example Usage

```python
# Configure model
model_factory = DefaultModelFactory()
model = model_factory.create("monte_carlo", config)

# Or with custom model
custom_model = PERTModel(optimistic_factor=0.8, pessimistic_factor=1.5)

# Use case doesn't know which model
forecast_use_case = GenerateForecastUseCase(model)
result = forecast_use_case.execute(remaining_work, velocity_metrics)
```

## Future Models

- **PERT Model**: Uses optimistic, most likely, and pessimistic estimates
- **Linear Regression**: Projects based on historical trend lines
- **Machine Learning**: Uses features like team size, sprint length, issue types
- **Bayesian Inference**: Updates predictions as more data becomes available