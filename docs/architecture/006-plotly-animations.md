# 006 - Plotly Chart Animations

## Status
ACCEPTED

## Context
When switching between baseline and adjusted velocity scenarios in the Sprint Radar reports, the charts were updating but without any smooth transitions or animations. This made it difficult for users to visually track the changes between scenarios.

## Decision
We implemented smooth animations for Plotly charts when switching between scenarios using the following approach:

1. **Use Plotly.animate() for transitions** - Instead of just using `Plotly.react()`, we now use `Plotly.animate()` when a chart already exists to provide smooth transitions.

2. **Consistent chart structure** - Ensure that the chart data structure remains consistent between updates (same number of traces, same trace types) to enable smooth animations.

3. **Animation configuration** - Added transition configuration with:
   - Duration: 750ms
   - Easing: cubic-in-out
   - Frame duration: 750ms

4. **Fallback handling** - If animation fails, fall back to `Plotly.react()` without animation to ensure the chart still updates.

## Implementation Details

### Basic Animation
```javascript
// Check if chart exists
const currentPlot = container._fullLayout;
if (currentPlot) {
    // Use animate for smooth transition
    Plotly.animate(container, {
        data: plotlyData,
        layout: plotlyLayout
    }, {
        transition: {
            duration: 750,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 750
        }
    });
} else {
    // First time - use react
    Plotly.react(container, plotlyData, plotlyLayout, config);
}
```

### Three-Step Animation Sequence
For bar charts with changing data and text labels, we implement a three-step sequence to prevent rescaling issues:

```javascript
// Step 1: Update layout to prevent rescaling
Plotly.relayout(container, layoutUpdate).then(() => {
    // Step 2: Animate the data (bar heights)
    return Plotly.animate(container, {
        data: [trace],
        traces: [0]
    }, {
        transition: { duration: 750, easing: 'cubic-in-out' }
    });
}).then(() => {
    // Step 3: Update text labels after animation
    const finalText = values.map(v => v > 0 ? (v * 100).toFixed(1) + '%' : '');
    Plotly.restyle(container, { text: [finalText] }, [0]);
});
```

### Bar Chart Normalization
To prevent jarring layout changes when the number of bars differs between scenarios:

```python
def _normalize_bar_chart_data(self, baseline_data: list, adjusted_data: list) -> tuple:
    """Normalize bar chart data to have the same x-axis values
    
    This ensures both datasets have the same number of bars by adding empty bars
    where needed, preventing jarring layout changes during animation.
    """
    # Find union of all x values
    all_x = sorted(baseline_x.union(adjusted_x))
    
    # Add missing values with 0 height
    for x in all_x:
        if x not in baseline_map:
            baseline_map[x] = 0
        if x not in adjusted_map:
            adjusted_map[x] = 0
```

## Consequences

### Positive
- Smooth visual transitions when switching between baseline and adjusted scenarios
- Better user experience for comparing different velocity scenarios
- Easier to track changes in chart values
- Professional appearance with smooth animations

### Negative
- Slightly more complex implementation with animation fallback logic
- Potential performance impact on slower devices (mitigated by fallback)
- Animation duration adds a small delay to chart updates

## Alternatives Considered

1. **Using only Plotly.react()** - This was the original approach but didn't provide animations
2. **CSS transitions** - Would only work for simple DOM elements, not Plotly's canvas-based charts
3. **Custom animation library** - Would add unnecessary complexity and dependencies

## References
- Plotly.js documentation on animations: https://plotly.com/javascript/animations/
- Legacy implementation in `/src/presentation/static/js/charts.js`