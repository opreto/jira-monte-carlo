from datetime import datetime, timedelta
from unittest.mock import Mock

from src.application.use_cases import (
    AnalyzeHistoricalDataUseCase,
    CalculateRemainingWorkUseCase,
    CalculateVelocityUseCase,
    RunMonteCarloSimulationUseCase,
)
from src.domain.entities import Issue, SimulationConfig, Sprint
from src.domain.value_objects import VelocityMetrics


class TestCalculateVelocityUseCase:
    def test_calculate_velocity_with_story_points(self):
        # Setup
        issue_repo = Mock()
        sprint_repo = Mock()

        # Create test data
        issues = [
            Issue(
                key=f"TEST-{i}",
                summary=f"Issue {i}",
                issue_type="Story",
                status="Done",
                created=datetime.now() - timedelta(days=10),
                resolved=datetime.now() - timedelta(days=i),
                story_points=5.0,
            )
            for i in range(1, 6)
        ]

        sprints = [
            Sprint(
                name=f"Sprint {i}",
                start_date=datetime.now() - timedelta(days=14 * i),
                end_date=datetime.now() - timedelta(days=14 * (i - 1)),
                completed_points=25.0,
                completed_issues=issues,
            )
            for i in range(1, 4)
        ]

        sprint_repo.get_last_n_sprints.return_value = sprints
        sprint_repo.get_all.return_value = sprints

        # Execute
        use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
        metrics = use_case.execute(lookback_sprints=3, velocity_field="story_points")

        # Assert
        assert metrics.average == 25.0
        assert metrics.median == 25.0
        assert metrics.std_dev == 0.0
        assert metrics.min_value == 25.0
        assert metrics.max_value == 25.0

    def test_calculate_velocity_empty_sprints(self):
        issue_repo = Mock()
        sprint_repo = Mock()
        sprint_repo.get_last_n_sprints.return_value = []
        sprint_repo.get_all.return_value = []

        use_case = CalculateVelocityUseCase(issue_repo, sprint_repo)
        metrics = use_case.execute()

        assert metrics.average == 0
        assert metrics.median == 0
        assert metrics.std_dev == 0


class TestRunMonteCarloSimulationUseCase:
    def test_monte_carlo_simulation(self):
        issue_repo = Mock()

        velocity_metrics = VelocityMetrics(
            average=20.0, median=20.0, std_dev=5.0, min_value=10.0, max_value=30.0, trend=0.5
        )

        config = SimulationConfig(num_simulations=1000, confidence_levels=[0.5, 0.85, 0.95], sprint_duration_days=14)

        use_case = RunMonteCarloSimulationUseCase(issue_repo)
        results = use_case.execute(remaining_work=100.0, velocity_metrics=velocity_metrics, config=config)

        # Assert structure
        assert len(results.percentiles) == 3
        assert 0.5 in results.percentiles
        assert 0.85 in results.percentiles
        assert 0.95 in results.percentiles

        # Assert logical ordering (with sprints, values might be equal)
        assert results.percentiles[0.5] <= results.percentiles[0.85]
        assert results.percentiles[0.85] <= results.percentiles[0.95]

        # Assert reasonable values
        assert results.mean_completion_date > datetime.now()
        assert results.std_dev_days > 0
        assert len(results.probability_distribution) > 0


class TestCalculateRemainingWorkUseCase:
    def test_calculate_remaining_work_story_points(self):
        issues = [
            Issue(
                key=f"TEST-{i}",
                summary=f"Issue {i}",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=8.0,
            )
            for i in range(1, 6)
        ]

        issue_repo = Mock()
        issue_repo.get_by_status.return_value = issues

        use_case = CalculateRemainingWorkUseCase(issue_repo)
        remaining = use_case.execute(todo_statuses=["To Do"], velocity_field="story_points")

        assert remaining == 40.0

    def test_calculate_remaining_work_count(self):
        issues = [
            Issue(key=f"TEST-{i}", summary=f"Issue {i}", issue_type="Story", status="To Do", created=datetime.now())
            for i in range(1, 6)
        ]

        issue_repo = Mock()
        issue_repo.get_by_status.return_value = issues

        use_case = CalculateRemainingWorkUseCase(issue_repo)
        remaining = use_case.execute(todo_statuses=["To Do"], velocity_field="count")

        assert remaining == 5.0

    def test_get_story_size_breakdown(self):
        """Test that story size breakdown correctly groups stories by size"""
        issues = [
            Issue(
                key="TEST-1",
                summary="Small 1",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=1.0,
            ),
            Issue(
                key="TEST-2",
                summary="Small 2",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=1.0,
            ),
            Issue(
                key="TEST-3",
                summary="Small 3",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=1.0,
            ),
            Issue(
                key="TEST-4",
                summary="Medium 1",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=3.0,
            ),
            Issue(
                key="TEST-5",
                summary="Medium 2",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=3.0,
            ),
            Issue(
                key="TEST-6",
                summary="Large",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=5.0,
            ),
            Issue(
                key="TEST-7",
                summary="No points",
                issue_type="Story",
                status="To Do",
                created=datetime.now(),
                story_points=None,
            ),
        ]

        issue_repo = Mock()
        issue_repo.get_by_status.return_value = issues

        use_case = CalculateRemainingWorkUseCase(issue_repo)
        breakdown = use_case.get_story_size_breakdown(["To Do"])

        assert breakdown == {1.0: 3, 3.0: 2, 5.0: 1}
        assert 0.0 not in breakdown  # Should not include stories without points


class TestAnalyzeHistoricalDataUseCase:
    def test_analyze_historical_data(self):
        # Create issues completed over several weeks
        issues = []
        base_date = datetime.now() - timedelta(days=30)

        for week in range(4):
            week_start = base_date + timedelta(days=week * 7)
            for day in range(5):  # 5 issues per week
                issue = Issue(
                    key=f"TEST-{week}-{day}",
                    summary=f"Issue {week}-{day}",
                    issue_type="Story",
                    status="Done",
                    created=week_start,
                    resolved=week_start + timedelta(days=day),
                    story_points=5.0,
                )
                issues.append(issue)

        issue_repo = Mock()
        issue_repo.get_completed_in_range.return_value = issues

        use_case = AnalyzeHistoricalDataUseCase(issue_repo)
        historical = use_case.execute(lookback_days=60)

        # Assert we have data
        assert len(historical.velocities) > 0
        assert len(historical.cycle_times) > 0
        assert len(historical.throughput) > 0
        assert len(historical.dates) > 0
