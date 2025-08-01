# UX Pattern: Chart Transition Smoothing

**Pattern ID**: UXP-001  
**Category**: Data Visualization  
**Status**: Active  
**Created**: 2024-01-25  

## Problem Statement

When users switch between baseline and adjusted velocity scenarios in Sprint Radar reports, charts with different data ranges cause jarring visual experiences:
- Bars appearing/disappearing cause layout reflow
- Y-axis rescaling makes comparison difficult  
- Scroll position is lost during updates
- Text labels create visual noise during transitions

## User Impact

- **Severity**: Medium
- **Frequency**: Every scenario comparison
- **User Feedback**: "The animation isn't working, and I get errors in the console"

## Solution Pattern

Implement multi-layered normalization and transition management:

### 1. Data Normalization Layer
Ensure datasets have identical structures before rendering:
```python
# Backend: Pad datasets with zero values
all_x_values = union(baseline_x, adjusted_x)
padded_data = fill_missing_with_zeros(data, all_x_values)
```

### 2. Visual Stability Layer
Maintain consistent visual properties during transitions:
- Lock container heights
- Preserve scroll positions
- Use consistent axis scales
- Hide transitioning text labels

### 3. Animation Layer
Use appropriate animation methods:
- `Plotly.animate()` for existing charts
- `Plotly.react()` for initial render
- Graceful fallback on errors

## Implementation Details

### Files Modified
- `src/presentation/combined_report_generator.py` - Data normalization (both chart data and scenario data)
- `packages/report-builder/src/renderer.tsx` - Animation logic  
- `src/presentation/static/js/scenario-switcher.js` - Chart updates with normalized data
- `src/presentation/templates.py` - Embedded JavaScript for chart updates

### Key Functions
- `_normalize_bar_chart_data()` - Ensures matching x-axes for Plotly chart data
- `_normalize_scenario_charts()` - Applies normalization to chart objects  
- `_normalize_scenario_data()` - Normalizes the raw probability distributions in scenario data
- `updateCharts()` - Frontend animation orchestration using pre-normalized data

## Visual Examples

### Before (Jarring)
```
Baseline:  [====][====][====]
              1    2    3

Adjusted:  [====][====][====][====][====]
              1    2    3    4    5
```

### After (Smooth)
```
Baseline:  [====][====][====][    ][    ]
              1    2    3    4    5

Adjusted:  [====][====][====][====][====]
              1    2    3    4    5
```

## Testing Checklist

- [ ] No layout jumps when switching scenarios
- [ ] Scroll position maintained
- [ ] Smooth bar height animations
- [ ] Consistent axis scaling
- [ ] Text labels appear/disappear gracefully
- [ ] Works across Chrome, Firefox, Safari
- [ ] Handles edge cases (empty data, single bar)

## Alternatives Considered

1. **Fixed axis ranges** - Too restrictive for varying data
2. **No animation** - Poor user experience
3. **Complete re-render** - Loses context and position
4. **CSS-only transitions** - Insufficient for dynamic layouts

## Related Patterns

- UXP-002: Loading State Management
- UXP-003: Error State Handling
- UXP-004: Responsive Chart Sizing

## Maintenance Notes

- Review when upgrading Plotly.js
- May be simplified when Plotly adds native support
- Consider extracting to reusable chart transition manager

## References

- [Plotly Animation Documentation](https://plotly.com/javascript/animations/)
- [Material Design Motion Guidelines](https://material.io/design/motion/)
- Original issue: "Charts updating but animation isn't working"