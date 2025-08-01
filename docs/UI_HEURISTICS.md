# UI Heuristics and Workarounds

This document catalogs UI heuristics and workarounds implemented in Sprint Radar to ensure smooth user experience, particularly around dynamic chart updates and scenario switching.

## Overview

UI heuristics are specific techniques we use to work around limitations in our visualization libraries (primarily Plotly.js) and browser rendering behavior. These workarounds are essential for maintaining a professional, smooth user experience.

## Critical UI Heuristics

### 1. Bar Chart Normalization for Scenario Switching

**Problem**: When switching between baseline and adjusted velocity scenarios, if the datasets have different numbers of bars (e.g., baseline completes in 5 sprints, adjusted in 7 sprints), Plotly will animate the chart resize, causing a jarring layout jump.

**Solution**: Normalize both datasets to have the same x-axis values by padding with zero-value "ghost" bars. Use a single data source for both initial render and scenario switching.

**Implementation**:
- **Backend**: `src/presentation/combined_report_generator.py::_normalize_bar_chart_data()`
- **Frontend**: `packages/report-builder/src/renderer.tsx` (unified data source)

**Technical Details**:
```python
# Backend: Ensure both datasets have same x-values
all_x = sorted(baseline_x.union(adjusted_x))
new_y = [x_to_y.get(x, 0) for x in all_x]  # 0 for missing values
```

```javascript
// Frontend: Use scenario data for initial render
if (window.scenarioChartData && initialScenario && chartType) {
    const scenarioData = window.scenarioChartData[initialScenario];
    if (scenarioData && scenarioData[chartType]) {
        data = scenarioData[chartType].data;
        layout = scenarioData[chartType].layout;
    }
}
```

### 1b. Chart Animation Sequencing

**Problem**: Animating both data and layout simultaneously causes rescaling/double-animation effects after the main animation completes.

**Solution**: Use three-step animation sequence from legacy code:
1. Update layout with `Plotly.relayout()` to prevent rescaling
2. Animate data with `Plotly.animate()` for smooth transitions
3. Update text labels with `Plotly.restyle()` after animation

**Implementation**: `packages/report-builder/src/renderer.tsx`

**Technical Details**:
```javascript
// Prevent rescaling during animation
Plotly.relayout(container, plotlyLayout).then(() => {
    // Animate just the data
    return Plotly.animate(container, {
        data: plotlyData,
        traces: [0]
    }, {
        transition: { duration: 750, easing: 'cubic-in-out' }
    });
}).then(() => {
    // Update text labels after animation
    Plotly.restyle(container, { text: [plotlyData[0].text] }, [0]);
});
```

### 2. Container Height Locking

**Problem**: Chart transitions can cause container height changes, making the entire page jump and disrupting the user's reading position.

**Solution**: Lock the container height before transitions, then restore to auto after completion.

**Implementation**: `src/presentation/static/js/charts.js`

```javascript
const container = document.getElementById('chart-container');
const containerHeight = container.offsetHeight;
container.style.height = containerHeight + 'px';
// ... perform transition ...
setTimeout(() => {
    container.style.height = 'auto';
}, 300);
```

### 3. Scroll Position Preservation

**Problem**: Chart updates and toggles can cause the browser to lose scroll position.

**Solution**: Store scroll position before updates and restore after.

**Implementation**: `src/presentation/static/js/charts.js::toggleChartType()`

```javascript
const scrollPosition = window.scrollY;
// ... perform update ...
window.scrollTo(0, scrollPosition);
```

### 4. Text Label Visibility Management

**Problem**: When bars animate from/to zero height, their text labels create visual clutter.

**Solution**: Conditionally hide labels for bars that are transitioning from/to zero.

**Implementation**: `src/presentation/static/js/scenario-switcher.js`

```javascript
const showText = probabilities.map((p, i) => {
    const prevValue = i < prevY.length ? prevY[i] : 0;
    return (prevValue > 0 && p > 0);  // Hide if transitioning from/to 0
});
```

### 5. Consistent Axis Scaling Across Scenarios

**Problem**: Y-axis rescaling during scenario switches makes it difficult to compare values.

**Solution**: Calculate maximum values across all scenarios and maintain consistent scaling.

**Implementation**: `src/presentation/static/js/scenario-switcher.js`

```javascript
// Calculate max across both scenarios
let maxProb = Math.max(
    ...baselineData.probability_distribution.map(d => d.probability),
    ...adjustedData.probability_distribution.map(d => d.probability)
);
const yRange = [0, maxProb * 1.2];  // 20% padding
```

### 6. Fade Transitions for UI Elements

**Problem**: Instant show/hide of UI elements is jarring.

**Solution**: Use opacity transitions with proper timing.

**Implementation**: Various components

```javascript
element.style.transition = 'opacity 0.3s ease-in-out';
element.style.opacity = '0';
setTimeout(() => {
    element.style.display = 'none';
}, 300);
```

## When to Add New Heuristics

Consider adding a new UI heuristic when:

1. **Users report jarring visual experiences** - Layout jumps, flashing, etc.
2. **Cross-browser inconsistencies** - Different behavior across browsers
3. **Library limitations** - Working around Plotly.js or other library constraints
4. **Performance optimizations** - Improving perceived performance

## How to Document New Heuristics

When implementing a new UI heuristic:

1. **Add inline code comments** explaining:
   - The problem being solved
   - Why this approach was chosen
   - Any tradeoffs or limitations

2. **Update this document** with:
   - Problem description
   - Solution approach
   - Implementation locations
   - Code examples

3. **Create tests** where possible to prevent regression

4. **Update LADR** if the heuristic represents a significant architectural decision

## Testing UI Heuristics

### Manual Testing
1. Test scenario switching with varying data ranges
2. Verify no layout jumps or flashes
3. Check scroll position preservation
4. Test on different screen sizes
5. Verify across browsers (Chrome, Firefox, Safari)

### Automated Testing
- Visual regression tests for critical transitions
- Performance benchmarks for animation smoothness
- Unit tests for normalization logic

## Maintenance Guidelines

### Regular Review
- Review heuristics when upgrading Plotly.js
- Check if browser updates affect behavior
- Consider if new browser APIs can replace workarounds

### Deprecation Process
1. Verify the original problem no longer exists
2. Test thoroughly across all supported browsers
3. Remove code and update documentation
4. Keep record in version history

## Related Documentation

- `/docs/architecture/006-plotly-animations.md` - Plotly animation architecture
- `/docs/ux-patterns/` - Detailed UX pattern documentation
- `/docs/ux-patterns/001-chart-transition-smoothing.md` - Chart transition pattern
- `/DESIGN_SYSTEM.md` - Overall design system documentation
- `/packages/ui/README.md` - UI component library documentation

## Common Pitfalls

1. **Forgetting to normalize data** - Always ensure datasets have matching structures
2. **Hard-coding transition timings** - Use constants for maintainability
3. **Not handling edge cases** - Empty datasets, single data points, etc.
4. **Browser-specific code** - Always provide fallbacks
5. **Memory leaks** - Clean up event listeners and timers

## Future Considerations

As we expand the application, consider:
- Creating a centralized transition manager
- Abstracting common patterns into reusable utilities
- Investigating alternative charting libraries if Plotly limitations persist
- Building a custom animation framework for complex scenarios