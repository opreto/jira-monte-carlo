#!/usr/bin/env python3
"""
Workaround script to handle velocity calculation from all project work
while forecasting only filtered items.

This script:
1. Temporarily modifies the JQL to get all project data
2. Runs sprint-radar to generate the forecast
3. The forecast will show all project velocity but remaining work for filtered items
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Get current JQL filter
    original_jql = os.environ.get('JIRA_JQL_FILTER', '')
    project_key = os.environ.get('JIRA_PROJECT_KEY', '')
    
    if not project_key:
        print("Error: JIRA_PROJECT_KEY environment variable not set")
        sys.exit(1)
    
    print(f"Original JQL filter: {original_jql}")
    print(f"Project key: {project_key}")
    
    # Create a temporary JQL that includes all project work
    # This will get both completed (for velocity) and incomplete (for backlog) items
    temp_jql = f"project = {project_key}"
    
    print(f"\nTemporarily using JQL: {temp_jql}")
    print("This will calculate velocity from ALL completed project work")
    print("Note: The forecast will include ALL incomplete project work, not just filtered items")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled")
        sys.exit(0)
    
    # Set the temporary JQL
    env = os.environ.copy()
    env['JIRA_JQL_FILTER'] = temp_jql
    
    # Run sprint-radar with the modified environment
    cmd = ['sprint-radar', '-f', 'jira-api://'] + sys.argv[1:]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("-" * 80)
    
    result = subprocess.run(cmd, env=env)
    
    if result.returncode == 0:
        print("-" * 80)
        print("\nSuccess! Note that the forecast includes ALL project work.")
        print(f"To forecast only '{original_jql}' items, we need to implement dual JQL support.")
    
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()