import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/cli.ts', 'src/index.ts'],
  format: ['cjs'],
  dts: false, // Skip TypeScript declarations for now
  shims: true,
  skipNodeModulesBundle: true,
  clean: true,
  target: 'node18',
})