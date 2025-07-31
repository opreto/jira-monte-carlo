# ML-Enhanced Heuristics Guide

## Overview

Sprint Radar now supports privacy-preserving machine learning to optimize various heuristics based on your team's specific patterns. All ML happens locally on your machine, and each project's data is completely isolated.

## Key Features

### 1. Privacy-First Design

- **Complete Data Isolation**: Each project's models are stored separately
- **Local-Only Processing**: No data ever leaves your machine
- **Statistical Features Only**: Models use aggregates, not raw data
- **Explainable Predictions**: Every ML decision includes reasoning

### 2. Available ML Models

#### Velocity Lookback Optimizer
Learns the optimal number of historical sprints to analyze for velocity calculations based on:
- Velocity stability patterns
- Trend detection
- Recent changes vs historical patterns
- Autocorrelation in velocity data

**Benefits**:
- More accurate forecasts by using the right amount of history
- Adapts to team changes and process improvements
- Detects when old data is no longer relevant

#### Sprint Health Lookback Optimizer
Learns the optimal number of sprints to analyze for sprint health metrics based on:
- Sprint completion rate patterns
- Consistency in meeting commitments
- Recent performance trends
- Delivery predictability

**Benefits**:
- Better understanding of team's delivery consistency
- Early detection of process degradation
- Adaptive lookback based on team stability

## Usage

### Enable ML Features

```bash
# Run forecast with ML optimization enabled
sprint-radar -f your-data.csv --enable-ml

# For Jira API, project key is automatically detected
sprint-radar -f jira-api:// --enable-ml

# ML will automatically activate when:
# - You have 20+ sprints of historical data
# - The --enable-ml flag is used
# - A project identifier can be determined (from filename or Jira API)
```

Note: For CSV files, include the project key in the filename (e.g., `PROJ-export.csv`) for ML features to activate.

### Understanding ML Explanations

When ML is enabled, you'll see explanations for predictions in your reports:

**For Velocity Analysis:**
```
[INFO] ML-optimized lookback: 8 sprints (confidence: 0.82)
  - variance: CV=0.45 indicates high variability
  - recency: Recent velocity differs from historical pattern
  - Recommendation: Using fewer sprints due to high variance
```

**For Sprint Health Analysis:**
```
[INFO] ML-optimized sprint health lookback: 14 sprints (confidence: 0.70)
  - delivery: 50% of sprints below 80% target
  - consistency: Inconsistent completion patterns detected
  - Recommendation: Using more sprints to understand delivery patterns
```

### ML Decision Transparency in Reports

When ML is enabled, HTML reports include visual indicators (🧠) next to metrics that were ML-optimized. Hovering over these indicators shows:
- The ML model used (e.g., VelocityLookbackOptimizer)
- The decision made (e.g., "Using 14 sprints lookback")
- Confidence level as a percentage
- Primary reasoning factor
- Additional supporting factors

This transparency helps you understand and trust ML recommendations.

### Fallback Behavior

The system gracefully falls back to standard heuristics when:
- Insufficient data for ML (< 20 sprints)
- ML model errors occur
- ML is disabled

## Privacy & Security

### Data Storage

```
~/.sprint-radar/
└── projects/
    └── PROJ-123/
        ├── models/           # Trained ML models
        ├── prediction_logs/  # Local improvement logs
        └── model_metadata/   # Model versioning
```

### What's Stored
- **Models**: Statistical patterns only (1-10MB per model)
- **Logs**: Features and predictions for improvement (no raw data)
- **Metadata**: Training dates, performance metrics

### What's NOT Stored
- Raw velocity numbers
- Sprint names or dates
- Issue keys or descriptions
- Any identifiable information

## Performance Impact

- **Training Time**: < 1 second for most models
- **Prediction Time**: < 10ms per prediction
- **Storage**: ~10MB per project
- **Memory**: Minimal (~50MB when active)

## Model Management

### Automatic Retraining

Models retrain automatically when:
- 30 days have passed since last training
- Significant new data is available (50% more sprints)
- Manual retraining is requested

### Manual Control

```python
# In Python scripts
from src.application.ml_enhanced_use_cases import MLModelManagementUseCase

# Check model status
manager = MLModelManagementUseCase("PROJ-123")
status = manager.get_model_status()
print(status)

# Get privacy report
privacy_report = manager.get_privacy_report()
print(privacy_report)

# Clear models if needed
manager.clear_models()  # All models
manager.clear_models("VelocityLookbackOptimizer")  # Specific velocity model
manager.clear_models("SprintHealthLookbackOptimizer")  # Specific sprint health model
```

## Future ML Enhancements

### Coming Soon
1. **Team Productivity Curves**: Learn actual ramp-up patterns for new team members
2. **Aging Threshold Optimizer**: Adapt "stale" definitions to your team's workflow
3. **Sprint Health Predictor**: Forecast issues before they impact velocity
4. **Lead Time Predictor**: Estimate completion time at issue creation

### Opt-In Federated Learning (Future)

- Share model insights (not data) across projects
- Learn from industry patterns while maintaining privacy
- Always opt-in, never automatic

## Troubleshooting

### ML Not Working?

1. **Check Data Availability**
   - Need at least 20 historical sprints
   - Ensure velocity data is present

2. **Verify Project Key**
   - Consistent project-key across commands
   - Check `~/.sprint-radar/projects/`

3. **Clear and Retrain**
   ```bash
   sprint-radar ml clear --project-key PROJ-123
   sprint-radar forecast --ml-optimize  # Will retrain
   ```

### Performance Issues?

- ML adds < 1% overhead to calculations
- If slower, check disk space for model storage
- Disable with `--no-ml` flag if needed

## Best Practices

1. **Let Models Learn**: Give ML at least 30 days of usage to optimize
2. **Review Explanations**: Understand why ML makes recommendations
3. **Provide Feedback**: Report issues to improve models
4. **Regular Updates**: Keep Sprint Radar updated for latest ML improvements
5. **Privacy First**: Never share model files between projects

## Example: A/B Testing ML vs Heuristics

```python
# Compare ML vs heuristic performance for velocity
from src.application.use_cases import CalculateVelocityUseCase
from src.application.ml_enhanced_use_cases import MLEnhancedVelocityUseCase

# Traditional heuristic
traditional = CalculateVelocityUseCase(issue_repo, sprint_repo)
heuristic_lookback = traditional.calculate_optimal_lookback(len(sprints))

# ML-enhanced velocity
ml_enhanced = MLEnhancedVelocityUseCase(
    issue_repo, sprint_repo, 
    project_key="PROJ-123", 
    enable_ml=True
)
velocity_metrics, ml_decisions = ml_enhanced.execute()

# Compare sprint health analysis
from src.application.process_health_use_cases import AnalyzeSprintHealthUseCase
from src.application.ml_enhanced_use_cases import MLEnhancedSprintHealthUseCase

# Traditional sprint health
traditional_health = AnalyzeSprintHealthUseCase(issue_repo, sprint_repo)
heuristic_health_lookback = traditional_health.calculate_optimal_lookback(len(sprints))

# ML-enhanced sprint health
ml_health = MLEnhancedSprintHealthUseCase(
    issue_repo, sprint_repo,
    project_key="PROJ-123",
    enable_ml=True
)
sprint_health, health_ml_decisions = ml_health.execute()

print(f"Velocity - Heuristic: {heuristic_lookback} sprints")
print(f"Velocity - ML: {ml_decisions.get_decision('lookback_period').value} sprints")
print(f"Sprint Health - Heuristic: {heuristic_health_lookback} sprints")
print(f"Sprint Health - ML: {health_ml_decisions.get_decision('sprint_health_lookback').value} sprints")
```

## Contributing

We welcome contributions to improve ML models! Areas of interest:
- Additional privacy-preserving features
- New model types for other heuristics
- Performance optimizations
- Explainability improvements

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.