// Polyfill for browser globals
if (typeof self === 'undefined') {
  global.self = global as any
}

import React from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { EnhancedSprintReport as SprintReport } from './templates/EnhancedSprintReport'
import { ReportData } from './types'
import fs from 'fs'
import path from 'path'
import postcss from 'postcss'
import tailwindcssPostcss from '@tailwindcss/postcss'
import autoprefixer from 'autoprefixer'
import cssnano from 'cssnano'

export class ReportRenderer {
  private cssCache: string | null = null

  async generateHTML(data: ReportData): Promise<string> {
    // Render React component to HTML
    const reportHtml = renderToStaticMarkup(<SprintReport data={data} />)

    // Get CSS (with caching)
    const css = await this.getCSS()

    // Generate complete HTML document
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.projectName} - Sprint Radar Report</title>
    <style>
${css}
    </style>
    <script src="https://cdn.plot.ly/plotly-3.0.3.min.js"></script>
    <style>
        /* Additional print styles */
        @media print {
            @page {
                size: A4;
                margin: 20mm;
            }
            body {
                print-color-adjust: exact;
                -webkit-print-color-adjust: exact;
            }
            .print\\:hidden {
                display: none !important;
            }
            h1, h2, h3, h4, h5, h6 {
                page-break-after: avoid;
            }
            table {
                page-break-inside: avoid;
            }
            .no-page-break {
                page-break-inside: avoid;
            }
        }
        
        /* Ensure Plotly charts render properly */
        .js-plotly-plot {
            width: 100% !important;
            height: auto !important;
        }
        .js-plotly-plot .plotly {
            width: 100% !important;
        }
    </style>
</head>
<body>
    ${reportHtml}
    <script>
        // Store scenario chart data globally
        window.scenarioChartData = ${JSON.stringify(data.scenarioCharts || null)};
        
        // Store combined scenario data (normalized) like in legacy code
        window.scenarioData = ${data.combinedScenarioData ? JSON.stringify(data.combinedScenarioData) : 'null'};
        
        // Initialize Plotly charts after DOM load
        document.addEventListener('DOMContentLoaded', function() {
            // Find all chart containers
            const chartContainers = document.querySelectorAll('[data-plotly]');
            console.log('Found', chartContainers.length, 'chart containers');
            
            // Determine initial scenario (default to 'adjusted' to match backend)
            const initialScenario = window.scenarioChartData ? 'adjusted' : null;
            
            chartContainers.forEach(container => {
                const chartType = container.getAttribute('data-chart-type');
                let data, layout;
                
                // If we have scenario chart data, use it for supported chart types
                if (window.scenarioChartData && initialScenario && chartType && 
                    ['probability_distribution', 'forecast_timeline', 'confidence_intervals'].includes(chartType)) {
                    const scenarioData = window.scenarioChartData[initialScenario];
                    if (scenarioData && scenarioData[chartType]) {
                        data = scenarioData[chartType].data;
                        layout = scenarioData[chartType].layout;
                        console.log('Using scenario data for initial render of', chartType);
                    }
                }
                
                // Fallback to embedded data if scenario data not available
                if (!data) {
                    data = JSON.parse(container.getAttribute('data-plotly-data') || '[]');
                    layout = JSON.parse(container.getAttribute('data-plotly-layout') || '{}');
                }
                
                const config = JSON.parse(container.getAttribute('data-plotly-config') || '{}');
                
                if (data.length > 0) {
                    console.log('Initializing chart with data-chart-type:', chartType);
                    
                    // Configure for initial render
                    const initialConfig = {
                        ...config,
                        responsive: true,
                        displayModeBar: false
                    };
                    
                    Plotly.newPlot(container, data, layout, initialConfig);
                }
            });
            
            // Handle scenario switching
            const scenarioButtons = document.querySelectorAll('.scenario-btn');
            if (scenarioButtons.length > 0) {
                // Set initial button state to match the initial scenario
                if (initialScenario) {
                    scenarioButtons.forEach(btn => {
                        if (btn.getAttribute('data-scenario') === initialScenario) {
                            btn.classList.add('bg-white', 'text-teal-700', 'shadow-sm', 'active');
                            btn.classList.remove('text-gray-600', 'hover:text-gray-900');
                        }
                    });
                    
                    // Also ensure the correct scenario description is visible
                    document.querySelectorAll('.scenario-description').forEach(desc => {
                        if (desc.getAttribute('data-scenario') === initialScenario) {
                            desc.style.display = 'block';
                            desc.style.opacity = '1';
                        } else {
                            desc.style.display = 'none';
                            desc.style.opacity = '0';
                        }
                    });
                }
                
                scenarioButtons.forEach(btn => {
                    btn.addEventListener('click', function() {
                        const scenario = this.getAttribute('data-scenario');
                        
                        // Update button states
                        scenarioButtons.forEach(b => {
                            b.classList.remove('bg-white', 'text-teal-700', 'shadow-sm', 'active');
                            b.classList.add('text-gray-600', 'hover:text-gray-900');
                        });
                        this.classList.remove('text-gray-600', 'hover:text-gray-900');
                        this.classList.add('bg-white', 'text-teal-700', 'shadow-sm', 'active');
                        
                        // Update description visibility with fade transition
                        document.querySelectorAll('.scenario-description').forEach(desc => {
                            if (!desc.style.transition) {
                                desc.style.transition = 'opacity 0.3s ease-in-out';
                            }
                            
                            if (desc.getAttribute('data-scenario') === scenario) {
                                if (desc.style.display === 'none' || !desc.style.display) {
                                    desc.style.display = 'block';
                                    desc.style.opacity = '0';
                                    setTimeout(() => {
                                        desc.style.opacity = '1';
                                    }, 50);
                                }
                            } else {
                                desc.style.opacity = '0';
                                setTimeout(() => {
                                    desc.style.display = 'none';
                                }, 300);
                            }
                        });
                        
                        // Update all scenario-dependent content
                        updateScenarioContent(scenario);
                    });
                });
            }
        });
        
        // Function to update scenario-dependent content
        function updateScenarioContent(scenario) {
            // Add fade transition to all changing elements
            const allChangingElements = document.querySelectorAll('.scenario-value, [data-baseline-sprints][data-adjusted-sprints]');
            allChangingElements.forEach(elem => {
                elem.style.transition = 'opacity 0.3s ease-in-out';
                elem.style.opacity = '0.5';
            });
            
            // Update values after a short delay for smooth transition
            setTimeout(() => {
                // Find elements that should change based on scenario
                const scenarioElements = document.querySelectorAll('.scenario-value[data-baseline-value][data-adjusted-value]');
                scenarioElements.forEach(elem => {
                    const value = scenario === 'baseline' 
                        ? elem.getAttribute('data-baseline-value') 
                        : elem.getAttribute('data-adjusted-value');
                    elem.textContent = value;
                });
                
                // Update confidence intervals if they exist
                const confidenceElements = document.querySelectorAll('[data-baseline-sprints][data-adjusted-sprints]');
                confidenceElements.forEach(elem => {
                    const sprints = scenario === 'baseline' 
                        ? elem.getAttribute('data-baseline-sprints') 
                        : elem.getAttribute('data-adjusted-sprints');
                    elem.textContent = sprints + ' sprints';
                });
                
                // Fade elements back in
                allChangingElements.forEach(elem => {
                    elem.style.opacity = '1';
                });
                
                // Update charts with new data
                updateCharts(scenario);
            }, 150);
        }
        
        // Function to update charts based on scenario - following legacy pattern
        function updateCharts(scenario) {
            console.log('updateCharts called with scenario:', scenario);
            
            // Check if Plotly is loaded
            if (typeof Plotly === 'undefined') {
                console.error('Plotly is not loaded!');
                return;
            }
            
            // Update probability distribution chart
            updateProbabilityChart(scenario);
            
            // Update confidence intervals chart
            updateConfidenceChart(scenario);
            
            // Update forecast timeline chart
            updateForecastTimeline(scenario);
        }
        
        // Update probability distribution chart like legacy code
        function updateProbabilityChart(scenario) {
            const container = document.querySelector('[data-chart-type="probability_distribution"]');
            if (!container || !window.scenarioData) return;
            
            // Get data for both scenarios to determine consistent ranges
            const baselineData = window.scenarioData.baseline;
            const adjustedData = window.scenarioData.adjusted;
            
            // Find all unique sprint numbers for consistent x-axis
            const allSprints = new Set();
            if (baselineData && baselineData.probability_distribution) {
                baselineData.probability_distribution.forEach(d => allSprints.add(d.sprint));
            }
            if (adjustedData && adjustedData.probability_distribution) {
                adjustedData.probability_distribution.forEach(d => allSprints.add(d.sprint));
            }
            
            const sprintNumbers = Array.from(allSprints).sort((a, b) => a - b);
            const minSprint = Math.min(...sprintNumbers);
            const maxSprint = Math.max(...sprintNumbers);
            
            // Get current scenario data
            const data = window.scenarioData[scenario];
            if (!data || !data.probability_distribution) {
                console.warn('No probability distribution data for', scenario);
                return;
            }
            
            // Use the normalized data directly - backend already handles padding
            const sprints = data.probability_distribution.map(d => d.sprint);
            const probabilities = data.probability_distribution.map(d => d.probability);
            
            console.log('UpdateProbabilityChart for', scenario);
            console.log('Sprints:', sprints);
            console.log('Probabilities:', probabilities);
            
            // Calculate max y value across both scenarios for consistent scaling
            let maxProb = 0;
            if (baselineData && baselineData.probability_distribution) {
                const baselineMax = Math.max(...baselineData.probability_distribution.map(d => d.probability));
                maxProb = Math.max(maxProb, baselineMax);
            }
            if (adjustedData && adjustedData.probability_distribution) {
                const adjustedMax = Math.max(...adjustedData.probability_distribution.map(d => d.probability));
                maxProb = Math.max(maxProb, adjustedMax);
            }
            
            // Create the trace
            const trace = {
                x: sprints,
                y: probabilities,
                type: 'bar',
                name: 'Probability Distribution',
                marker: {
                    color: probabilities,
                    colorscale: [
                        [0, 'rgba(3, 86, 76, 0.3)'],
                        [0.5, 'rgba(3, 86, 76, 0.7)'],
                        [1, '#03564c']
                    ],
                    line: { color: 'rgba(255,255,255,0.8)', width: 2 }
                },
                text: probabilities.map(p => p > 0 ? (p * 100).toFixed(1) + '%' : ''),
                textposition: 'outside',
                hovertemplate: '<b>%{x} sprints</b><br>Probability: %{y:.1%}<extra></extra>'
            };
            
            // Use consistent ranges
            const xRange = [minSprint - 0.5, maxSprint + 0.5];
            const yRange = [0, maxProb * 1.2];
            
            // Create layout update
            const layoutUpdate = {
                xaxis: {
                    range: xRange,
                    dtick: 1
                },
                yaxis: {
                    range: yRange
                }
            };
            
            const config = { responsive: true, displayModeBar: false };
            
            try {
                const currentPlot = container._fullLayout;
                if (currentPlot) {
                    // Use the legacy animation sequence
                    Plotly.relayout(container, layoutUpdate).then(() => {
                        return Plotly.animate(container, {
                            data: [trace],
                            traces: [0]
                        }, {
                            transition: { duration: 750, easing: 'cubic-in-out' },
                            frame: { duration: 750 }
                        });
                    }).then(() => {
                        // Update text labels after animation
                        const finalText = probabilities.map(p => p > 0 ? (p * 100).toFixed(1) + '%' : '');
                        Plotly.restyle(container, { text: [finalText] }, [0]);
                    }).catch(error => {
                        console.error('Animation error:', error);
                        Plotly.react(container, [trace], layoutUpdate, config);
                    });
                } else {
                    // Initial plot - get full layout from scenario chart data
                    if (window.scenarioChartData && window.scenarioChartData[scenario]) {
                        const fullLayout = window.scenarioChartData[scenario].probability_distribution.layout;
                        Plotly.newPlot(container, [trace], fullLayout, config);
                    }
                }
            } catch (error) {
                console.error('Update probability chart error:', error);
            }
        }
        
        // Update confidence intervals chart
        function updateConfidenceChart(scenario) {
            const container = document.querySelector('[data-chart-type="confidence_intervals"]');
            if (!container || !window.scenarioChartData || !window.scenarioChartData[scenario]) return;
            
            const chartData = window.scenarioChartData[scenario].confidence_intervals;
            if (!chartData) return;
            
            const config = { responsive: true, displayModeBar: false };
            
            try {
                const currentPlot = container._fullLayout;
                if (currentPlot) {
                    Plotly.relayout(container, chartData.layout).then(() => {
                        return Plotly.animate(container, {
                            data: chartData.data,
                            traces: [0]
                        }, {
                            transition: { duration: 750, easing: 'cubic-in-out' }
                        });
                    });
                } else {
                    Plotly.newPlot(container, chartData.data, chartData.layout, config);
                }
            } catch (error) {
                console.error('Update confidence chart error:', error);
            }
        }
        
        // Update forecast timeline chart
        function updateForecastTimeline(scenario) {
            const container = document.querySelector('[data-chart-type="forecast_timeline"]');
            if (!container || !window.scenarioChartData || !window.scenarioChartData[scenario]) return;
            
            const chartData = window.scenarioChartData[scenario].forecast_timeline;
            if (!chartData) return;
            
            const config = { responsive: true, displayModeBar: false };
            
            try {
                // Timeline charts have multiple traces, so we need to handle differently
                Plotly.react(container, chartData.data, chartData.layout, config);
            } catch (error) {
                console.error('Update timeline chart error:', error);
            }
        }
    </script>
</body>
</html>`

    return html
  }

  private async getCSS(): Promise<string> {
    if (this.cssCache) {
      return this.cssCache
    }

    // Create a CSS file that imports Tailwind
    const cssInput = `
@import "tailwindcss";

/* Custom CSS Variables */
:root {
  --color-primary: #03564c;
  --color-secondary: #0E5473;
  --color-accent: #6B1229;
  --color-success: #00A86B;
  --color-warning: #FFA500;
  --color-danger: #DC143C;
  --color-primary-rgb: 3, 86, 76;
  --color-secondary-rgb: 14, 84, 115;
  --color-accent-rgb: 107, 18, 41;
}

@theme {
  --color-gray-50: #f9fafb;
  --color-gray-100: #f3f4f6;
  --color-gray-200: #e5e7eb;
  --color-gray-300: #d1d5db;
  --color-gray-400: #9ca3af;
  --color-gray-500: #6b7280;
  --color-gray-600: #4b5563;
  --color-gray-700: #374151;
  --color-gray-800: #1f2937;
  --color-gray-900: #111827;
  
  --color-primary-50: #e6f4f2;
  --color-primary-100: #cce9e5;
  --color-primary-200: #99d3ca;
  --color-primary-300: #66bcb0;
  --color-primary-400: #33a695;
  --color-primary-500: #03564c;
  --color-primary-600: #024840;
  --color-primary-700: #023a33;
  --color-primary-800: #022d2c;
  --color-primary-900: #011f1f;
  --color-primary-950: #001212;
  
  --color-teal-50: #e6f4f2;
  --color-teal-100: #cce9e5;
  --color-teal-200: #99d3ca;
  --color-teal-300: #66bcb0;
  --color-teal-400: #33a695;
  --color-teal-500: #03564c;
  --color-teal-600: #024840;
  --color-teal-700: #023a33;
  --color-teal-800: #022d2c;
  --color-teal-900: #011f1f;
  
  --color-burgundy-50: #fdf2f4;
  --color-burgundy-100: #fbe5e9;
  --color-burgundy-200: #f6ccd4;
  --color-burgundy-300: #f2b2be;
  --color-burgundy-400: #ed99a9;
  --color-burgundy-500: #e97f93;
  --color-burgundy-600: #e4667e;
  --color-burgundy-700: #b83355;
  --color-burgundy-800: #8c1a3a;
  --color-burgundy-900: #6B1229;
  
  --color-cerulean-50: #e6f3f8;
  --color-cerulean-100: #cce7f1;
  --color-cerulean-200: #99cfe3;
  --color-cerulean-300: #66b7d5;
  --color-cerulean-400: #339fc7;
  --color-cerulean-500: #0E5473;
  --color-cerulean-600: #0b445e;
  --color-cerulean-700: #09354a;
  --color-cerulean-800: #072635;
  --color-cerulean-900: #041720;
  
  --color-emerald-50: #f0fdf9;
  --color-emerald-100: #ccfbea;
  --color-emerald-200: #9af5d7;
  --color-emerald-300: #5fe9bf;
  --color-emerald-400: #2dd4a2;
  --color-emerald-500: #14b885;
  --color-emerald-600: #0d9668;
  
  --color-rose-400: #fb7185;
  --color-rose-500: #f43f5e;
  --color-rose-600: #e11d48;
  
  --color-amber-500: #f59e0b;
  --color-amber-600: #d97706;
  
  --color-orange-50: #fff8e6;
  --color-orange-100: #fff1cc;
  --color-orange-200: #ffe399;
  --color-orange-300: #ffd566;
  --color-orange-400: #ffc733;
  --color-orange-500: #FFA500;
  --color-orange-600: #cc8400;
  --color-orange-700: #996300;
  --color-orange-800: #664200;
  --color-orange-900: #332100;
  
  --color-violet-500: #8b5cf6;
  
  --color-red-50: #fef2f2;
  --color-red-100: #fee2e2;
  --color-red-200: #fecaca;
  --color-red-300: #fca5a5;
  --color-red-400: #f87171;
  --color-red-500: #ef4444;
  --color-red-600: #dc2626;
  --color-red-700: #b91c1c;
  --color-red-800: #991b1b;
  --color-red-900: #7f1d1d;
  
  --color-green-50: #f0fdf4;
  --color-green-100: #dcfce7;
  --color-green-200: #bbf7d0;
  --color-green-300: #86efac;
  --color-green-400: #4ade80;
  --color-green-500: #22c55e;
  --color-green-600: #16a34a;
  --color-green-700: #15803d;
  --color-green-800: #166534;
  --color-green-900: #14532d;
  
  --color-blue-50: #eff6ff;
  --color-blue-100: #dbeafe;
  --color-blue-200: #bfdbfe;
  --color-blue-300: #93c5fd;
  --color-blue-400: #60a5fa;
  --color-blue-500: #3b82f6;
  --color-blue-600: #2563eb;
  --color-blue-700: #1d4ed8;
  --color-blue-800: #1e40af;
  --color-blue-900: #1e3a8a;
  
  --color-yellow-50: #fefce8;
  --color-yellow-100: #fef3c7;
  --color-yellow-200: #fde68a;
  --color-yellow-300: #fcd34d;
  --color-yellow-400: #fbbf24;
  --color-yellow-500: #f59e0b;
  --color-yellow-600: #d97706;
  --color-yellow-700: #b45309;
  --color-yellow-800: #92400e;
  --color-yellow-900: #78350f;
}
`

    // Process with PostCSS
    const result = await postcss([
      tailwindcssPostcss(),
      autoprefixer(),
      cssnano({ preset: 'default' }),
    ]).process(cssInput, { from: undefined })

    this.cssCache = result.css
    return this.cssCache
  }

}