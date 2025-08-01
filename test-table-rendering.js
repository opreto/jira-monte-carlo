// Test rendering the actual Table components
const React = require('react');
const { renderToString } = require('react-dom/server');

// Mock Table components (simplified versions)
const Table = ({ children, className }) => React.createElement('table', { className: className || "min-w-full divide-y divide-gray-200" }, children);
const TableHeader = ({ children }) => React.createElement('thead', { className: "bg-gray-50" }, children);
const TableBody = ({ children }) => React.createElement('tbody', { className: "bg-white divide-y divide-gray-200" }, children);
const TableRow = ({ children, className }) => React.createElement('tr', { className: className || "transition-all duration-150 hover:bg-teal-50/20 hover:shadow-sm" }, children);
const TableHead = ({ children }) => React.createElement('th', { className: "px-6 py-3 text-left text-xs font-medium font-sans text-gray-700 uppercase tracking-wider" }, children);
const TableCell = ({ children }) => React.createElement('td', { className: "px-6 py-4 whitespace-nowrap text-sm font-sans text-gray-900" }, children);

// Test data - actual Aging Items detail_items
const detailItems = [
  {
    "key": "PARA-62",
    "summary": "Enforce a consistent UI style",
    "age_days": 254,
    "status": "To Do",
    "assignee": "Unassigned",
    "type": "abandoned"
  },
  {
    "key": "PARA-68",
    "summary": "Highlight currently running simulation step in Blockly",
    "age_days": 246,
    "status": "To Do",
    "assignee": "Unassigned",
    "type": "abandoned"
  }
];

// Test rendering the table
try {
  console.log('Testing table rendering...');
  
  const tableElement = React.createElement(Table, null,
    React.createElement(TableHeader, null,
      React.createElement(TableRow, null,
        React.createElement(TableHead, null, 'Key'),
        React.createElement(TableHead, null, 'Summary'),
        React.createElement(TableHead, null, 'Age'),
        React.createElement(TableHead, null, 'Status'),
        React.createElement(TableHead, null, 'Assignee')
      )
    ),
    React.createElement(TableBody, null,
      detailItems.map((item, i) => {
        console.log(`Rendering row ${i}: ${item.key}`);
        
        return React.createElement(TableRow, { key: i },
          React.createElement(TableCell, null,
            React.createElement('span', { className: "text-teal-600 font-medium" }, item.key)
          ),
          React.createElement(TableCell, null,
            item.summary.length > 50 ? item.summary.substring(0, 50) + '...' : item.summary
          ),
          React.createElement(TableCell, null, `${item.age_days} days`),
          React.createElement(TableCell, null,
            React.createElement('span', { 
              className: `px-2 py-1 rounded-full text-xs font-medium ${
                item.type === 'abandoned' ? 'bg-red-100 text-red-800' : 'bg-orange-100 text-orange-800'
              }`
            }, item.status)
          ),
          React.createElement(TableCell, null, item.assignee)
        );
      })
    )
  );
  
  const html = renderToString(tableElement);
  console.log('Table rendered successfully!');
  console.log('HTML length:', html.length);
  console.log('\nFirst 1000 chars:');
  console.log(html.substring(0, 1000));
  
  // Check if all rows were rendered
  const rowCount = (html.match(/<tr/g) || []).length - 1; // -1 for header row
  console.log(`\nRendered ${rowCount} data rows (expected ${detailItems.length})`);
  
} catch (error) {
  console.error('Table render failed:', error);
  console.error(error.stack);
}