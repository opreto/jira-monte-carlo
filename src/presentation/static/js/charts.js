// Chart initialization and handling for Sprint Radar reports

// Store chart data globally for toggling
let storySizeCharts = {};
let currentChartType = 'bar';

// Initialize all charts
function initializeCharts(chartData, processHealthChartData) {
    // Render main charts
    for (const [chartId, data] of Object.entries(chartData)) {
        try {
            if (chartId === 'story_size_breakdown') {
                // Special handling for story size breakdown with multiple chart types
                storySizeCharts = {
                    pie: data.pie,
                    bar: data.bar
                };
                
                // Render initial bar chart
                if (storySizeCharts.bar) {
                    const barData = storySizeCharts.bar;
                    Plotly.newPlot('story-size-breakdown', barData.data, barData.layout, {responsive: true});
                }
            } else {
                // Regular chart rendering
                const elementId = chartId.replace(/_/g, '-');
                Plotly.newPlot(elementId, data.data, data.layout, {responsive: true});
            }
        } catch (e) {
            console.error(`Error rendering chart ${chartId}:`, e);
        }
    }
    
    // Render process health charts
    for (const [chartId, data] of Object.entries(processHealthChartData)) {
        try {
            const elementId = chartId.replace(/_/g, '-');
            Plotly.newPlot(elementId, data.data, data.layout, {responsive: true});
        } catch (e) {
            console.error(`Error rendering process health chart ${chartId}:`, e);
        }
    }
}

// Toggle function for chart type
function toggleChartType(type) {
    if (type === currentChartType || !storySizeCharts[type]) return;
    
    // Store current scroll position
    const scrollPosition = window.scrollY;
    
    // Update button states
    document.getElementById('pie-toggle').classList.toggle('active', type === 'pie');
    document.getElementById('bar-toggle').classList.toggle('active', type === 'bar');
    
    // Get chart data
    const chartData = storySizeCharts[type];
    
    // Get container and lock its height
    const container = document.getElementById('story-size-breakdown');
    const containerHeight = container.offsetHeight;
    container.style.height = containerHeight + 'px';
    container.style.opacity = '0';
    
    setTimeout(() => {
        // Update chart
        Plotly.react('story-size-breakdown', chartData.data, chartData.layout, {responsive: true});
        
        // Fade in and restore height to auto
        container.style.opacity = '1';
        setTimeout(() => {
            container.style.height = 'auto';
            // Restore scroll position
            window.scrollTo(0, scrollPosition);
        }, 50);
        currentChartType = type;
    }, 300);
}