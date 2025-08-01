import re

# Read the HTML file
with open("reports/test-sorted.html", "r") as f:
    html_content = f.read()

# Look for the Process Health Score section - capture everything up to Completion Forecast Summary
pattern = r"Process Health Score</h2>.*?(?=<section.*?Completion Forecast Summary|$)"
match = re.search(pattern, html_content, re.DOTALL)

if match:
    health_section = match.group()

    # Check if we can find the percentage
    score_match = re.search(r"text-6xl font-bold.*?>(\d+)%", health_section)
    if score_match:
        print(f"Health Score Found: {score_match.group(1)}%")

    # Look for the breakdown section
    if "Score Breakdown" in health_section:
        print("Score Breakdown section found!")

        # Extract the breakdown section - increase limit to capture all components
        breakdown_start = health_section.find("Score Breakdown")
        breakdown_section = health_section[breakdown_start : breakdown_start + 10000]

        # Check for component divs - look for the actual component pattern
        component_count = breakdown_section.count('class="rounded-lg bg-white border')
        print(f"Found {component_count} breakdown components")

        # Look for specific text patterns
        if "Aging Items" in breakdown_section:
            print("✓ Aging Items component found")
        if "Work In Progress" in breakdown_section:
            print("✓ WIP component found")
        if "Sprint Predictability" in breakdown_section:
            print("✓ Sprint Predictability component found")

        # Search for Sprint Predictability in the entire section
        if (
            "Sprint Predictability" not in breakdown_section
            and "Sprint Predictability" in health_section
        ):
            print("⚠️  Sprint Predictability found elsewhere in health section")

        # Check where the breakdown section ends
        if "</div></div></div>" in breakdown_section:
            end_idx = breakdown_section.find("</div></div></div>")
            print(f"\nBreakdown section ends at char {end_idx}")
            print(
                f"Content after breakdown: {breakdown_section[end_idx : end_idx + 200]}"
            )

        # Check if there's a "No breakdown data" message
        if "No breakdown data available" in breakdown_section:
            print("⚠️  'No breakdown data available' message is shown")

        # Look for score percentages in the breakdown
        import re

        score_pattern = r'class="text-2xl font-bold text-\w+-600">(\d+)%'
        scores = re.findall(score_pattern, breakdown_section)
        print(f"\nFound {len(scores)} component scores: {scores}")

        # Extract component names and scores
        component_pattern = r'class="text-lg font-semibold[^"]*">([^<]+)</h4>.*?class="text-2xl font-bold[^"]*">(\d+)%'
        components = re.findall(component_pattern, breakdown_section, re.DOTALL)
        print("\nComponent breakdown:")
        for name, score in components:
            print(f"  - {name}: {score}%")

        # Extract a larger sample of the breakdown content
        print("\nFirst 5000 chars of breakdown section:")
        print(breakdown_section[:5000])

    elif "Limited Health Data" in health_section:
        print("Limited Health Data message found!")
    else:
        print("No breakdown section found in the HTML")

    # Check if the gauge chart is present
    if "health_score_gauge" in health_section:
        print("Health score gauge chart is present")

    # Check for ProcessHealthBreakdown component
    if "ProcessHealthBreakdown" in health_section:
        print("ProcessHealthBreakdown component reference found")

    # Check how the breakdown section ends
    if "</table>" in breakdown_section and "</details>" in breakdown_section:
        details_end = breakdown_section.find("</details>")
        after_details = breakdown_section[details_end : details_end + 200]
        print(f"\nContent after first component details: {after_details}")

    # Check the end of the health section
    print("\nLast 500 chars of health section:")
    print(health_section[-500:])

    # Find the last complete table row
    last_para = health_section.rfind("PARA-")
    if last_para > 0:
        context = health_section[last_para - 50 : last_para + 100]
        print(f"\nContext around last PARA reference: {context}")

    # Check if the HTML is truncated
    if not health_section.strip().endswith("</html>"):
        print("\n⚠️  WARNING: HTML appears to be truncated!")
else:
    print("Process Health Score section not found")
