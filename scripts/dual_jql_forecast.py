#!/usr/bin/env python3
"""
Advanced workaround that implements dual JQL queries:
1. Uses project-wide data for velocity calculation
2. Filters to show only specific backlog items

This provides accurate velocity based on all completed work
while forecasting only the filtered items.
"""

import os
import sys
import json
from datetime import datetime
from collections import defaultdict
from dotenv import load_dotenv
from atlassian import Jira
import click

# Load environment variables
load_dotenv()

def fetch_velocity_data(jira, project_key, lookback_weeks=26):
    """Fetch completed issues for velocity calculation"""
    velocity_jql = f"project = {project_key} AND statusCategory = Done AND resolved >= -{lookback_weeks}w ORDER BY resolved DESC"
    print(f"Fetching velocity data: {velocity_jql}")
    
    result = jira.jql(velocity_jql, limit=1000)
    issues = result.get('issues', [])
    
    # Group by sprint
    sprints = defaultdict(lambda: {'completed_points': 0, 'completed_count': 0})
    
    for issue in issues:
        story_points = issue['fields'].get('customfield_10016', 0) or 0
        sprint_field = issue['fields'].get('customfield_10020', [])
        
        if sprint_field:
            for sprint_data in sprint_field:
                if isinstance(sprint_data, str) and 'name=' in sprint_data:
                    import re
                    name_match = re.search(r'name=([^,\]]+)', sprint_data)
                    if name_match:
                        sprint_name = name_match.group(1)
                        sprints[sprint_name]['completed_points'] += float(story_points) if story_points else 0
                        sprints[sprint_name]['completed_count'] += 1
    
    # Calculate velocity metrics
    velocities = [s['completed_points'] for s in sprints.values() if s['completed_points'] > 0]
    
    if not velocities:
        return None, issues
        
    import statistics
    velocity_metrics = {
        'average': statistics.mean(velocities),
        'median': statistics.median(velocities),
        'std_dev': statistics.stdev(velocities) if len(velocities) > 1 else 0,
        'min': min(velocities),
        'max': max(velocities),
        'sprint_count': len(velocities)
    }
    
    return velocity_metrics, issues

def fetch_backlog_data(jira, jql_filter):
    """Fetch backlog items to forecast"""
    print(f"Fetching backlog data: {jql_filter}")
    
    result = jira.jql(jql_filter, limit=1000)
    issues = result.get('issues', [])
    
    # Calculate remaining work
    remaining_points = 0
    remaining_count = 0
    
    for issue in issues:
        story_points = issue['fields'].get('customfield_10016', 0) or 0
        remaining_points += float(story_points) if story_points else 0
        remaining_count += 1
    
    return {
        'total_points': remaining_points,
        'total_count': remaining_count,
        'issues': issues
    }

@click.command()
@click.option('--backlog-jql', help='JQL for backlog items to forecast')
@click.option('--velocity-project', help='Project key for velocity calculation')
@click.option('--output', '-o', default='forecast-report.json', help='Output file')
def main(backlog_jql, velocity_project, output):
    """Generate forecast using dual JQL approach"""
    
    # Initialize Jira connection
    jira = Jira(
        url=os.getenv("JIRA_URL"),
        username=os.getenv("JIRA_USERNAME"),
        password=os.getenv("ATLASSIAN_API_TOKEN"),
        cloud=True
    )
    
    # Use environment variables as defaults
    if not backlog_jql:
        backlog_jql = os.getenv('JIRA_JQL_FILTER', 'statusCategory != Done')
    if not velocity_project:
        velocity_project = os.getenv('JIRA_PROJECT_KEY')
        
    if not velocity_project:
        print("Error: Need project key for velocity calculation")
        sys.exit(1)
    
    print("=" * 80)
    print("Dual JQL Forecast Tool")
    print("=" * 80)
    
    # Fetch velocity data from all project work
    velocity_metrics, completed_issues = fetch_velocity_data(jira, velocity_project)
    
    if not velocity_metrics:
        print("\nError: No completed work found for velocity calculation")
        print(f"Searched in project: {velocity_project}")
        sys.exit(1)
    
    print(f"\nVelocity Metrics (from {velocity_metrics['sprint_count']} sprints):")
    print(f"  Average: {velocity_metrics['average']:.1f} points/sprint")
    print(f"  Median: {velocity_metrics['median']:.1f} points/sprint")
    print(f"  Std Dev: {velocity_metrics['std_dev']:.1f}")
    print(f"  Range: {velocity_metrics['min']:.1f} - {velocity_metrics['max']:.1f}")
    
    # Fetch backlog data using the filter
    backlog_data = fetch_backlog_data(jira, backlog_jql)
    
    print(f"\nBacklog to Forecast:")
    print(f"  Total Items: {backlog_data['total_count']}")
    print(f"  Total Points: {backlog_data['total_points']:.1f}")
    
    # Simple forecast calculation
    if velocity_metrics['average'] > 0:
        sprints_needed = backlog_data['total_points'] / velocity_metrics['average']
        print(f"\nForecast:")
        print(f"  Sprints needed (average): {sprints_needed:.1f}")
        print(f"  Sprints needed (conservative): {backlog_data['total_points'] / velocity_metrics['min']:.1f}")
        print(f"  Sprints needed (optimistic): {backlog_data['total_points'] / velocity_metrics['max']:.1f}")
    
    # Save detailed report
    report = {
        'generated_at': datetime.now().isoformat(),
        'velocity_data': {
            'source': f"project = {velocity_project}",
            'metrics': velocity_metrics,
            'completed_issues_count': len(completed_issues)
        },
        'backlog_data': {
            'source': backlog_jql,
            'total_points': backlog_data['total_points'],
            'total_count': backlog_data['total_count']
        },
        'forecast': {
            'sprints_needed_average': sprints_needed if velocity_metrics['average'] > 0 else None,
            'sprints_needed_conservative': backlog_data['total_points'] / velocity_metrics['min'] if velocity_metrics['min'] > 0 else None,
            'sprints_needed_optimistic': backlog_data['total_points'] / velocity_metrics['max'] if velocity_metrics['max'] > 0 else None,
        }
    }
    
    with open(output, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {output}")
    print("\nNote: This is a temporary workaround. Use sprint-radar for full Monte Carlo simulation.")

if __name__ == '__main__':
    main()