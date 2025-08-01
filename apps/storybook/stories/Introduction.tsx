import React from 'react';

export default {
  title: 'Introduction',
};

export const Welcome = () => (
  <div className="max-w-4xl mx-auto p-8">
    <h1 className="text-4xl font-bold text-gray-900 mb-4">Sprint Radar Design System</h1>
    
    <p className="text-lg text-gray-600 mb-8">
      Welcome to the Sprint Radar Design System documentation!
    </p>
    
    <h2 className="text-2xl font-semibold text-gray-800 mb-3">Overview</h2>
    <p className="text-gray-600 mb-6">
      This design system provides a comprehensive set of components, tokens, and patterns for building consistent and accessible user interfaces across the Sprint Radar platform.
    </p>
    
    <h3 className="text-xl font-semibold text-gray-800 mb-3">Design Principles</h3>
    <ul className="list-disc list-inside space-y-2 text-gray-600 mb-6">
      <li><strong>Mobile-First</strong>: Every component is designed to work beautifully on mobile devices first</li>
      <li><strong>Accessible</strong>: WCAG AA compliant with proper contrast ratios and keyboard navigation</li>
      <li><strong>Themeable</strong>: Full support for light and dark modes with system preference detection</li>
      <li><strong>Performance</strong>: Optimized for fast loading and smooth interactions</li>
    </ul>
    
    <h3 className="text-xl font-semibold text-gray-800 mb-3">Getting Started</h3>
    <p className="text-gray-600 mb-4">
      Browse the components in the sidebar to see interactive examples and documentation.
    </p>
    <p className="text-gray-600 mb-6">
      Each component includes:
    </p>
    <ul className="list-disc list-inside space-y-2 text-gray-600 mb-6">
      <li>Live examples with controls</li>
      <li>Code snippets</li>
      <li>Props documentation</li>
      <li>Accessibility guidelines</li>
    </ul>
    
    <h3 className="text-xl font-semibold text-gray-800 mb-3">Tech Stack</h3>
    <ul className="list-disc list-inside space-y-2 text-gray-600">
      <li><strong>React 19</strong> - UI library</li>
      <li><strong>TypeScript</strong> - Type safety</li>
      <li><strong>Tailwind CSS v4</strong> - Utility-first styling</li>
      <li><strong>Radix UI</strong> - Accessible primitives</li>
      <li><strong>CVA</strong> - Variant management</li>
      <li><strong>Vite</strong> - Build tool</li>
    </ul>
  </div>
);