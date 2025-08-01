const tokens = require('./tokens.json')

// Helper to extract token values
const extractTokenValues = (tokenGroup) => {
  const values = {}
  Object.entries(tokenGroup).forEach(([key, token]) => {
    if (token.value) {
      values[key] = token.value
    } else {
      values[key] = extractTokenValues(token)
    }
  })
  return values
}

module.exports = {
  theme: {
    extend: {
      colors: {
        // Base colors
        gray: extractTokenValues(tokens['sprint-radar'].color.base.gray),
        primary: extractTokenValues(tokens['sprint-radar'].color.base.primary),
        success: extractTokenValues(tokens['sprint-radar'].color.base.success),
        warning: extractTokenValues(tokens['sprint-radar'].color.base.warning),
        error: extractTokenValues(tokens['sprint-radar'].color.base.error),
        
        // Semantic colors (will need custom plugin for light/dark)
        background: {
          DEFAULT: 'var(--color-background)',
          surface: 'var(--color-background-surface)',
          elevated: 'var(--color-background-elevated)',
        },
        foreground: {
          DEFAULT: 'var(--color-text-primary)',
          secondary: 'var(--color-text-secondary)',
          muted: 'var(--color-text-muted)',
        },
        border: {
          DEFAULT: 'var(--color-border)',
          focus: 'var(--color-border-focus)',
        },
        
        // Chart colors
        chart: {
          'confidence-high': tokens['sprint-radar'].color.semantic.chart.confidence.high.value,
          'confidence-medium': tokens['sprint-radar'].color.semantic.chart.confidence.medium.value,
          'confidence-low': tokens['sprint-radar'].color.semantic.chart.confidence.low.value,
          'data-1': tokens['sprint-radar'].color.semantic.chart.data['1'].value,
          'data-2': tokens['sprint-radar'].color.semantic.chart.data['2'].value,
          'data-3': tokens['sprint-radar'].color.semantic.chart.data['3'].value,
          'data-4': tokens['sprint-radar'].color.semantic.chart.data['4'].value,
          'data-5': tokens['sprint-radar'].color.semantic.chart.data['5'].value,
        }
      },
      
      spacing: extractTokenValues(tokens['sprint-radar'].spacing),
      
      fontFamily: {
        sans: tokens['sprint-radar'].typography.fontFamily.sans.value,
        mono: tokens['sprint-radar'].typography.fontFamily.mono.value,
      },
      
      fontSize: Object.entries(tokens['sprint-radar'].typography.fontSize).reduce((acc, [key, value]) => {
        acc[key] = [value.value, { lineHeight: value.lineHeight }]
        return acc
      }, {}),
      
      fontWeight: extractTokenValues(tokens['sprint-radar'].typography.fontWeight),
      
      borderRadius: extractTokenValues(tokens['sprint-radar'].borderRadius),
      
      boxShadow: extractTokenValues(tokens['sprint-radar'].shadow),
      
      transitionDuration: extractTokenValues(tokens['sprint-radar'].transition),
      
      screens: extractTokenValues(tokens['sprint-radar'].breakpoint),
    },
  },
  
  plugins: [
    // Plugin to generate CSS variables from tokens
    function({ addBase }) {
      addBase({
        ':root': {
          // Light mode variables
          '--color-background': tokens['sprint-radar'].color.semantic.background.default.light.value,
          '--color-background-surface': tokens['sprint-radar'].color.semantic.background.surface.light.value,
          '--color-background-elevated': tokens['sprint-radar'].color.semantic.background.elevated.light.value,
          '--color-text-primary': tokens['sprint-radar'].color.semantic.text.primary.light.value,
          '--color-text-secondary': tokens['sprint-radar'].color.semantic.text.secondary.light.value,
          '--color-text-muted': tokens['sprint-radar'].color.semantic.text.muted.light.value,
          '--color-border': tokens['sprint-radar'].color.semantic.border.default.light.value,
          '--color-border-focus': tokens['sprint-radar'].color.semantic.border.focus.light.value,
        },
        
        // Dark mode
        '@media (prefers-color-scheme: dark)': {
          ':root': {
            '--color-background': tokens['sprint-radar'].color.semantic.background.default.dark.value,
            '--color-background-surface': tokens['sprint-radar'].color.semantic.background.surface.dark.value,
            '--color-background-elevated': tokens['sprint-radar'].color.semantic.background.elevated.dark.value,
            '--color-text-primary': tokens['sprint-radar'].color.semantic.text.primary.dark.value,
            '--color-text-secondary': tokens['sprint-radar'].color.semantic.text.secondary.dark.value,
            '--color-text-muted': tokens['sprint-radar'].color.semantic.text.muted.dark.value,
            '--color-border': tokens['sprint-radar'].color.semantic.border.default.dark.value,
            '--color-border-focus': tokens['sprint-radar'].color.semantic.border.focus.dark.value,
          }
        },
        
        // Print mode
        '@media print': {
          ':root': {
            '--color-background': '#ffffff',
            '--color-background-surface': '#ffffff',
            '--color-background-elevated': '#ffffff',
            '--color-text-primary': '#000000',
            '--color-text-secondary': '#4b5563',
            '--color-text-muted': '#6b7280',
            '--color-border': '#e5e7eb',
            '--color-border-focus': '#000000',
          }
        }
      })
    }
  ],
}