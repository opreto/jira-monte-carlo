#!/usr/bin/env python3
"""Test script for responsive design across different viewport sizes"""

import webbrowser
import os
from pathlib import Path

# Get the path to the test report
report_path = Path(__file__).parent / "reports" / "responsive-test-report.html"

if not report_path.exists():
    print(f"Error: Report not found at {report_path}")
    print("Please run: sprint-radar -f jira-api:// --output reports/responsive-test-report.html")
    exit(1)

# Convert to file URL
file_url = f"file://{report_path.absolute()}"

print("Sprint Radar - Responsive Design Test")
print("=====================================")
print()
print("Opening report in your default browser...")
print(f"URL: {file_url}")
print()
print("Please test the following viewport sizes:")
print()
print("1. Mobile (iPhone 12 Pro): 390 x 844")
print("   - Check mobile menu toggle")
print("   - Verify tables switch to card layout")
print("   - Ensure charts are readable")
print("   - Test touch interactions")
print()
print("2. Tablet (iPad): 768 x 1024")
print("   - Check grid transitions from 2 to 3 columns")
print("   - Verify navigation switches to horizontal")
print("   - Ensure optimal spacing")
print()
print("3. Desktop (1080p): 1920 x 1080")
print("   - Check full desktop layout")
print("   - Verify 6-column metrics grid")
print("   - Test hover states")
print()
print("4. 4K Display: 3840 x 2160")
print("   - Check enhanced typography")
print("   - Verify proper scaling")
print("   - Ensure no content is too small")
print()
print("Use browser developer tools (F12) to simulate different devices.")
print("In Chrome/Edge: Device Toolbar (Ctrl+Shift+M)")
print("In Firefox: Responsive Design Mode (Ctrl+Shift+M)")

# Open the report
webbrowser.open(file_url)