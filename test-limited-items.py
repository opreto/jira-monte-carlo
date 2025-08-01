#!/usr/bin/env python3
"""Test if limiting detail items fixes the rendering issue"""

import json

# Load test data
with open("reports/debug-process-health.json", "r") as f:
    health_data = json.load(f)

# Limit the detail items to just 3 for the Aging Items component
if (
    health_data.get("health_score_breakdown")
    and len(health_data["health_score_breakdown"]) > 0
):
    aging_component = health_data["health_score_breakdown"][0]
    if aging_component.get("detail_items") and len(aging_component["detail_items"]) > 3:
        print(f"Limiting detail_items from {len(aging_component['detail_items'])} to 3")
        aging_component["detail_items"] = aging_component["detail_items"][:3]

# Save modified data
with open("reports/debug-process-health-limited.json", "w") as f:
    json.dump(health_data, f, indent=2)

print("Modified health data saved. Now generate a report with limited items:")
print(
    "python -m src.presentation.cli -f jira-api:// -o reports/test-limited-items.html"
)
