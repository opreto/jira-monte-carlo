# LADR-006: Velocity Scenario Refactoring for Sprint-Specific Adjustments

**Status:** ACCEPTED  
**Date:** 2025-08-01  
**Author:** Assistant  
**Deciders:** Xavier

## Context and Problem Statement

The current implementation of velocity and team adjustments in the Monte Carlo simulation averages out sprint-specific adjustments into a single factor. This defeats the purpose of having detailed velocity scenarios that can model complex real-world situations like:
- Team members joining with ramp-up periods
- Temporary velocity reductions (holidays, technical debt sprints)
- Gradual improvements from process changes

The averaging happens in the application layer (`ApplyVelocityAdjustmentsUseCase`), violating clean architecture principles by losing domain-specific information before it reaches the infrastructure layer.

## Decision Drivers

- **Accuracy**: Sprint-specific adjustments provide more accurate forecasts
- **Clean Architecture**: Domain logic should be preserved through layers
- **Backward Compatibility**: Existing functionality must continue to work
- **Performance**: Simulations should remain performant
- **Testability**: Changes should be easily testable

## Considered Options

### Option 1: Modify ForecastingModel Interface
Add VelocityScenario as a parameter to the forecast method.
- ❌ Breaks existing interface contract
- ❌ Forces all models to handle scenarios
- ❌ Violates Open-Closed Principle

### Option 2: Create Extended Configuration Classes
Extend ModelConfiguration to optionally include VelocityScenario.
- ✅ Maintains backward compatibility
- ✅ Follows Open-Closed Principle
- ✅ Models can opt-in to scenario support
- ✅ Clean separation of concerns

### Option 3: Pass Scenario Through Model Metadata
Use the existing metadata dictionary to pass scenarios.
- ❌ Type safety issues
- ❌ Hidden dependencies
- ❌ Poor discoverability

## Decision Outcome

**Chosen Option: Option 2 - Extended Configuration Classes**

Create a new configuration class that includes velocity scenario information:
- `MonteCarloConfigurationWithScenario` extends `MonteCarloConfiguration`
- `MonteCarloModel` checks for this configuration type and applies scenarios
- Use case passes the full scenario instead of averaging

## Implementation Details

### 1. Domain Layer
```python
@dataclass
class MonteCarloConfigurationWithScenario(MonteCarloConfiguration):
    """Monte Carlo configuration with velocity scenario support"""
    velocity_scenario: Optional[VelocityScenario] = None
    baseline_team_size: int = 5  # For team change calculations
```

### 2. Infrastructure Layer
The Monte Carlo model will:
- Check if configuration includes a scenario
- Apply sprint-specific adjustments during each sprint of simulation
- Maintain existing behavior when no scenario is provided

### 3. Application Layer
The use case will:
- Create configuration with scenario instead of averaging
- Pass scenario directly to the model
- Remove the averaging logic

## Consequences

### Positive
- More accurate forecasts with sprint-specific adjustments
- Clean architecture principles maintained
- Backward compatibility preserved
- Better represents real-world scenarios
- Easier to test specific adjustment patterns

### Negative
- Slightly more complex configuration
- Small performance impact from per-sprint calculations
- Need to update tests for new behavior

## Validation

Success will be measured by:
1. Integration tests showing different results for averaged vs sprint-specific adjustments
2. Existing tests continue to pass
3. Performance impact < 10% for typical simulations
4. React reports correctly display scenario information