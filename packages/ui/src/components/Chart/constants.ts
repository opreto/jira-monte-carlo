export const chartColors = {
  primary: [
    '#14b885', // primary-500 - vibrant emerald
    '#0d9668', // primary-600
    '#0f7655', // primary-700
    '#2dd4a2', // primary-400
    '#5fe9bf', // primary-300
  ],
  categorical: [
    '#14b885', // emerald - primary
    '#8b5cf6', // violet
    '#ec4899', // pink
    '#3b82f6', // blue
    '#14b8a6', // teal
    '#f97316', // orange
    '#84cc16', // lime
    '#6366f1', // indigo
  ],
  sequential: {
    green: ['#f0fdf4', '#dcfce7', '#bbf7d0', '#86efac', '#4ade80', '#22c55e', '#16a34a', '#15803d', '#14532d'],
    blue: ['#eff6ff', '#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6', '#2563eb', '#1d4ed8', '#1e3a8a'],
    red: ['#fef2f2', '#fee2e2', '#fecaca', '#fca5a5', '#f87171', '#ef4444', '#dc2626', '#b91c1c', '#7f1d1d'],
  },
  diverging: [
    '#7f1d1d', // red-900
    '#dc2626', // red-600
    '#f87171', // red-400
    '#fecaca', // red-200
    '#f9fafb', // gray-50
    '#bfdbfe', // blue-200
    '#3b82f6', // blue-500
    '#1d4ed8', // blue-700
    '#1e3a8a', // blue-900
  ],
}

export const chartLayouts = {
  timeSeries: {
    xaxis: {
      type: 'date' as const,
      tickformat: '%Y-%m-%d',
      showgrid: true,
      gridcolor: '#f3f4f6',
      zerolinecolor: '#e5e7eb',
    },
    yaxis: {
      showgrid: true,
      gridcolor: '#f3f4f6',
      zerolinecolor: '#e5e7eb',
    },
  },
  bar: {
    xaxis: {
      showgrid: false,
      zerolinecolor: '#e5e7eb',
    },
    yaxis: {
      showgrid: true,
      gridcolor: '#f3f4f6',
      zerolinecolor: '#e5e7eb',
    },
    bargap: 0.15,
    bargroupgap: 0.1,
  },
  pie: {
    showlegend: true,
    legend: {
      orientation: 'v' as const,
      x: 1.02,
      y: 0.5,
    },
  },
  scatter: {
    xaxis: {
      showgrid: true,
      gridcolor: '#f3f4f6',
      zerolinecolor: '#e5e7eb',
    },
    yaxis: {
      showgrid: true,
      gridcolor: '#f3f4f6',
      zerolinecolor: '#e5e7eb',
    },
  },
  histogram: {
    bargap: 0.1,
    xaxis: {
      showgrid: false,
    },
    yaxis: {
      showgrid: true,
      gridcolor: '#f3f4f6',
    },
  },
}