import re
import json

# Read the HTML file
with open("reports/test-sprint-health.html", "r") as f:
    html_content = f.read()

# Look for the React props data
# The data is passed via data-report attribute
pattern = r'data-report="([^"]+)"'
match = re.search(pattern, html_content)

if match:
    # Unescape HTML entities
    json_data = match.group(1)
    json_data = json_data.replace("&quot;", '"')
    json_data = json_data.replace("&lt;", "<")
    json_data = json_data.replace("&gt;", ">")
    json_data = json_data.replace("&amp;", "&")

    try:
        data = json.loads(json_data)

        # Look for process health data
        if "processHealth" in data:
            ph = data["processHealth"]
            print(f"Process Health Score: {ph.get('score', 'N/A')}%")

            if "health_score_breakdown" in ph:
                breakdown = ph["health_score_breakdown"]
                print(f"\nHealth Score Breakdown has {len(breakdown)} components:")
                for i, comp in enumerate(breakdown):
                    print(
                        f"\n{i + 1}. {comp.get('name', 'Unknown')}: {comp.get('score', 0) * 100:.0f}%"
                    )
                    print(f"   Description: {comp.get('description', 'N/A')}")
                    if "detail_items" in comp and comp["detail_items"]:
                        print(f"   Detail items: {len(comp['detail_items'])}")
            else:
                print("No health_score_breakdown found in data")

            # Check for sprint_health
            if "sprint_health" in ph:
                sh = ph["sprint_health"]
                print("\nSprint Health data found:")
                print(
                    f"  - Predictability score: {sh.get('predictability_score', 'N/A')}"
                )
                print(f"  - Sprint metrics: {len(sh.get('sprint_metrics', []))}")
        else:
            print("No processHealth found in data")

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print("First 500 chars of data:")
        print(json_data[:500])
else:
    print("No data-report attribute found in HTML")
