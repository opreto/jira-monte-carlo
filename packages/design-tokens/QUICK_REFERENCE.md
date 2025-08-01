# Design System Quick Reference

## Colors

### Primary Palette
```css
/* Teal (Primary) */
--teal-50: #e6f4f2;
--teal-500: #03564c;
--teal-700: #023a33;
--teal-800: #022d2c;

/* Burgundy (Secondary) */
--burgundy-50: #fdf2f4;
--burgundy-900: #6B1229;

/* Cerulean (Accent) */
--cerulean-50: #e6f3f8;
--cerulean-500: #0E5473;
```

### Semantic Colors
```css
--success: #00A86B;  /* Jade Green */
--warning: #FFA500;  /* Orange */
--error: #DC143C;    /* Crimson */
```

## Typography

### Fonts
```css
/* Display headings */
font-family: 'Sublima', Georgia, serif;
font-weight: 700;
letter-spacing: -0.02em;

/* Body text */
font-family: 'Inter', -apple-system, sans-serif;
font-weight: 400;
line-height: 1.7;
```

### Sizes
- **H1**: 4rem / 3rem (mobile)
- **H2**: 3rem  
- **H3**: 2rem
- **Body**: 1rem
- **Small**: 0.875rem

## Common Components

### Card
```jsx
<div className="rounded-lg bg-white border border-gray-200 shadow-sm hover:shadow-md p-6">
  {/* Content */}
</div>
```

### Primary Button
```jsx
<button className="bg-teal-700 text-white px-4 py-2 rounded-md hover:bg-teal-800 transition-colors">
  Action
</button>
```

### Metric Display
```jsx
<div className="text-center">
  <div className="text-3xl font-bold text-teal-700">
    42
    <span className="text-lg text-gray-600 ml-1">pts</span>
  </div>
  <div className="text-sm text-gray-600">Metric Label</div>
</div>
```

### Table Row
```jsx
<tr className="hover:bg-teal-50/20 transition-colors">
  <td className="px-6 py-4 text-sm">{/* Content */}</td>
</tr>
```

## Utility Classes

### Spacing
- `p-4` = 1rem padding
- `m-2` = 0.5rem margin
- `gap-6` = 1.5rem gap

### Colors
- `text-teal-700` = Primary text
- `bg-teal-50` = Light background
- `border-gray-200` = Default border

### Shadows
- `shadow-sm` = Subtle shadow
- `shadow-md` = Medium shadow
- `shadow-lg` = Large shadow

### Transitions
- `transition-all duration-200`
- `hover:shadow-md`
- `hover:bg-teal-50/20`

## Chart Colors Array
```javascript
const chartColors = {
  primary: '#03564c',    // Teal
  secondary: '#0E5473',  // Cerulean
  tertiary: '#6B1229',   // Burgundy
  quaternary: '#FF8C00', // Orange
  success: '#00A86B',    // Green
  warning: '#FFA500',    // Orange
  danger: '#DC143C'      // Red
}
```

## Quick Tips

1. **Always use semantic colors** for status indicators
2. **Display font for headings only**, never for body text
3. **Maintain 8px grid** for consistent spacing
4. **Add hover states** to all interactive elements
5. **Use teal-700** for primary actions and headers
6. **Keep contrast ratios** above 4.5:1 for text