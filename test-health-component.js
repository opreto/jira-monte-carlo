// Test script to render ProcessHealthBreakdown component in isolation
const React = require('react');
const { renderToString } = require('react-dom/server');

// Simplified ProcessHealthBreakdown component
const ProcessHealthBreakdown = ({ healthMetrics }) => {
  if (!healthMetrics.health_score_breakdown || healthMetrics.health_score_breakdown.length === 0) {
    return React.createElement('div', null, 'No breakdown data');
  }
  
  console.log('Rendering', healthMetrics.health_score_breakdown.length, 'components');
  
  return React.createElement('div', null,
    healthMetrics.health_score_breakdown.map((component, index) => {
      console.log(`Rendering component ${index}: ${component.name}`);
      
      try {
        return React.createElement('div', { key: index },
          React.createElement('h4', null, component.name),
          React.createElement('span', null, `${Math.round(component.score * 100)}%`),
          React.createElement('p', null, component.description),
          
          // Insights
          component.insights && component.insights.length > 0 && 
            React.createElement('ul', null,
              component.insights.map((insight, i) => 
                React.createElement('li', { key: i }, insight)
              )
            ),
          
          // Detail items
          component.detail_items && component.detail_items.length > 0 &&
            React.createElement('details', null,
              React.createElement('summary', null, `View ${component.detail_items.length} items`),
              React.createElement('div', null, 
                component.detail_items.map((item, i) =>
                  React.createElement('div', { key: i }, 
                    `${item.key}: ${item.summary} (${item.age_days} days)`
                  )
                )
              )
            )
        );
      } catch (error) {
        console.error(`Error rendering component ${index}:`, error);
        return React.createElement('div', { key: index }, `Error: ${error.message}`);
      }
    })
  );
};

// Test data
const testData = {
  health_score_breakdown: [
    {
      name: "Aging Items",
      score: 0.2,
      description: "Based on 16 critical items out of 40 total",
      insights: ["16 items (40%) are stale or abandoned"],
      recommendations: ["Review and prioritize stale items"],
      detail_items: [
        { key: "PARA-62", summary: "Test item", age_days: 254, status: "To Do", assignee: "Unassigned", type: "abandoned" }
      ]
    },
    {
      name: "Work In Progress",
      score: 1.0,
      description: "3 items in progress, 0 WIP limit violations",
      insights: ["Team size: 3 active members", "All WIP limits are being respected"],
      recommendations: [],
      detail_items: null
    },
    {
      name: "Sprint Predictability",
      score: 0.869,
      description: "Based on 10 recent sprints",
      insights: ["Average completion rate: 77%", "Completion rate improving by 6.3% per sprint"],
      recommendations: [],
      detail_items: null
    }
  ]
};

// Test rendering
try {
  console.log('Starting render test...');
  const html = renderToString(React.createElement(ProcessHealthBreakdown, { healthMetrics: testData }));
  console.log('Render successful!');
  console.log('HTML length:', html.length);
  console.log('\nFirst 500 chars:');
  console.log(html.substring(0, 500));
} catch (error) {
  console.error('Render failed:', error);
  console.error(error.stack);
}