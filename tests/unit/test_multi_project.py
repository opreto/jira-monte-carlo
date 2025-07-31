"""Tests for multi-project domain entities"""

from datetime import datetime
from pathlib import Path

from src.domain.entities import Issue
from src.domain.multi_project import AggregatedMetrics, MultiProjectReport, ProjectData


class TestProjectData:
    def test_project_data_creation(self):
        # Create test issues
        issues = [
            Issue(
                key="TEST-1",
                summary="Issue 1",
                issue_type="Story",
                status="Done",
                created=datetime.now(),
                story_points=5.0,
            ),
            Issue(
                key="TEST-2",
                summary="Issue 2",
                issue_type="Story",
                status="In Progress",
                created=datetime.now(),
                story_points=3.0,
            ),
            Issue(
                key="TEST-3",
                summary="Issue 3",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=8.0,
            ),
        ]

        project = ProjectData(
            name="Test Project",
            file_path=Path("test.csv"),
            issues=issues,
            remaining_work=8.0,
        )

        assert project.name == "Test Project"
        assert project.total_issues == 3
        assert project.done_issues == 1
        assert project.in_progress_issues == 1
        assert project.todo_issues == 1
        # 1 done out of 3 issues = 33.33%
        assert abs(project.completion_percentage - 33.33) < 0.1

    def test_project_data_with_story_size_breakdown(self):
        """Test that ProjectData properly handles story_size_breakdown"""
        story_breakdown = {1.0: 5, 3.0: 3, 5.0: 2, 8.0: 1}

        project = ProjectData(
            name="Test Project",
            file_path=Path("test.csv"),
            remaining_work=50.0,
            story_size_breakdown=story_breakdown,
        )

        assert project.story_size_breakdown == story_breakdown
        assert project.story_size_breakdown[1.0] == 5
        assert project.story_size_breakdown[3.0] == 3


class TestAggregatedMetrics:
    def test_aggregated_metrics_calculation(self):
        metrics = AggregatedMetrics(
            total_projects=3,
            total_issues=100,
            total_completed_issues=60,
            total_remaining_work=150.0,
            combined_velocity=60.0,
        )

        assert metrics.overall_completion_percentage == 60.0
        assert metrics.total_projects == 3


class TestMultiProjectReport:
    def test_multi_project_report(self):
        # Create test projects
        project1 = ProjectData(
            name="Project A", file_path=Path("a.csv"), remaining_work=50.0
        )

        project2 = ProjectData(
            name="Project B", file_path=Path("b.csv"), remaining_work=75.0
        )

        # Create aggregated metrics
        metrics = AggregatedMetrics(
            total_projects=2,
            total_issues=50,
            total_completed_issues=30,
            total_remaining_work=125.0,
            combined_velocity=30.0,
        )

        report = MultiProjectReport(
            projects=[project1, project2], aggregated_metrics=metrics
        )

        assert report.has_multiple_projects is True
        assert report.get_project_by_name("Project A") == project1
        assert report.get_project_by_name("Project C") is None
