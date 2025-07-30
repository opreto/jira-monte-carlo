import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.domain.entities import Issue, Sprint
from src.domain.value_objects import DateRange, FieldMapping
from src.infrastructure.repositories import (
    FileConfigRepository,
    InMemoryIssueRepository,
    InMemorySprintRepository,
    SprintExtractor,
)


class TestInMemoryIssueRepository:
    def test_add_and_get_all_issues(self):
        repo = InMemoryIssueRepository()

        issues = [
            Issue(
                key=f"TEST-{i}",
                summary=f"Issue {i}",
                issue_type="Story",
                status="Done" if i % 2 == 0 else "To Do",
                created=datetime.now(),
            )
            for i in range(5)
        ]

        repo.add_issues(issues)

        assert len(repo.get_all()) == 5

    def test_get_by_status(self):
        repo = InMemoryIssueRepository()

        issues = [
            Issue(
                key=f"TEST-{i}",
                summary=f"Issue {i}",
                issue_type="Story",
                status="Done" if i < 3 else "To Do",
                created=datetime.now(),
            )
            for i in range(5)
        ]

        repo.add_issues(issues)

        done_issues = repo.get_by_status("Done")
        todo_issues = repo.get_by_status("To Do")

        assert len(done_issues) == 3
        assert len(todo_issues) == 2
        assert len(repo.get_by_status("Unknown")) == 0

    def test_get_by_date_range(self):
        repo = InMemoryIssueRepository()

        base_date = datetime.now()
        issues = [
            Issue(
                key=f"TEST-{i}",
                summary=f"Issue {i}",
                issue_type="Story",
                status="Done",
                created=base_date - timedelta(days=i * 5),
            )
            for i in range(5)
        ]

        repo.add_issues(issues)

        # Get issues from last 10 days
        date_range = DateRange(start=base_date - timedelta(days=10), end=base_date)

        filtered_issues = repo.get_by_date_range(date_range)
        assert len(filtered_issues) == 3  # Issues 0, 1, 2

    def test_get_completed_in_range(self):
        repo = InMemoryIssueRepository()

        base_date = datetime.now()
        issues = []

        # Create issues with different resolved dates
        for i in range(5):
            issue = Issue(
                key=f"TEST-{i}",
                summary=f"Issue {i}",
                issue_type="Story",
                status="Done",
                created=base_date - timedelta(days=20),
                resolved=base_date - timedelta(days=i * 5) if i < 3 else None,
            )
            issues.append(issue)

        repo.add_issues(issues)

        # Get issues resolved in last 10 days
        date_range = DateRange(start=base_date - timedelta(days=10), end=base_date)

        completed_issues = repo.get_completed_in_range(date_range)
        assert len(completed_issues) == 3  # Issues 0, 1, and 2 (10 days is inclusive)


class TestInMemorySprintRepository:
    def test_add_and_get_sprints(self):
        repo = InMemorySprintRepository()

        sprints = [
            Sprint(
                name=f"Sprint {i}",
                start_date=datetime.now() - timedelta(days=14 * (5 - i)),
                end_date=datetime.now() - timedelta(days=14 * (4 - i)),
            )
            for i in range(3)
        ]

        repo.add_sprints(sprints)

        assert len(repo.get_all()) == 3
        # Check they're sorted by start date (oldest first)
        all_sprints = repo.get_all()
        assert all_sprints[0].name == "Sprint 0"  # Oldest
        assert all_sprints[1].name == "Sprint 1"
        assert all_sprints[2].name == "Sprint 2"  # Newest

    def test_get_last_n_sprints(self):
        repo = InMemorySprintRepository()

        # Create past and future sprints
        base_date = datetime.now()
        sprints = []

        # Past sprints
        for i in range(5):
            sprint = Sprint(
                name=f"Past Sprint {i}",
                start_date=base_date - timedelta(days=14 * (i + 2)),
                end_date=base_date - timedelta(days=14 * (i + 1)),
            )
            sprints.append(sprint)

        # Future sprint
        future_sprint = Sprint(
            name="Future Sprint",
            start_date=base_date + timedelta(days=1),
            end_date=base_date + timedelta(days=14),
        )
        sprints.append(future_sprint)

        repo.add_sprints(sprints)

        # Get last 3 completed sprints
        last_sprints = repo.get_last_n_sprints(3)

        assert len(last_sprints) == 3
        assert all("Past Sprint" in s.name for s in last_sprints)
        assert "Future Sprint" not in [s.name for s in last_sprints]


class TestFileConfigRepository:
    def test_save_and_load_field_mapping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FileConfigRepository(Path(tmpdir))

            mapping = FieldMapping(
                key_field="Issue Key", summary_field="Summary", status_field="Status"
            )

            # Save
            repo.save_field_mapping(mapping)

            # Load
            loaded = repo.load_field_mapping()

            assert loaded is not None
            assert loaded.key_field == "Issue Key"
            assert loaded.summary_field == "Summary"
            assert loaded.status_field == "Status"

    def test_load_nonexistent_field_mapping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FileConfigRepository(Path(tmpdir))

            loaded = repo.load_field_mapping()
            assert loaded is None

    def test_save_and_load_status_mapping(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = FileConfigRepository(Path(tmpdir))

            status_mapping = {
                "done": ["Done", "Closed", "Resolved"],
                "in_progress": ["In Progress", "In Review"],
                "todo": ["To Do", "Open", "Backlog"],
            }

            # Save
            repo.save_status_mapping(status_mapping)

            # Load
            loaded = repo.load_status_mapping()

            assert loaded is not None
            assert loaded["done"] == ["Done", "Closed", "Resolved"]
            assert loaded["in_progress"] == ["In Progress", "In Review"]
            assert loaded["todo"] == ["To Do", "Open", "Backlog"]


class TestSprintExtractor:
    def test_extract_sprints_from_issues(self):
        # Create issues with sprint information
        issues = []

        for sprint_num in range(1, 4):
            for i in range(5):
                issue = Issue(
                    key=f"TEST-{sprint_num}-{i}",
                    summary=f"Issue {i} in Sprint {sprint_num}",
                    issue_type="Story",
                    status="Done",
                    created=datetime.now() - timedelta(days=20),
                    resolved=datetime.now() - timedelta(days=sprint_num * 7 - i),
                    story_points=5.0,
                    custom_fields={"Sprint": f"Sprint {sprint_num}"},
                )
                issues.append(issue)

        # Extract sprints
        sprints = SprintExtractor.extract_sprints_from_issues(
            issues, sprint_field="Sprint", done_statuses=["Done"]
        )

        assert len(sprints) == 3

        # Check sprint properties (sorted by start date, so Sprint 3 is first)
        expected_order = [3, 2, 1]  # Sprint 3 has oldest dates
        for i, sprint in enumerate(sprints):
            expected_num = expected_order[i]
            assert sprint.name == f"Sprint {expected_num}"
            assert sprint.completed_points == 25.0  # 5 issues * 5 points
            assert len(sprint.completed_issues) == 5

    def test_extract_sprints_handles_missing_data(self):
        issues = [
            Issue(
                key="TEST-1",
                summary="No sprint field",
                issue_type="Story",
                status="Done",
                created=datetime.now(),
                resolved=datetime.now(),
            ),
            Issue(
                key="TEST-2",
                summary="Not done",
                issue_type="Story",
                status="In Progress",
                created=datetime.now(),
                custom_fields={"Sprint": "Sprint 1"},
            ),
            Issue(
                key="TEST-3",
                summary="No resolved date",
                issue_type="Story",
                status="Done",
                created=datetime.now(),
                custom_fields={"Sprint": "Sprint 1"},
            ),
        ]

        sprints = SprintExtractor.extract_sprints_from_issues(
            issues, sprint_field="Sprint", done_statuses=["Done"]
        )

        # Should not create any sprints due to missing data
        assert len(sprints) == 0
