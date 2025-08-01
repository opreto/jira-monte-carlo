#!/usr/bin/env python3
"""Test script to generate a report with the new responsive design"""

import subprocess
import sys
from pathlib import Path

def generate_test_report():
    """Generate a test report to verify responsive design"""
    
    # Generate report with adjusted scenario
    cmd = [
        sys.executable, "-m", "montecarlo",
        "report",
        "-f", "jira-api://",
        "-o", "reports/test_responsive.html"
    ]
    
    print("Generating test report with new responsive design...")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Report generated successfully: reports/test_responsive.html")
            print("\nPlease open the report in your browser and:")
            print("1. Check that charts don't overlap when resizing the window")
            print("2. Verify proper spacing on 4K displays")
            print("3. Test mobile responsiveness")
        else:
            print(f"❌ Error generating report: {result.stderr}")
            return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(generate_test_report())