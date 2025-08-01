import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './.storybook/**/*.{js,ts,jsx,tsx}',
    './stories/**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/ui/src/**/*.{js,ts,jsx,tsx}',
    '../web/src/**/*.{js,ts,jsx,tsx}',
  ],
  presets: [
    require('@sprint-radar/design-tokens/tailwind-preset')
  ],
  theme: {
    extend: {
      colors: {
        // Add background and foreground colors for compatibility
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
        muted: {
          DEFAULT: 'var(--color-text-muted)',
          foreground: 'var(--color-text-muted)',
        },
      },
    },
  },
  plugins: [],
}

export default config