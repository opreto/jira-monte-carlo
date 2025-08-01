// Polyfill for browser globals
if (typeof self === 'undefined') {
  global.self = global as any
}
if (typeof window === 'undefined') {
  global.window = global as any
}
if (typeof document === 'undefined') {
  global.document = { createElement: () => ({}) } as any
}

export { ReportRenderer } from './renderer'
export * from './types'