import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.tsx'],
  format: ['cjs', 'esm'],
  dts: true,
  external: ['react', 'react-dom'],
  clean: true,
  sourcemap: true,
  minify: process.env.NODE_ENV === 'production',
})