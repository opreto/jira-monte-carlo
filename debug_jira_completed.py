#!/usr/bin/env python3
"""Check for any completed issues in the project"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from atlassian import Jira

# Load environment variables
load_dotenv()

# Connect to Jira
jira = Jira(
    url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_USERNAME"),
    password=os.getenv("ATLASSIAN_API_TOKEN"),
    cloud=True
)

project_key = os.getenv("JIRA_PROJECT_KEY", "PARA")

# Check for ALL completed issues in the project
print(f"Checking for completed issues in project {project_key}...")
print("=" * 80)

# Look for completed issues in the last 6 months
six_months_ago = (datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d")
completed_jql = f"project = {project_key} AND statusCategory = Done AND resolved >= {six_months_ago} ORDER BY resolved DESC"
print(f"Using JQL: {completed_jql}")

result = jira.jql(completed_jql, limit=20)
issues = result.get("issues", [])

print(f"\nFound {result.get('total', 0)} completed issues in the last 6 months")

if issues:
    print("\nCompleted issues with story points:")
    print("-" * 80)
    
    issues_with_points = 0
    total_points = 0
    
    for issue in issues:
        story_points = issue['fields'].get('customfield_10016')
        labels = issue['fields'].get('labels', [])
        resolved = issue['fields'].get('resolutiondate', 'No date')[:10]
        
        if story_points:
            issues_with_points += 1
            total_points += float(story_points)
            
        points_str = str(story_points) if story_points is not None else "None"
        print(f"{issue['key']}: {issue['fields']['summary'][:40]:40} | Points: {points_str:>4} | Labels: {', '.join(labels) or 'None':20} | Resolved: {resolved}")
    
    print("-" * 80)
    print(f"Issues with story points: {issues_with_points}/{len(issues)}")
    print(f"Total story points completed: {total_points}")
    
    # Check sprint information
    print("\n\nSprint information:")
    print("-" * 80)
    
    sprints_seen = set()
    for issue in issues:
        sprint_field = issue['fields'].get('customfield_10020')
        if sprint_field:
            for sprint_data in sprint_field:
                if isinstance(sprint_data, str) and 'name=' in sprint_data:
                    # Extract sprint name
                    import re
                    name_match = re.search(r'name=([^,\]]+)', sprint_data)
                    if name_match:
                        sprint_name = name_match.group(1)
                        sprints_seen.add(sprint_name)
    
    print(f"Unique sprints with completed work: {len(sprints_seen)}")
    for sprint in sorted(sprints_seen):
        print(f"  - {sprint}")

else:
    print("\nNo completed issues found in the last 6 months!")
    
    # Let's check if there are ANY completed issues
    all_completed_jql = f"project = {project_key} AND statusCategory = Done"
    all_result = jira.jql(all_completed_jql, limit=1)
    total_completed = all_result.get('total', 0)
    
    print(f"\nTotal completed issues in project {project_key}: {total_completed}")
    
    if total_completed > 0:
        print("There are completed issues, but they are older than 6 months.")
        print("Consider using the --max-velocity-age parameter to include older data.")