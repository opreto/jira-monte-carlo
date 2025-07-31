from datetime import datetime, timedelta

from src.domain.entities import Issue, Sprint, Team


class TestIssue:
    def test_cycle_time_calculation(self):
        created = datetime(2023, 1, 1)
        resolved = datetime(2023, 1, 10)

        issue = Issue(
            key="TEST-1",
            summary="Test issue",
            issue_type="Story",
            status="Done",
            created=created,
            resolved=resolved,
        )

        assert issue.cycle_time == 9

    def test_cycle_time_unresolved(self):
        issue = Issue(
            key="TEST-1",
            summary="Test issue",
            issue_type="Story",
            status="In Progress",
            created=datetime(2023, 1, 1),
        )

        assert issue.cycle_time is None

    def test_age_calculation(self):
        created = datetime.now() - timedelta(days=5)
        issue = Issue(
            key="TEST-1",
            summary="Test issue",
            issue_type="Story",
            status="In Progress",
            created=created,
        )

        assert issue.age == 5


class TestSprint:
    def test_velocity_calculation(self):
        sprint = Sprint(
            name="Sprint 1",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 14),
            completed_points=42.0,
        )

        assert sprint.velocity == 42.0

    def test_duration_calculation(self):
        sprint = Sprint(
            name="Sprint 1",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 14),
        )

        assert sprint.duration_days == 13


class TestTeam:
    def test_average_velocity(self):
        team = Team(
            name="Alpha Team",
            members=["Alice", "Bob"],
            historical_velocities=[20.0, 30.0, 40.0],
        )

        assert team.average_velocity == 30.0

    def test_average_velocity_empty(self):
        team = Team(name="Alpha Team", members=["Alice", "Bob"], historical_velocities=[])

        assert team.average_velocity == 0.0

    def test_velocity_std_dev(self):
        team = Team(
            name="Alpha Team",
            members=["Alice", "Bob"],
            historical_velocities=[20.0, 30.0, 40.0],
        )

        # Standard deviation of [20, 30, 40] is ~8.16
        assert abs(team.velocity_std_dev - 8.16) < 0.1

    def test_velocity_std_dev_insufficient_data(self):
        team = Team(name="Alpha Team", members=["Alice", "Bob"], historical_velocities=[20.0])

        assert team.velocity_std_dev == 0.0


class TestSimulationResult:
    def test_simulation_result_creation(self):
        """Test that SimulationResult holds all necessary data"""
        from src.domain.entities import SimulationResult

        percentiles = {0.5: 6.0, 0.85: 8.0, 0.95: 9.0}
        completion_dates = [
            datetime.now() + timedelta(days=84),
            datetime.now() + timedelta(days=98),
            datetime.now() + timedelta(days=112),
        ]

        result = SimulationResult(
            percentiles=percentiles,
            mean_completion_date=datetime.now() + timedelta(days=91),
            std_dev_days=14.0,
            probability_distribution=[0.1, 0.3, 0.4, 0.2],
            completion_dates=completion_dates,
            confidence_intervals={(0.5, (5, 7)), (0.85, (7, 9))},
            completion_sprints=[6, 7, 8],
        )

        assert result.percentiles[0.5] == 6.0
        assert result.percentiles[0.85] == 8.0
        assert len(result.completion_dates) == 3
        assert len(result.completion_sprints) == 3
        assert result.std_dev_days == 14.0
