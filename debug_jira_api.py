#!/usr/bin/env python3
"""Debug script to inspect Jira API data directly"""

import os
import json
from datetime import datetime
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

# Get the JQL from environment
jql = os.getenv("JIRA_JQL_FILTER", "statusCategory != Done AND labels = mvp")
print(f"Using JQL: {jql}")
print("=" * 80)

# Fetch issues
result = jira.jql(jql, limit=5, expand="changelog")
issues = result.get("issues", [])

print(f"Found {result.get('total', 0)} total issues, showing first {len(issues)}")
print("=" * 80)

# Analyze first issue in detail
if issues:
    issue = issues[0]
    print("\nFirst issue details:")
    print(f"Key: {issue['key']}")
    print(f"Summary: {issue['fields']['summary']}")
    print(f"Status: {issue['fields']['status']['name']}")
    print(f"Created: {issue['fields']['created']}")
    
    # Check for resolved date
    resolved = issue['fields'].get('resolutiondate')
    print(f"Resolved: {resolved}")
    
    # Check for story points
    print("\nCustom fields containing 'point' or 'story':")
    for field_name, field_value in issue['fields'].items():
        if field_name.startswith('customfield_'):
            # Try to get field name from schema if available
            field_label = field_name
            if field_value is not None and str(field_value).strip():
                if 'point' in str(field_value).lower() or 'story' in field_name.lower():
                    print(f"  {field_name}: {field_value}")
    
    # Check for sprints
    print("\nSprint information:")
    for field_name, field_value in issue['fields'].items():
        if field_name.startswith('customfield_') and field_value:
            if isinstance(field_value, list) and field_value:
                first_val = str(field_value[0])
                if 'com.atlassian.greenhopper.service.sprint.Sprint' in first_val:
                    print(f"  Sprint field: {field_name}")
                    print(f"  Sprint data: {field_value[0][:200]}...")
    
    # Check changelog for transitions
    print("\nChangelog analysis:")
    if 'changelog' in issue:
        histories = issue['changelog']['histories']
        print(f"  Total history entries: {len(histories)}")
        
        # Look for status changes to Done
        done_transitions = 0
        for history in histories:
            for item in history['items']:
                if item['field'] == 'status' and item['toString'] in ['Done', 'Closed', 'Resolved']:
                    done_transitions += 1
                    print(f"  - Transitioned to {item['toString']} on {history['created']}")
        
        if done_transitions == 0:
            print("  - No transitions to Done/Closed/Resolved found")

# Now check for completed issues to understand velocity
print("\n" + "=" * 80)
print("Checking for completed issues...")

# Modify JQL to find completed issues
completed_jql = "statusCategory = Done AND labels = mvp ORDER BY resolved DESC"
print(f"Using JQL: {completed_jql}")

completed_result = jira.jql(completed_jql, limit=10)
completed_issues = completed_result.get("issues", [])

print(f"Found {completed_result.get('total', 0)} completed issues")

if completed_issues:
    print("\nRecent completed issues:")
    for issue in completed_issues[:5]:
        resolved = issue['fields'].get('resolutiondate', 'No resolution date')
        print(f"  - {issue['key']}: {issue['fields']['summary'][:50]}... (Resolved: {resolved})")
else:
    print("\nNo completed issues found with the mvp label!")

# Check field mappings
print("\n" + "=" * 80)
print("Getting field mappings...")

fields = jira.get_all_fields()
print(f"Total fields: {len(fields)}")

print("\nStory Points fields:")
for field in fields:
    if 'story' in field['name'].lower() or 'point' in field['name'].lower():
        print(f"  - {field['id']}: {field['name']}")

print("\nSprint fields:")
for field in fields:
    if 'sprint' in field['name'].lower():
        print(f"  - {field['id']}: {field['name']}")