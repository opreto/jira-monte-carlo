# Velocity Change Predictions

Date: 2025-07-29
Status: ACCEPTED

## Context

Teams need to model the impact of personnel changes on project forecasts. Common scenarios include:
- Developers going on vacation
- Team scaling (adding/removing members)
- Partial capacity allocation
- Onboarding ramp-up periods

Currently, the tool uses historical velocity without accounting for known future changes.

## Decision

Implement a velocity change prediction system following clean architecture principles:

### Domain Layer

```python
# src/domain/velocity_adjustments.py
@dataclass
class VelocityAdjustment:
    """Represents a velocity change for a sprint range"""
    sprint_start: int
    sprint_end: Optional[int]  # None means "forever"
    factor: float  # 0.5 = 50% capacity, 1.5 = 150% capacity
    reason: Optional[str]
    
@dataclass
class TeamChange:
    """Represents a team size change"""
    sprint: int
    change: int  # +2 for additions, -2 for departures
    ramp_up_sprints: int = 3
    productivity_curve: str = "linear"  # or "exponential"
    
@dataclass
class VelocityScenario:
    """Collection of adjustments forming a scenario"""
    name: str
    adjustments: List[VelocityAdjustment]
    team_changes: List[TeamChange]
    
    def get_adjusted_velocity(self, sprint: int, base_velocity: float) -> float:
        """Calculate adjusted velocity for a given sprint"""
        # Domain logic for applying adjustments
```

### Application Layer

```python
# src/application/velocity_prediction_use_cases.py
class ApplyVelocityAdjustmentsUseCase:
    """Apply velocity adjustments to forecasting"""
    
    def execute(
        self,
        base_forecast: ForecastResult,
        scenario: VelocityScenario
    ) -> Tuple[ForecastResult, ForecastResult]:
        """Returns (baseline, adjusted) forecasts"""
        # Orchestrate the adjustment process
        
class GenerateScenarioComparisonUseCase:
    """Generate comparison data for reporting"""
    
    def execute(
        self,
        baseline: ForecastResult,
        adjusted: ForecastResult,
        scenario: VelocityScenario
    ) -> ScenarioComparison:
        """Generate comparison metrics and descriptions"""
```

### Infrastructure Layer

```python
# src/infrastructure/velocity_adjustment_parser.py
class VelocityAdjustmentParser:
    """Parse CLI arguments into domain objects"""
    
    def parse_velocity_change(self, value: str) -> VelocityAdjustment:
        """Parse format: 'sprint:N[-M|+],factor:F[,reason:R]'"""
        
    def parse_team_change(self, value: str) -> TeamChange:
        """Parse format: 'sprint:N,change:±C[,ramp:R]'"""
```

### Presentation Layer

```python
# src/presentation/scenario_report_generator.py
class ScenarioReportGenerator:
    """Generate linked baseline/adjusted reports"""
    
    def generate_reports(
        self,
        comparison: ScenarioComparison,
        output_path: Path
    ) -> Tuple[Path, Path]:
        """Generate both reports with cross-links"""
        
    def _add_scenario_banner(self, scenario: VelocityScenario) -> str:
        """Generate user-friendly description of adjustments"""
        # Example: "This forecast includes: 30% reduced capacity 
        # for sprints 5-7 (summer holidays), adding 1 developer 
        # starting sprint 8 with 3-sprint ramp-up"
        
    def _add_chart_disclaimer(self, adjustment: VelocityAdjustment) -> str:
        """Add disclaimer to affected charts"""
```

## Implementation Strategy

1. **Phase 1: Core Domain Logic**
   - Implement velocity adjustment calculations
   - Add scenario modeling to forecasting

2. **Phase 2: CLI Integration**
   - Parse adjustment flags
   - Generate dual reports

3. **Phase 3: Enhanced Reporting**
   - Add comparison visualizations
   - Implement cross-linking between reports

## Benefits

- Clean separation of concerns
- Domain logic independent of CLI parsing
- Easy to add UI later (scenarios are domain objects)
- Testable at each layer

## Future Enhancements

- Save/load scenarios from files
- Interactive scenario builder in reports
- Machine learning from historical adjustments
- Team productivity profiles

## Example Usage

```bash
# Simple vacation
sprint-radar -f data.csv \
  --velocity-change "sprint:3,factor:0.5,reason:vacation"

# Complex scenario with dual reports
sprint-radar -f data.csv \
  --velocity-change "sprint:2-3,factor:0.8,reason:holidays" \
  --team-change "sprint:4,change:+1,ramp:3" \
  --output forecast.html

# Generates:
# - forecast-baseline.html
# - forecast-adjusted.html (with changes applied)
```