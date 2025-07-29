"""Tests for process health chart generation"""

import pytest
import json
from datetime import datetime, timedelta

from src.domain.process_health import (
    AgingAnalysis,
    AgingCategory,
    AgingItem,
    BlockedItem,
    BlockedItemsAnalysis,
    SprintHealth,
    SprintHealthAnalysis,
    WIPAnalysis,
    WIPItem,
    WIPStatus,
)
from src.presentation.process_health_charts import ProcessHealthChartGenerator


class TestProcessHealthChartGenerator:
    """Test process health chart generation"""

    @pytest.fixture
    def chart_colors(self):
        """Chart color configuration"""
        return {
            "primary": "#667eea",
            "success": "#28a745",
            "warning": "#ffc107",
            "error": "#dc3545",
            "info": "#17a2b8",
            "data1": "#0066CC",
            "neutral": "#6c757d",
            "success_rgba": lambda alpha: f"rgba(40,167,69,{alpha})",
            "warning_rgba": lambda alpha: f"rgba(255,193,7,{alpha})",
            "error_rgba": lambda alpha: f"rgba(220,53,69,{alpha})",
        }

    @pytest.fixture
    def chart_generator(self, chart_colors):
        """Create chart generator instance"""
        return ProcessHealthChartGenerator(chart_colors)

    def test_get_color_with_alpha(self, chart_generator):
        """Test color with alpha conversion"""
        # Test with rgba function
        color = chart_generator._get_color_with_alpha("success", 0.5)
        assert color == "rgba(40,167,69,0.5)"

        # Test with hex color conversion
        chart_generator.chart_colors = {"warning": "#ffc107"}
        color = chart_generator._get_color_with_alpha("warning", 0.7)
        assert "rgba(255,193,7,0.7)" in color

        # Test fallback
        color = chart_generator._get_color_with_alpha("unknown", 0.5)
        assert "rgba" in color

    def test_create_aging_distribution_chart(self, chart_generator):
        """Test creating aging distribution chart"""
        # Create test data
        fresh_items = [
            AgingItem("TEST-1", "Fresh 1", "To Do", 3, AgingCategory.FRESH),
            AgingItem("TEST-2", "Fresh 2", "To Do", 5, AgingCategory.FRESH),
        ]
        aging_items = [
            AgingItem("TEST-3", "Aging 1", "In Progress", 20, AgingCategory.AGING),
        ]
        stale_items = [
            AgingItem("TEST-4", "Stale 1", "Blocked", 35, AgingCategory.STALE),
        ]

        analysis = AgingAnalysis(
            items_by_category={
                AgingCategory.FRESH: fresh_items,
                AgingCategory.NORMAL: [],
                AgingCategory.AGING: aging_items,
                AgingCategory.STALE: stale_items,
                AgingCategory.ABANDONED: [],
            },
            average_age_by_status={
                "To Do": 4.0,
                "In Progress": 20.0,
                "Blocked": 35.0,
            },
            oldest_items=stale_items,
            blocked_items=[],
            total_items=len(fresh_items + aging_items + stale_items),
        )

        # Generate chart
        chart_json = chart_generator.create_aging_distribution_chart(analysis)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert "data" in chart_data
        assert len(chart_data["data"]) == 1
        assert chart_data["data"][0]["type"] == "bar"

        # Verify data
        bar_data = chart_data["data"][0]
        assert bar_data["x"] == ["Fresh", "Normal", "Aging", "Stale", "Abandoned"]
        assert bar_data["y"] == [2, 0, 1, 1, 0]

        # Verify layout
        assert "layout" in chart_data
        assert chart_data["layout"]["title"]["text"] == "<b>Aging Work Items Distribution</b>"

    def test_create_aging_by_status_chart(self, chart_generator):
        """Test creating aging by status chart"""
        analysis = AgingAnalysis(
            items_by_category={},
            average_age_by_status={
                "To Do": 5.0,
                "In Progress": 15.0,
                "Blocked": 40.0,
                "In Review": 8.0,
            },
            oldest_items=[],
            blocked_items=[],
            total_items=0,
        )

        # Generate chart
        chart_json = chart_generator.create_aging_by_status_chart(analysis)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert chart_data["data"][0]["type"] == "bar"
        assert chart_data["data"][0]["orientation"] == "h"

        # Verify data is sorted by age
        bar_data = chart_data["data"][0]
        assert bar_data["y"][0] == "Blocked"  # Highest age
        assert bar_data["x"][0] == 40.0

        # Verify colors based on age
        colors = bar_data["marker"]["color"]
        assert len(colors) == 4

    def test_create_wip_by_status_chart(self, chart_generator):
        """Test creating WIP by status chart"""
        items_by_status = {
            WIPStatus.TODO: [
                WIPItem("TEST-1", "Todo 1", WIPStatus.TODO, 1, None),
            ],
            WIPStatus.IN_PROGRESS: [
                WIPItem("TEST-2", "WIP 1", WIPStatus.IN_PROGRESS, 3, "Dev1"),
                WIPItem("TEST-3", "WIP 2", WIPStatus.IN_PROGRESS, 5, "Dev2"),
                WIPItem("TEST-4", "WIP 3", WIPStatus.IN_PROGRESS, 2, "Dev3"),
            ],
            WIPStatus.REVIEW: [
                WIPItem("TEST-5", "Review 1", WIPStatus.REVIEW, 1, "Dev1"),
            ],
            WIPStatus.BLOCKED: [],
        }

        analysis = WIPAnalysis(
            items_by_status=items_by_status,
            wip_by_assignee={"Dev1": 2, "Dev2": 1, "Dev3": 1},
            total_wip=4,
            wip_limits={
                WIPStatus.IN_PROGRESS: 5,
                WIPStatus.REVIEW: 2,
            },
        )

        # Generate chart
        chart_json = chart_generator.create_wip_by_status_chart(analysis)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert chart_data["data"][0]["type"] == "bar"
        assert chart_data["data"][0]["name"] == "Current WIP"

        # Verify data
        bar_data = chart_data["data"][0]
        assert bar_data["x"] == ["Todo", "In Progress", "Review", "Blocked"]
        assert bar_data["y"] == [1, 3, 1, 0]

        # Verify WIP limit lines
        assert "shapes" in chart_data["layout"]
        assert len(chart_data["layout"]["shapes"]) >= 2  # Two limits set

    def test_create_sprint_health_trend_chart(self, chart_generator):
        """Test creating sprint health trend chart"""
        now = datetime.now()
        sprint_metrics = [
            SprintHealth("Sprint 1", now - timedelta(days=56), now - timedelta(days=42), 20, 25, 0, 0, 0.8),
            SprintHealth("Sprint 2", now - timedelta(days=42), now - timedelta(days=28), 23, 25, 2, 0, 0.92),
            SprintHealth("Sprint 3", now - timedelta(days=28), now - timedelta(days=14), 18, 20, 0, 2, 0.9),
            SprintHealth("Sprint 4", now - timedelta(days=14), now, 25, 25, 0, 0, 1.0),
        ]

        analysis = SprintHealthAnalysis(
            sprint_metrics=sprint_metrics,
            average_completion_rate=0.905,
            completion_rate_trend=0.04,
            average_scope_change=0.05,
            predictability_score=0.95,
        )

        # Generate chart
        chart_json = chart_generator.create_sprint_health_trend_chart(analysis)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert chart_data["data"][0]["type"] == "scatter"
        assert chart_data["data"][0]["mode"] == "lines+markers"

        # Verify data
        line_data = chart_data["data"][0]
        assert line_data["x"] == ["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4"]
        assert line_data["y"] == [80, 92, 90, 100]

        # Verify average and target lines
        assert "shapes" in chart_data["layout"]

    def test_create_sprint_scope_change_chart(self, chart_generator):
        """Test creating sprint scope change chart"""
        now = datetime.now()
        sprint_metrics = [
            SprintHealth("Sprint 1", now - timedelta(days=42), now - timedelta(days=28), 20, 25, 5, 0, 0.8),
            SprintHealth("Sprint 2", now - timedelta(days=28), now - timedelta(days=14), 23, 25, 2, 3, 0.92),
            SprintHealth("Sprint 3", now - timedelta(days=14), now, 18, 20, 0, 2, 0.9),
        ]

        analysis = SprintHealthAnalysis(
            sprint_metrics=sprint_metrics,
            average_completion_rate=0.87,
            completion_rate_trend=0.05,
            average_scope_change=0.1,
            predictability_score=0.85,
        )

        # Generate chart
        chart_json = chart_generator.create_sprint_scope_change_chart(analysis)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert len(chart_data["data"]) == 3  # Added, removed, and trend line
        assert chart_data["data"][0]["name"] == "Scope Added"
        assert chart_data["data"][1]["name"] == "Scope Removed"

        # Verify data
        assert chart_data["data"][0]["y"] == [5, 2, 0]  # Added
        assert chart_data["data"][1]["y"] == [0, -3, -2]  # Removed (negative)

    def test_create_blocked_items_severity_chart(self, chart_generator):
        """Test creating blocked items severity chart"""
        items_by_severity = {
            "low": [
                BlockedItem("TEST-1", "Low 1", "Blocked", 1, "Minor issue"),
                BlockedItem("TEST-2", "Low 2", "Blocked", 2, "Waiting"),
            ],
            "medium": [
                BlockedItem("TEST-3", "Med 1", "Blocked", 4, "Dependency"),
            ],
            "high": [
                BlockedItem("TEST-4", "High 1", "Blocked", 10, "Major blocker"),
                BlockedItem("TEST-5", "High 2", "Blocked", 8, "Critical"),
            ],
        }

        analysis = BlockedItemsAnalysis(
            blocked_items=list(items_by_severity["low"])
            + list(items_by_severity["medium"])
            + list(items_by_severity["high"]),
            total_blocked_points=15.0,
            average_blocked_days=5.0,
            blockers_by_type={
                "Minor issue": 1,
                "Waiting": 1,
                "Dependency": 1,
                "Major blocker": 1,
                "Critical": 1,
            },
            repeat_blockers=[],
        )

        # Generate chart
        chart_json = chart_generator.create_blocked_items_severity_chart(analysis)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert chart_data["data"][0]["type"] == "pie"
        assert chart_data["data"][0]["hole"] == 0.4  # Donut chart

        # Verify data
        pie_data = chart_data["data"][0]
        assert pie_data["labels"] == ["Low (≤2 days)", "Medium (3-5 days)", "High (>5 days)"]
        assert pie_data["values"] == [2, 1, 2]

        # Verify center annotation
        assert "annotations" in chart_data["layout"]
        assert chart_data["layout"]["annotations"][0]["text"] == "<b>5</b><br>Blocked Items"

    def test_create_process_health_score_gauge(self, chart_generator):
        """Test creating process health score gauge"""
        # Test healthy score
        chart_json = chart_generator.create_process_health_score_gauge(0.85)
        chart_data = json.loads(chart_json)

        # Verify chart structure
        assert chart_data["data"][0]["type"] == "indicator"
        assert chart_data["data"][0]["mode"] == "gauge+number+delta"

        # Verify data
        indicator_data = chart_data["data"][0]
        assert indicator_data["value"] == 85  # 0.85 * 100
        assert "Healthy" in indicator_data["title"]["text"]

        # Test fair score
        chart_json = chart_generator.create_process_health_score_gauge(0.65)
        chart_data = json.loads(chart_json)
        assert "Fair" in chart_data["data"][0]["title"]["text"]

        # Test needs attention score
        chart_json = chart_generator.create_process_health_score_gauge(0.45)
        chart_data = json.loads(chart_json)
        assert "Needs Attention" in chart_data["data"][0]["title"]["text"]
