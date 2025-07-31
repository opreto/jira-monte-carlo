# Monte Carlo Simulation and Process Health Heuristics

This document details all the heuristics, thresholds, and algorithms used throughout the Monte Carlo project analytics system.

## Table of Contents

1. [Monte Carlo Simulation](#monte-carlo-simulation)
2. [Process Health Analysis](#process-health-analysis)
3. [Velocity Adjustments](#velocity-adjustments)
4. [Lead Time Analysis](#lead-time-analysis)
5. [Sprint Health Metrics](#sprint-health-metrics)
6. [Aging Analysis](#aging-analysis)
7. [Work In Progress (WIP) Analysis](#work-in-progress-wip-analysis)
8. [Blocked Items Analysis](#blocked-items-analysis)
9. [Lookback Period Auto-Detection](#lookback-period-auto-detection)

## Monte Carlo Simulation

The Monte Carlo simulation uses random sampling from historical velocity data to predict project completion.

### Core Algorithm

```python
# For each simulation run:
1. Sample velocity from normal distribution: velocity = random.gauss(mean, std_dev)
2. Ensure positive velocity: velocity = max(0.1, velocity)
3. Simulate sprints until work is complete
4. Safety limit: max 1000 sprints per simulation
```

### Key Parameters

- **Number of Simulations**: Default 10,000 runs
- **Confidence Levels**: [50%, 70%, 85%, 95%] - percentiles calculated from simulation results
- **Variance Multiplier**: Default 1.0 - can be adjusted for sensitivity analysis
- **Sprint Duration**: Default 14 days
- **Minimum Historical Data**: 3 data points required for meaningful statistics

### Velocity Sampling

- Uses normal (Gaussian) distribution based on historical data
- Mean: Average velocity from past sprints
- Standard Deviation: Calculated from historical variance
- Warning triggered if std_dev > 0.5 * mean (high variance)

### Confidence Interval Calculation

For each confidence level:

- Percentile index: `int(n * confidence_level)`
- Lower bound: `int(n * alpha/2)` where alpha = 1 - confidence_level
- Upper bound: `int(n * (1 - alpha/2))`

## Process Health Analysis

Process health is calculated as a composite score from multiple components.

### Overall Health Score Calculation

The overall health score (0-1) is the weighted average of component scores:

```python
overall_score = sum(component.score * component.weight) / sum(weights)
```

### Health Score Thresholds

- **Healthy**: ≥ 0.8 (Green)
- **Needs Attention**: 0.6 - 0.79 (Yellow)
- **Critical**: < 0.6 (Red)

### Component Weights

All components have equal weight (1.0) by default, contributing equally to the overall score.

## Velocity Adjustments

### Capacity Factors

- **Factor Range**: 0.0 - 2.0
  - 0.5 = 50% capacity (half productivity)
  - 1.0 = 100% capacity (normal)
  - 1.5 = 150% capacity (increased productivity)

### Team Change Ramp-up

New team members have reduced productivity that ramps up over time:

#### Linear Ramp-up (Default)

- Sprint 0: 25% productivity
- Gradual increase: `0.25 + (0.75 * sprints_since_start / ramp_up_sprints)`
- Full productivity: After ramp_up_sprints

#### Exponential Ramp-up

- Starts slower, accelerates: `0.25 + 0.75 * (progress^2)`

#### Step Function

- 25% → 50% → 75% → 100% in equal steps

## Lead Time Analysis

### Lead Time Scoring

Lead time affects process health score based on these thresholds:

| Lead Time (days) | Score | Status |
|------------------|-------|---------|
| ≤ 7 | 1.0 | Excellent |
| 8-14 | 0.9 | Good |
| 15-21 | 0.7 | Fair |
| 22-30 | 0.5 | Poor |
| > 30 | 0.2-0.5* | Critical |

*Gradually declines: `max(0.2, 0.5 - (lead_time - 30) / 60)`

### Quality Adjustments

- **Defect Rate Penalty**: `min(0.3, defect_rate * 0.5)`
  - Maximum 30% score reduction
  - Applied when defect_rate > 0

- **Flow Efficiency Bonus**:
  - > 80% efficiency: +0.1 to score
  - > 60% efficiency: +0.05 to score

### Defect Rate Thresholds

- **High**: > 15% - "High defect rate - improve quality practices"
- **Medium**: 10-15% - "Consider additional quality checks"
- **Low**: < 10% - Acceptable

### Flow Efficiency

Calculated as: `cycle_time / lead_time`

- Measures the ratio of active work time to total time
- Higher is better (less waiting/blocked time)

## Sprint Health Metrics

### Predictability Score

Based on velocity consistency across sprints:

- Uses coefficient of variation (CV) = std_dev / mean
- Score calculation: Implementation-specific

### Sprint Velocity Trend

- Positive trend: Velocity increasing over time
- Negative trend: Velocity decreasing
- Calculated using linear regression or moving averages

## Aging Analysis

Work items are categorized by age with dynamic thresholds:

### Default Age Categories

| Category | Age Range | Description |
|----------|-----------|-------------|
| Fresh | 0-7 days | Recently created |
| Normal | 8-14 days | Typical processing |
| Aging | 15-30 days | Needs attention |
| Stale | 31-60 days | Overdue |
| Abandoned | 60+ days | Severely overdue |

### Aging Score Calculation

```python
critical_items = stale + abandoned items
aging_ratio = critical_items / total_items
score = 1 - min(aging_ratio * 2, 1)
```

- Perfect score (1.0) when no critical items
- Score decreases as critical ratio increases
- Minimum score of 0 when ≥50% items are critical

### Blocked Item Detection

Items are considered blocked if their status contains keywords:

- "blocked"
- "impediment"
- "waiting"
- "hold"

## Work In Progress (WIP) Analysis

### WIP Score Calculation

If WIP limits are defined:

```python
violation_ratio = violation_count / total_limit
score = max(0, 1 - violation_ratio)
```

If no limits defined:

- Score = 1.0 if no violations
- Score = 0.5 if any violations exist

### WIP Categories

- **TODO**: Not yet started
- **IN_PROGRESS**: Active work
- **REVIEW**: Awaiting review
- **BLOCKED**: Impediments present
- **DONE**: Completed

## Blocked Items Analysis

### Severity Classification

Based on days blocked:

- **Low**: ≤ 2 days
- **Medium**: 3-5 days
- **High**: > 5 days

### Blocked Items Score

```python
high_severity_count = items_blocked > 5 days
blocked_ratio = high_severity_count / total_blocked_items
score = 1 - min(blocked_ratio * 2, 1)
```

- Score of 1.0 when no items blocked
- Decreases based on high-severity ratio
- Minimum score of 0 when ≥50% are high severity

## Confidence Levels and Percentiles

### Standard Confidence Levels

The system uses these standard percentiles for predictions:

- **P50 (50%)**: Median case - equally likely to finish earlier or later
- **P70 (70%)**: Moderate confidence - 70% chance of completion by this sprint
- **P85 (85%)**: Conservative estimate - 85% chance of completion
- **P95 (95%)**: Highly conservative - 95% chance of completion

### Multi-Project Aggregation

When combining multiple projects:

```python
variance_factor = 1.0 + (confidence_level - 0.5) * 0.5
adjusted_sprints = base_sprints * variance_factor
```

This adds increasing variance for higher confidence levels to account for coordination overhead.

## Data Quality and Validation

### Minimum Data Requirements

- **Velocity Calculation**: At least 1 completed sprint
- **Statistical Analysis**: At least 3 data points
- **Trend Detection**: At least 5 data points recommended

### Data Confidence Score

Calculated based on:

- Number of historical data points
- Consistency of data (low variance = higher confidence)
- Recency of data
- Completeness of fields

### Outlier Detection

- Velocities beyond 2 standard deviations are flagged
- Option to exclude outliers from calculations
- Automatic warnings for suspicious data patterns

## Usage Guidelines

### When to Adjust Heuristics

1. **Aging Thresholds**: Adjust based on your team's workflow and sprint length
2. **WIP Limits**: Set based on team size and capacity
3. **Lead Time Targets**: Adjust based on project type and complexity
4. **Defect Rate Thresholds**: Adjust based on quality standards

### Interpreting Results

- **Single Metric Focus**: Don't optimize for one metric at the expense of others
- **Trend Analysis**: Look at trends over time, not just current values
- **Context Matters**: Consider team changes, holidays, and external factors
- **Confidence Intervals**: Use appropriate confidence level for decision-making

### Best Practices

1. Collect at least 3-6 sprints of data before relying on predictions
2. Regularly review and adjust thresholds based on team performance
3. Use multiple confidence levels to communicate uncertainty
4. Monitor process health metrics weekly or bi-weekly
5. Document any manual adjustments or overrides

## Lookback Period Auto-Detection

The system automatically determines the optimal number of historical sprints to analyze when `--lookback-sprints auto` is used (default).

### Heuristic Algorithm

The auto-detection balances three key factors:
1. **Statistical Significance**: Having enough data points for meaningful analysis
2. **Recency**: Using recent data that reflects current team performance
3. **Data Availability**: Adapting to the amount of historical data available

### Detection Rules

| Available Sprints | Lookback Period | Rationale |
|------------------|-----------------|-----------|
| ≤ 6 | All sprints | Use all available data when limited |
| 7-12 | 6 sprints | Standard agile retrospective period (6-12 weeks) |
| 13-24 | 8-10 sprints | 2-3 months of data for better statistical confidence |
| 25-52 | 12 sprints | One quarter of data balances recency with significance |
| > 52 | 16-20 sprints | Cap at ~5 months to maintain relevance |

### Implementation Details

```python
if total_sprints <= 6:
    return total_sprints
elif total_sprints <= 12:
    return 6
elif total_sprints <= 24:
    return min(10, total_sprints // 2)
elif total_sprints <= 52:
    return 12
else:
    return min(20, total_sprints // 3)
```

### Usage

- **Default Behavior**: The system uses `auto` by default, intelligently selecting the lookback period
- **Manual Override**: Specify a number to override: `--lookback-sprints 10`
- **Applies To**: Both velocity calculations and sprint health metrics for consistency

### Benefits

1. **Adaptive**: Automatically adjusts to team maturity and data availability
2. **Consistent**: Same heuristic used across all analytics for coherent reporting
3. **Balanced**: Avoids using too little data (low confidence) or too old data (irrelevant)
4. **Smart Defaults**: New teams get appropriate analysis without configuration
