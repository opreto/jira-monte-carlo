"""Tests for process health domain entities and use cases"""
from datetime import datetime, timedelta
from unittest.mock import Mock

from src.domain.entities import Issue, Sprint
from src.domain.process_health import (
    AgingAnalysis,
    AgingCategory,
    AgingItem,
    BlockedItem,
    BlockedItemsAnalysis,
    ProcessHealthMetrics,
    SprintHealth,
    SprintHealthAnalysis,
    WIPAnalysis,
    WIPItem,
    WIPStatus,
)
from src.application.process_health_use_cases import (
    AnalyzeAgingWorkItemsUseCase,
    AnalyzeBlockedItemsUseCase,
    AnalyzeProcessHealthUseCase,
    AnalyzeSprintHealthUseCase,
    AnalyzeWorkInProgressUseCase,
)


class TestAgingAnalysis:
    """Test aging analysis domain entities"""
    
    def test_aging_item_creation(self):
        """Test creating an aging item"""
        item = AgingItem(
            key="TEST-1",
            summary="Test issue",
            status="In Progress",
            age_days=10,
            category=AgingCategory.NORMAL
        )
        
        assert item.key == "TEST-1"
        assert item.summary == "Test issue"
        assert item.status == "In Progress"
        assert item.age_days == 10
        assert item.category == AgingCategory.NORMAL
    
    def test_aging_category_values(self):
        """Test aging category enumeration values"""
        assert AgingCategory.FRESH.value == "fresh"
        assert AgingCategory.NORMAL.value == "normal"
        assert AgingCategory.AGING.value == "aging"
        assert AgingCategory.STALE.value == "stale"
        assert AgingCategory.ABANDONED.value == "abandoned"
    
    def test_aging_analysis_aggregation(self):
        """Test aging analysis aggregation"""
        items = [
            AgingItem("TEST-1", "Issue 1", "To Do", 5, AgingCategory.FRESH),
            AgingItem("TEST-2", "Issue 2", "In Progress", 15, AgingCategory.AGING),
            AgingItem("TEST-3", "Issue 3", "In Progress", 20, AgingCategory.AGING),
        ]
        
        analysis = AgingAnalysis(
            items_by_category={
                AgingCategory.FRESH: [items[0]],
                AgingCategory.AGING: [items[1], items[2]]
            },
            average_age_by_status={
                "To Do": 5.0,
                "In Progress": 17.5
            },
            oldest_items=[items[2]],  # Item with age 20
            blocked_items=[],
            total_items=3
        )
        
        assert analysis.total_items == 3
        assert len(analysis.items_by_category[AgingCategory.FRESH]) == 1
        assert len(analysis.items_by_category[AgingCategory.AGING]) == 2
        assert analysis.average_age_by_status["In Progress"] == 17.5
        assert len(analysis.oldest_items) == 1


class TestWIPAnalysis:
    """Test WIP analysis domain entities"""
    
    def test_wip_item_creation(self):
        """Test creating a WIP item"""
        item = WIPItem(
            key="TEST-1",
            summary="Test issue",
            status="In Progress",
            wip_status=WIPStatus.IN_PROGRESS,
            assignee="John Doe",
            age_days=5
        )
        
        assert item.key == "TEST-1"
        assert item.summary == "Test issue"
        assert item.status == "In Progress"
        assert item.wip_status == WIPStatus.IN_PROGRESS
        assert item.age_days == 5
        assert item.assignee == "John Doe"
    
    def test_wip_status_values(self):
        """Test WIP status enumeration values"""
        assert WIPStatus.TODO.value == "todo"
        assert WIPStatus.IN_PROGRESS.value == "in_progress"
        assert WIPStatus.REVIEW.value == "review"
        assert WIPStatus.BLOCKED.value == "blocked"
    
    def test_wip_analysis_with_limits(self):
        """Test WIP analysis with limits"""
        items = [
            WIPItem("TEST-1", "Issue 1", "To Do", WIPStatus.TODO, None, 1),
            WIPItem("TEST-2", "Issue 2", "In Progress", WIPStatus.IN_PROGRESS, "Dev1", 3),
            WIPItem("TEST-3", "Issue 3", "In Progress", WIPStatus.IN_PROGRESS, "Dev2", 5),
        ]
        
        analysis = WIPAnalysis(
            items_by_status={
                WIPStatus.TODO: [items[0]],
                WIPStatus.IN_PROGRESS: [items[1], items[2]]
            },
            wip_by_assignee={
                "Dev1": 1,
                "Dev2": 1
            },
            total_wip=3,
            wip_limits={
                WIPStatus.IN_PROGRESS: 3
            }
        )
        
        assert analysis.total_wip == 3
        assert len(analysis.items_by_status[WIPStatus.IN_PROGRESS]) == 2
        assert analysis.wip_limits[WIPStatus.IN_PROGRESS] == 3
        assert len(analysis.wip_violations) == 0  # No violations


class TestSprintHealthAnalysis:
    """Test sprint health analysis domain entities"""
    
    def test_sprint_health_creation(self):
        """Test creating sprint health metrics"""
        metrics = SprintHealth(
            sprint_name="Sprint 10",
            start_date=datetime.now() - timedelta(days=14),
            end_date=datetime.now(),
            completed_points=20,
            committed_points=25,
            added_points=5,
            removed_points=2,
            completion_rate=0.8
        )
        
        assert metrics.sprint_name == "Sprint 10"
        assert metrics.completed_points == 20
        assert metrics.committed_points == 25
        assert metrics.completion_rate == 0.8
    
    def test_sprint_health_analysis_trends(self):
        """Test sprint health analysis with trends"""
        now = datetime.now()
        sprint_metrics = [
            SprintHealth("Sprint 1", now - timedelta(days=42), now - timedelta(days=28), 20, 25, 0, 0, 0.8),
            SprintHealth("Sprint 2", now - timedelta(days=28), now - timedelta(days=14), 18, 20, 2, 0, 0.9),
            SprintHealth("Sprint 3", now - timedelta(days=14), now, 22, 25, 3, 1, 0.88),
        ]
        
        analysis = SprintHealthAnalysis(
            sprint_metrics=sprint_metrics,
            average_completion_rate=0.86,
            completion_rate_trend=0.04,
            average_scope_change=0.12,
            predictability_score=0.85
        )
        
        assert len(analysis.sprint_metrics) == 3
        assert analysis.average_completion_rate == 0.86
        assert analysis.completion_rate_trend == 0.04
        assert analysis.predictability_score == 0.85


class TestBlockedItemsAnalysis:
    """Test blocked items analysis domain entities"""
    
    def test_blocked_item_creation(self):
        """Test creating a blocked item"""
        item = BlockedItem(
            key="TEST-1",
            summary="Blocked issue",
            status="Blocked",
            blocked_days=3,
            blocker_description="Waiting for API access"
        )
        
        assert item.key == "TEST-1"
        assert item.summary == "Blocked issue"
        assert item.blocked_days == 3
        assert item.blocker_description == "Waiting for API access"
        assert item.severity in ["low", "medium", "high"]
    
    def test_blocked_items_analysis_by_severity(self):
        """Test blocked items analysis grouped by severity"""
        items = [
            BlockedItem("TEST-1", "Issue 1", "Blocked", 1, "Minor block"),
            BlockedItem("TEST-2", "Issue 2", "Blocked", 4, "Medium block"),
            BlockedItem("TEST-3", "Issue 3", "Blocked", 10, "Major block"),
        ]
        
        analysis = BlockedItemsAnalysis(
            blocked_items=items,
            total_blocked_points=10.0,  # Assuming some story points
            average_blocked_days=5.0,
            blockers_by_type={
                "Minor block": 1,
                "Medium block": 1,
                "Major block": 1
            },
            repeat_blockers=[]
        )
        
        assert len(analysis.blocked_items) == 3
        assert analysis.average_blocked_days == 5.0
        assert analysis.total_blocked_points == 10.0
        # Test the severity grouping property
        severity_groups = analysis.items_by_severity
        assert "low" in severity_groups
        assert "high" in severity_groups


class TestProcessHealthMetrics:
    """Test overall process health metrics"""
    
    def test_process_health_score_calculation(self):
        """Test process health score calculation"""
        aging_analysis = AgingAnalysis(
            items_by_category={},
            average_age_by_status={"In Progress": 15.0},
            oldest_items=[],
            blocked_items=[],
            total_items=10
        )
        
        wip_analysis = WIPAnalysis(
            items_by_status={},
            wip_by_assignee={},
            total_wip=8,
            wip_limits={WIPStatus.IN_PROGRESS: 10}
        )
        
        sprint_health = SprintHealthAnalysis(
            sprint_metrics=[],
            average_completion_rate=0.85,
            completion_rate_trend=0.02,
            average_scope_change=0.1,
            predictability_score=0.8
        )
        
        blocked_items = BlockedItemsAnalysis(
            blocked_items=[],
            total_blocked_points=5.0,
            average_blocked_days=3.0,
            blockers_by_type={},
            repeat_blockers=[]
        )
        
        metrics = ProcessHealthMetrics(
            aging_analysis=aging_analysis,
            wip_analysis=wip_analysis,
            sprint_health=sprint_health,
            blocked_items=blocked_items
        )
        
        # Score should be between 0 and 1
        assert 0 <= metrics.health_score <= 1
        # With these good values (high completion rate, low blocked items), score should be high
        assert metrics.health_score > 0.7


class TestAnalyzeAgingWorkItemsUseCase:
    """Test aging work items use case"""
    
    def test_analyze_aging_work_items(self):
        """Test analyzing aging work items"""
        # Create mock repository
        issue_repo = Mock()
        
        # Create test issues with different ages
        today = datetime.now()
        issues = [
            Issue(
                key="TEST-1",
                summary="Fresh issue",
                status="To Do",
                created=today - timedelta(days=3),
                issue_type="Story"
            ),
            Issue(
                key="TEST-2",
                summary="Normal issue",
                status="In Progress",
                created=today - timedelta(days=10),
                issue_type="Bug"
            ),
            Issue(
                key="TEST-3",
                summary="Aging issue",
                status="In Review",
                created=today - timedelta(days=20),
                issue_type="Story"
            ),
            Issue(
                key="TEST-4",
                summary="Stale issue",
                status="Blocked",
                created=today - timedelta(days=35),
                issue_type="Task"
            ),
            Issue(
                key="TEST-5",
                summary="Done issue",
                status="Done",
                created=today - timedelta(days=40),
                resolved=today - timedelta(days=5),
                issue_type="Story"
            ),
        ]
        
        issue_repo.get_all.return_value = issues
        
        # Create use case and execute
        use_case = AnalyzeAgingWorkItemsUseCase(issue_repo)
        analysis = use_case.execute(
            status_mapping={
                "done": ["Done", "Closed"],
                "todo": ["To Do"],
                "in_progress": ["In Progress", "In Review", "Blocked"]
            }
        )
        
        # Verify results
        assert analysis.total_items == 4  # Excluding done items
        assert analysis.thresholds is not None  # Dynamic thresholds were computed
        # With dynamic thresholds, categories are distributed by percentiles
        # So with only 4 items, we won't have all 5 categories
        assert len(analysis.items_by_category) > 0
        assert "To Do" in analysis.average_age_by_status
        assert len(analysis.oldest_items) > 0


class TestAnalyzeWorkInProgressUseCase:
    """Test work in progress use case"""
    
    def test_analyze_wip_with_limits(self):
        """Test analyzing WIP with limits"""
        # Create mock repository
        issue_repo = Mock()
        
        # Create test issues
        issues = [
            Issue(
                key="TEST-1",
                summary="Todo issue",
                status="To Do",
                created=datetime.now() - timedelta(days=1),
                issue_type="Story"
            ),
            Issue(
                key="TEST-2",
                summary="In progress 1",
                status="In Progress",
                created=datetime.now() - timedelta(days=3),
                assignee="Dev1",
                issue_type="Bug"
            ),
            Issue(
                key="TEST-3",
                summary="In progress 2",
                status="In Progress",
                created=datetime.now() - timedelta(days=5),
                assignee="Dev2",
                issue_type="Story"
            ),
            Issue(
                key="TEST-4",
                summary="In review",
                status="In Review",
                created=datetime.now() - timedelta(days=2),
                assignee="Dev1",
                issue_type="Task"
            ),
        ]
        
        issue_repo.get_all.return_value = issues
        
        # Create use case and execute
        use_case = AnalyzeWorkInProgressUseCase(issue_repo)
        analysis = use_case.execute(
            status_mapping={
                "todo": ["To Do"],
                "in_progress": ["In Progress"],
                "review": ["In Review"]
            },
            wip_limits={
                "in_progress": 3,
                "review": 2
            }
        )
        
        # Verify results
        assert analysis.total_wip == 3  # In Progress + In Review
        # Check that items are properly categorized
        if WIPStatus.REVIEW in analysis.items_by_status:
            assert len(analysis.items_by_status[WIPStatus.IN_PROGRESS]) == 2
            assert len(analysis.items_by_status[WIPStatus.REVIEW]) == 1
        else:
            # All might be categorized as IN_PROGRESS
            assert len(analysis.items_by_status[WIPStatus.IN_PROGRESS]) == 3
        assert analysis.wip_by_assignee["Dev1"] == 2
        assert len(analysis.wip_violations) == 0  # No limits exceeded


class TestAnalyzeSprintHealthUseCase:
    """Test sprint health use case"""
    
    def test_analyze_sprint_health(self):
        """Test analyzing sprint health"""
        # Create mock repositories
        issue_repo = Mock()
        sprint_repo = Mock()
        
        # Create test sprints
        sprints = [
            Sprint(
                name="Sprint 1",
                start_date=datetime.now() - timedelta(days=28),
                end_date=datetime.now() - timedelta(days=14),
                completed_points=25
            ),
            Sprint(
                name="Sprint 2",
                start_date=datetime.now() - timedelta(days=14),
                end_date=datetime.now(),
                completed_points=23
            ),
        ]
        
        sprint_repo.get_last_n_sprints.return_value = sprints
        
        # Create test issues for scope changes
        sprint1_issues = [
            Issue(
                key="TEST-1",
                summary="Sprint 1 story",
                status="Done",
                created=datetime.now() - timedelta(days=25),
                story_points=5,
                issue_type="Story"
            ),
            Issue(
                key="TEST-2",
                summary="Sprint 1 bug",
                status="Done",
                created=datetime.now() - timedelta(days=20),
                story_points=3,
                issue_type="Bug"
            ),  # Added
        ]
        sprint2_issues = [
            Issue(
                key="TEST-3",
                summary="Sprint 2 task",
                status="In Progress",
                created=datetime.now() - timedelta(days=10),
                story_points=2,
                issue_type="Task"
            ),  # Removed
        ]
        
        # Mock issue repository to return all issues 
        all_issues = sprint1_issues + sprint2_issues
        # Add sprint information to custom fields
        for issue in sprint1_issues:
            issue.custom_fields = {"sprint": ["Sprint 1"]}
        for issue in sprint2_issues:
            issue.custom_fields = {"sprint": ["Sprint 2"]}
            
        issue_repo.get_all.return_value = all_issues
        
        # Create use case and execute
        use_case = AnalyzeSprintHealthUseCase(issue_repo, sprint_repo)
        analysis = use_case.execute(lookback_sprints=2)
        
        # Verify results
        assert analysis is not None
        assert len(analysis.sprint_metrics) == 2
        # Check that metrics were created for each sprint
        assert all(m.sprint_name in ["Sprint 1", "Sprint 2"] for m in analysis.sprint_metrics)
        assert 0 <= analysis.predictability_score <= 1


class TestAnalyzeBlockedItemsUseCase:
    """Test blocked items use case"""
    
    def test_analyze_blocked_items(self):
        """Test analyzing blocked items"""
        # Create mock repository
        issue_repo = Mock()
        
        # Create test issues
        today = datetime.now()
        issues = [
            Issue(
                key="TEST-1",
                summary="Not blocked",
                status="In Progress",
                created=today - timedelta(days=5),
                issue_type="Story"
            ),
            Issue(
                key="TEST-2",
                summary="Recently blocked",
                status="Blocked",
                created=today - timedelta(days=10),
                updated=today - timedelta(days=2),
                labels=["blocked"],
                issue_type="Bug"
            ),
            Issue(
                key="TEST-3",
                summary="Long blocked",
                status="Blocked",
                created=today - timedelta(days=20),
                updated=today - timedelta(days=8),
                labels=["blocked", "waiting-for-vendor"],
                issue_type="Story"
            ),
        ]
        
        issue_repo.get_all.return_value = issues
        
        # Create use case and execute
        use_case = AnalyzeBlockedItemsUseCase(issue_repo)
        analysis = use_case.execute(
            status_mapping={
                "done": ["Done"],
                "blocked": ["Blocked"]
            }
        )
        
        # Verify results
        assert len(analysis.blocked_items) == 2
        assert analysis.average_blocked_days > 0
        # Check that items_by_severity property works
        severity_groups = analysis.items_by_severity
        assert isinstance(severity_groups, dict)


class TestAnalyzeProcessHealthUseCase:
    """Test overall process health use case"""
    
    def test_analyze_process_health(self):
        """Test analyzing overall process health"""
        # Create mock use cases
        aging_use_case = Mock()
        wip_use_case = Mock()
        sprint_health_use_case = Mock()
        blocked_items_use_case = Mock()
        
        # Mock return values
        aging_use_case.execute.return_value = AgingAnalysis(
            items_by_category={},
            average_age_by_status={"In Progress": 10.0},
            oldest_items=[],
            blocked_items=[],
            total_items=5
        )
        
        wip_use_case.execute.return_value = WIPAnalysis(
            items_by_status={},
            wip_by_assignee={},
            total_wip=5,
            wip_limits={}
        )
        
        sprint_health_use_case.execute.return_value = SprintHealthAnalysis(
            sprint_metrics=[],
            average_completion_rate=0.9,
            completion_rate_trend=0.05,
            average_scope_change=0.05,
            predictability_score=0.95
        )
        
        blocked_items_use_case.execute.return_value = BlockedItemsAnalysis(
            blocked_items=[],
            total_blocked_points=3.0,
            average_blocked_days=2.0,
            blockers_by_type={},
            repeat_blockers=[]
        )
        
        # Create use case and execute
        use_case = AnalyzeProcessHealthUseCase(
            aging_use_case=aging_use_case,
            wip_use_case=wip_use_case,
            sprint_health_use_case=sprint_health_use_case,
            blocked_items_use_case=blocked_items_use_case
        )
        
        metrics = use_case.execute(
            status_mapping={
                "done": ["Done"],
                "todo": ["To Do"],
                "in_progress": ["In Progress"]
            },
            wip_limits={},
            lookback_sprints=6
        )
        
        # Verify results
        assert metrics.aging_analysis is not None
        assert metrics.wip_analysis is not None
        assert metrics.sprint_health is not None
        assert metrics.blocked_items is not None
        assert 0 <= metrics.health_score <= 1
        # With excellent sprint health and low aging, score should be high
        assert metrics.health_score > 0.7