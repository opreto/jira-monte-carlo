// Scenario switching functionality for combined reports

// Function to switch between scenarios
function switchScenario(scenario) {
    window.currentScenario = scenario;
    
    // Update UI elements
    updateScenarioDisplay();
    
    // Update all charts
    updateCharts();
}

function updateScenarioDisplay() {
    const descriptionEl = document.getElementById('scenario-description');
    const baselineNotice = document.getElementById('baseline-notice');
    
    // Add smooth transitions for the UI elements
    [descriptionEl, baselineNotice].forEach(el => {
        if (el) {
            el.style.transition = 'opacity 0.3s ease-in-out';
        }
    });
    
    if (window.currentScenario === 'baseline') {
        // Fade out description, then hide and show baseline notice
        if (descriptionEl) {
            descriptionEl.style.opacity = '0';
            setTimeout(() => {
                descriptionEl.style.display = 'none';
                if (baselineNotice) {
                    baselineNotice.style.display = 'block';
                    baselineNotice.style.opacity = '0';
                    setTimeout(() => baselineNotice.style.opacity = '1', 50);
                }
            }, 300);
        }
    } else {
        // Fade out baseline notice, then hide and show description
        if (baselineNotice) {
            baselineNotice.style.opacity = '0';
            setTimeout(() => {
                baselineNotice.style.display = 'none';
                if (descriptionEl) {
                    descriptionEl.style.display = 'block';
                    descriptionEl.style.opacity = '0';
                    setTimeout(() => descriptionEl.style.opacity = '1', 50);
                }
            }, 300);
        }
    }
    
    // Update summary metrics
    updateSummaryMetrics();
}

function updateSummaryMetrics() {
    const data = window.scenarioData[window.currentScenario];
    if (!data) return;
    
    // Update percentile values in summary
    const percentiles = data.percentiles;
    updateTextContent('p50-value', percentiles.p50 + ' sprints');
    updateTextContent('p70-value', percentiles.p70 + ' sprints');
    updateTextContent('p85-value', percentiles.p85 + ' sprints');
    updateTextContent('p95-value', percentiles.p95 + ' sprints');
}

function updateTextContent(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}

function updateCharts() {
    // Update each chart with new data
    updateProbabilityChart();
    updateConfidenceChart();
    updateForecastTimeline();
    updateSummaryTable();
}

function updateProbabilityChart() {
    const chartDiv = document.getElementById('probability-distribution');
    if (!chartDiv) return;
    
    // Get data for both scenarios to determine consistent ranges
    const baselineData = window.scenarioData.baseline;
    const adjustedData = window.scenarioData.adjusted;
    
    // Find the union of all sprint numbers
    const allSprints = new Set();
    if (baselineData && baselineData.probability_distribution) {
        baselineData.probability_distribution.forEach(d => allSprints.add(d.sprint));
    }
    if (adjustedData && adjustedData.probability_distribution) {
        adjustedData.probability_distribution.forEach(d => allSprints.add(d.sprint));
    }
    
    // Create a consistent x-axis from min to max sprint
    const sprintNumbers = Array.from(allSprints).sort((a, b) => a - b);
    const minSprint = Math.min(...sprintNumbers);
    const maxSprint = Math.max(...sprintNumbers);
    const fullSprintRange = [];
    for (let i = minSprint; i <= maxSprint; i++) {
        fullSprintRange.push(i);
    }
    
    // Get current scenario data
    const data = window.scenarioData[window.currentScenario];
    if (!data || !data.probability_distribution) {
        console.warn('No probability distribution data for', window.currentScenario);
        return;
    }
    
    // Create a map for quick lookup
    const probMap = new Map();
    data.probability_distribution.forEach(d => {
        probMap.set(d.sprint, d.probability);
    });
    
    // Build arrays with consistent x-axis, using 0 for missing values
    const sprints = fullSprintRange;
    const probabilities = sprints.map(s => probMap.get(s) || 0);
    
    // Calculate max y value across both scenarios
    let maxProb = 0;
    if (baselineData && baselineData.probability_distribution) {
        const baselineMax = Math.max(...baselineData.probability_distribution.map(d => d.probability));
        maxProb = Math.max(maxProb, baselineMax);
    }
    if (adjustedData && adjustedData.probability_distribution) {
        const adjustedMax = Math.max(...adjustedData.probability_distribution.map(d => d.probability));
        maxProb = Math.max(maxProb, adjustedMax);
    }
    
    // Get previous data to check which bars are appearing/disappearing
    const prevData = chartDiv.data && chartDiv.data[0] ? chartDiv.data[0] : null;
    const prevY = prevData ? prevData.y : [];
    
    // Determine which bars are transitioning from/to zero
    const showText = probabilities.map((p, i) => {
        const prevValue = i < prevY.length ? prevY[i] : 0;
        // Hide text if transitioning from 0 or to 0
        return (prevValue > 0 && p > 0);
    });
    
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
            line: { color: 'rgba(255,255,255,0.8)', width: 2 },
            opacity: 0.9
        },
        text: probabilities.map((p, i) => {
            if (p > 0 && showText[i]) {
                return `${(p * 100).toFixed(1)}%`;
            }
            return '';
        }),
        textposition: 'outside',
        textfont: { 
            size: 12, 
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        },
        hovertemplate: '<b>%{x} sprints</b><br>Probability: %{y:.1%}<extra></extra>'
    };
    
    // Get the current layout
    const currentLayout = chartDiv.layout || {};
    
    // Use consistent ranges
    const xRange = [minSprint - 0.5, maxSprint + 0.5];
    const yRange = [0, maxProb * 1.2];
    
    // Update the layout with new ranges
    const layoutUpdate = {
        xaxis: {
            range: xRange,
            autorange: false,
            title: currentLayout.xaxis ? currentLayout.xaxis.title : undefined
        },
        yaxis: {
            range: yRange,
            autorange: false,
            title: currentLayout.yaxis ? currentLayout.yaxis.title : undefined
        }
    };
    
    // First update the layout to prevent rescaling
    Plotly.relayout(chartDiv, layoutUpdate);
    
    // Then animate the data change
    Plotly.animate(chartDiv, {
        data: [trace],
        traces: [0]
    }, {
        transition: {
            duration: 750,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 750,
            redraw: false
        }
    }).then(() => {
        // After animation completes, show all text labels for non-zero bars
        const finalText = probabilities.map(p => p > 0 ? `${(p * 100).toFixed(1)}%` : '');
        Plotly.restyle(chartDiv, { text: [finalText] }, [0]);
    });
}

function updateConfidenceChart() {
    const data = window.scenarioData[window.currentScenario];
    if (!data || !data.confidence_intervals || data.confidence_intervals.length === 0) {
        console.warn('No confidence interval data for', window.currentScenario);
        return;
    }
    
    const chartDiv = document.getElementById('confidence-intervals');
    if (!chartDiv) return;
    
    // Extract data
    const confidenceData = data.confidence_intervals;
    const labels = confidenceData.map(d => `${d.level}%`);
    const sprints = confidenceData.map(d => d.value);
    
    // Color based on confidence level
    const colors = confidenceData.map(d => {
        if (d.level <= 50) return '#DC143C';  // Red - Aggressive
        else if (d.level <= 85) return '#FFA500';  // Amber - Moderate
        else return '#00A86B';  // Green - Conservative
    });
    
    const trace = {
        x: labels,
        y: sprints,
        type: 'bar',
        marker: {
            color: colors,
            line: { color: 'white', width: 2 }
        },
        text: sprints.map(s => `<b>${s.toFixed(0)} sprints</b>`),
        textposition: 'auto',
        textfont: { size: 14, color: 'white' },
        hovertemplate: '<b>%{x} Confidence</b><br>Sprints: %{y:.0f}<extra></extra>'
    };
    
    // Calculate max value across both scenarios for consistent scaling
    let maxSprintsGlobal = 10;
    const baselineData = window.scenarioData.baseline;
    const adjustedData = window.scenarioData.adjusted;
    
    if (baselineData && baselineData.confidence_intervals) {
        const baselineMax = Math.max(...baselineData.confidence_intervals.map(d => d.value));
        maxSprintsGlobal = Math.max(maxSprintsGlobal, baselineMax);
    }
    if (adjustedData && adjustedData.confidence_intervals) {
        const adjustedMax = Math.max(...adjustedData.confidence_intervals.map(d => d.value));
        maxSprintsGlobal = Math.max(maxSprintsGlobal, adjustedMax);
    }
    
    // Calculate appropriate dtick based on max value
    let dtick = 1;
    if (maxSprintsGlobal > 20) dtick = 5;
    if (maxSprintsGlobal > 50) dtick = 10;
    if (maxSprintsGlobal > 100) dtick = 20;
    if (maxSprintsGlobal > 200) dtick = 50;
    
    // Get the current layout
    const currentLayout = chartDiv.layout || {};
    
    // Use consistent y range across scenarios
    const yRange = [0, maxSprintsGlobal * 1.1];
    
    // Update the layout
    const layoutUpdate = {
        xaxis: {
            title: currentLayout.xaxis ? currentLayout.xaxis.title : undefined
        },
        yaxis: {
            tickmode: 'linear',
            tick0: 0,
            dtick: dtick,
            range: yRange,
            autorange: false,
            title: currentLayout.yaxis ? currentLayout.yaxis.title : undefined
        }
    };
    
    // First update the layout to prevent rescaling
    Plotly.relayout(chartDiv, layoutUpdate);
    
    // Then animate the data change
    Plotly.animate(chartDiv, {
        data: [trace],
        traces: [0]
    }, {
        transition: {
            duration: 750,
            easing: 'cubic-in-out'
        },
        frame: {
            duration: 750,
            redraw: false
        }
    });
}

function updateForecastTimeline() {
    // Similar updates for forecast timeline
    // Implementation depends on the specific chart structure
}

function updateSummaryTable() {
    const data = window.scenarioData[window.currentScenario];
    if (!data || !data.summary_stats) {
        console.warn('No summary stats for', window.currentScenario);
        return;
    }
    
    const tbody = document.querySelector('.summary-table tbody');
    if (!tbody) return;
    
    // Clear existing rows
    tbody.innerHTML = '';
    
    // Add new rows
    for (const [level, stats] of Object.entries(data.summary_stats)) {
        const row = document.createElement('tr');
        row.className = stats.class;
        row.innerHTML = `
            <td>${level}</td>
            <td>${stats.sprints} sprints</td>
            <td>${stats.date}</td>
            <td>${stats.probability}% chance of completing by this date</td>
        `;
        tbody.appendChild(row);
    }
}

// Function to fix initial chart rendering
function fixInitialCharts() {
    // Update probability chart to use consistent ranges
    const probDiv = document.getElementById('probability-distribution');
    if (probDiv && probDiv.data) {
        updateProbabilityChart();
    }
    
    // Update confidence chart to use consistent ranges
    const confDiv = document.getElementById('confidence-intervals');
    if (confDiv && confDiv.data) {
        updateConfidenceChart();
    }
}

// Initialize on page load  
document.addEventListener('DOMContentLoaded', function() {
    // Wait for charts to be rendered by Plotly
    let checkInterval = setInterval(function() {
        const probDiv = document.getElementById('probability-distribution');
        const confDiv = document.getElementById('confidence-intervals');
        
        // Check if Plotly has finished rendering the charts
        if (probDiv && probDiv.data && confDiv && confDiv.data) {
            clearInterval(checkInterval);
            
            // Initialize display and fix charts
            if (window.scenarioData) {
                updateScenarioDisplay();
                
                // Fix the initial charts to use consistent ranges
                setTimeout(fixInitialCharts, 100);
            }
        }
    }, 100);
});