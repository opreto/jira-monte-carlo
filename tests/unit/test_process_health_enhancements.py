"""Tests for process health enhancements - Lead Time Analysis and improved scoring"""

from datetime import datetime, timedelta
from unittest.mock import Mock

from src.application.process_health_use_cases import (
    AnalyzeLeadTimeUseCase,
)
from src.domain.entities import Issue
from src.domain.process_health import (
    AgingAnalysis,
    AgingCategory,
    AgingItem,
    LeadTimeAnalysis,
    LeadTimeMetrics,
    ProcessHealthMetrics,
)


class TestLeadTimeAnalysis:
    """Test lead time analysis functionality"""

    def test_lead_time_metrics_creation(self):
        """Test creating lead time metrics"""
        created = datetime(2024, 1, 1)
        resolved = datetime(2024, 1, 15)

        metrics = LeadTimeMetrics(
            issue_key="TEST-1",
            created_date=created,
            resolved_date=resolved,
            lead_time_days=14.0,
            cycle_time_days=10.0,
            wait_time_days=4.0,
            issue_type="Story",
            labels=["feature", "backend"],
        )

        assert metrics.issue_key == "TEST-1"
        assert metrics.lead_time_days == 14.0
        assert metrics.cycle_time_days == 10.0
        assert metrics.wait_time_days == 4.0
        assert not metrics.is_defect

    def test_defect_detection(self):
        """Test defect detection based on issue type"""
        bug_metrics = LeadTimeMetrics(
            issue_key="BUG-1",
            created_date=datetime.now(),
            resolved_date=None,
            lead_time_days=None,
            cycle_time_days=None,
            wait_time_days=None,
            issue_type="Bug",
            labels=[],
        )

        assert bug_metrics.is_defect

    def test_flow_efficiency_calculation(self):
        """Test flow efficiency calculation"""
        metrics = LeadTimeMetrics(
            issue_key="TEST-1",
            created_date=datetime.now(),
            resolved_date=None,
            lead_time_days=10.0,
            cycle_time_days=8.0,
            wait_time_days=2.0,
            issue_type="Story",
        )

        assert metrics.flow_efficiency == 0.8  # 8/10 = 80%

    def test_lead_time_analysis_properties(self):
        """Test LeadTimeAnalysis aggregate properties"""
        metrics_list = [
            LeadTimeMetrics(
                issue_key=f"TEST-{i}",
                created_date=datetime.now(),
                resolved_date=datetime.now() + timedelta(days=i * 5),
                lead_time_days=float(i * 5),
                cycle_time_days=float(i * 4),
                wait_time_days=float(i),
                issue_type="Bug" if i == 1 else "Story",
            )
            for i in range(1, 4)
        ]

        analysis = LeadTimeAnalysis(metrics=metrics_list)

        assert analysis.average_lead_time == 10.0  # (5+10+15)/3
        assert analysis.median_lead_time == 10.0
        assert analysis.defect_rate == 1 / 3  # 1 bug out of 3 issues
        assert abs(analysis.average_flow_efficiency - 0.8) < 0.0001  # (0.8+0.8+0.8)/3

        percentiles = analysis.lead_time_percentiles
        assert percentiles[50] == 10.0  # median
        assert percentiles[85] >= 10.0  # should be higher than median


class TestHealthScoreEnhancements:
    """Test health score calculation improvements"""

    def test_health_score_with_lead_time(self):
        """Test health score includes lead time analysis"""
        lead_time_analysis = LeadTimeAnalysis(
            metrics=[
                LeadTimeMetrics(
                    issue_key="TEST-1",
                    created_date=datetime.now() - timedelta(days=5),
                    resolved_date=datetime.now(),
                    lead_time_days=5.0,
                    cycle_time_days=4.0,
                    wait_time_days=1.0,
                    issue_type="Story",
                )
            ]
        )

        health_metrics = ProcessHealthMetrics(lead_time_analysis=lead_time_analysis)

        # Score should be high for 5-day lead time (excellent)
        score = health_metrics.health_score
        assert 0.8 <= score <= 1.0

    def test_health_score_with_poor_lead_time(self):
        """Test health score with poor lead time"""
        lead_time_analysis = LeadTimeAnalysis(
            metrics=[
                LeadTimeMetrics(
                    issue_key="TEST-1",
                    created_date=datetime.now() - timedelta(days=45),
                    resolved_date=datetime.now(),
                    lead_time_days=45.0,
                    cycle_time_days=40.0,
                    wait_time_days=5.0,
                    issue_type="Story",
                )
            ]
        )

        health_metrics = ProcessHealthMetrics(lead_time_analysis=lead_time_analysis)

        # Score should be low for 45-day lead time
        score = health_metrics.health_score
        assert score < 0.5

    def test_health_score_breakdown_with_detail_items(self):
        """Test health score breakdown includes detail items"""
        # Create aging analysis with critical items
        aging_items = []
        for i in range(5):
            aging_items.append(
                AgingItem(
                    key=f"OLD-{i}",
                    summary=f"Old issue {i}",
                    status="In Progress",
                    age_days=100 + i * 10,
                    category=AgingCategory.ABANDONED,
                    assignee=f"user{i}" if i % 2 == 0 else None,
                )
            )

        aging_analysis = AgingAnalysis(
            items_by_category={
                AgingCategory.ABANDONED: aging_items,
                AgingCategory.NORMAL: [],
            },
            average_age_by_status={"In Progress": 105.0},
            oldest_items=aging_items[:3],
            blocked_items=[],
            total_items=10,
        )

        health_metrics = ProcessHealthMetrics(aging_analysis=aging_analysis)

        breakdown = health_metrics.health_score_breakdown

        # Find aging component
        aging_component = next((c for c in breakdown if c.name == "Aging Items"), None)
        assert aging_component is not None
        assert aging_component.detail_items is not None
        assert len(aging_component.detail_items) > 0

        # Check detail items are sorted by age descending
        ages = [item["age_days"] for item in aging_component.detail_items]
        assert ages == sorted(ages, reverse=True)

        # Check detail item structure
        first_item = aging_component.detail_items[0]
        assert "key" in first_item
        assert "summary" in first_item
        assert "age_days" in first_item
        assert "status" in first_item
        assert "assignee" in first_item
        assert "type" in first_item


class TestLeadTimeUseCase:
    """Test lead time analysis use case"""

    def test_analyze_lead_time_use_case(self):
        """Test the lead time analysis use case"""
        # Create test issues
        issues = []
        base_date = datetime.now()

        for i in range(5):
            issue = Mock(spec=Issue)
            issue.key = f"TEST-{i}"
            issue.summary = f"Test issue {i}"
            issue.issue_type = "Bug" if i == 0 else "Story"
            issue.labels = ["feature"] if i % 2 == 0 else []
            issue.created = base_date - timedelta(days=10 + i)
            issue.resolved = base_date - timedelta(days=i) if i < 3 else None
            issue.status = "Done" if i < 3 else "In Progress"
            issue.assignee = f"dev{i}"
            issue.custom_fields = {}
            issues.append(issue)

        # Create repository mock
        issue_repo = Mock()
        issue_repo.get_all.return_value = issues

        # Execute use case
        use_case = AnalyzeLeadTimeUseCase(issue_repo)
        analysis = use_case.execute()

        assert analysis is not None
        assert len(analysis.metrics) == 3  # Only resolved issues
        assert analysis.defect_rate == 1 / 3  # 1 bug out of 3 resolved
        assert analysis.average_lead_time > 0


class TestHealthScoreNonNegative:
    """Test that health scores cannot go negative"""

    def test_lead_time_score_bounds(self):
        """Test lead time score is always between 0 and 1"""
        # Test with very high defect rate
        lead_time_analysis = LeadTimeAnalysis(
            metrics=[
                LeadTimeMetrics(
                    issue_key=f"BUG-{i}",
                    created_date=datetime.now() - timedelta(days=50),
                    resolved_date=datetime.now(),
                    lead_time_days=50.0,
                    cycle_time_days=50.0,
                    wait_time_days=0.0,
                    issue_type="Bug",
                )
                for i in range(10)  # All bugs = 100% defect rate
            ]
        )

        health_metrics = ProcessHealthMetrics(lead_time_analysis=lead_time_analysis)

        breakdown = health_metrics.health_score_breakdown
        lead_time_component = next((c for c in breakdown if c.name == "Lead Time & Quality"), None)

        assert lead_time_component is not None
        assert 0 <= lead_time_component.score <= 1  # Must be bounded

    def test_flow_efficiency_bonus(self):
        """Test flow efficiency provides positive bonus"""
        lead_time_analysis = LeadTimeAnalysis(
            metrics=[
                LeadTimeMetrics(
                    issue_key="FAST-1",
                    created_date=datetime.now() - timedelta(days=10),
                    resolved_date=datetime.now(),
                    lead_time_days=10.0,
                    cycle_time_days=9.5,  # 95% flow efficiency
                    wait_time_days=0.5,
                    issue_type="Story",
                )
            ]
        )

        health_metrics = ProcessHealthMetrics(lead_time_analysis=lead_time_analysis)

        breakdown = health_metrics.health_score_breakdown
        lead_time_component = next((c for c in breakdown if c.name == "Lead Time & Quality"), None)

        # Should get bonus for excellent flow efficiency
        assert lead_time_component.score > 0.9
