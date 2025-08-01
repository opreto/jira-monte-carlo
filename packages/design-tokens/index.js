const tokens = require('./tokens.json')
const tailwindPreset = require('./tailwind-preset')

module.exports = {
  tokens,
  tailwindPreset,
  // Export specific token groups for easier access
  colors: tokens['sprint-radar'].color,
  spacing: tokens['sprint-radar'].spacing,
  typography: tokens['sprint-radar'].typography,
  borderRadius: tokens['sprint-radar'].borderRadius,
  shadows: tokens['sprint-radar'].shadow,
  transitions: tokens['sprint-radar'].transition,
  breakpoints: tokens['sprint-radar'].breakpoint
}