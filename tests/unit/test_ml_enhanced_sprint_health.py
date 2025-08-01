"""Tests for ML Enhanced Sprint Health Use Case."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch


from src.application.ml_enhanced_use_cases import MLEnhancedSprintHealthUseCase
from src.domain.entities import Sprint
from src.domain.process_health import SprintHealthAnalysis
from src.infrastructure.repositories import (
    InMemorySprintRepository,
    InMemoryIssueRepository,
)


class TestMLEnhancedSprintHealthUseCase:
    """Test ML-enhanced sprint health analysis."""

    def test_ml_enhanced_sprint_health_initialization(self):
        """Test initialization of ML-enhanced sprint health use case."""
        issue_repo = InMemoryIssueRepository()
        sprint_repo = InMemorySprintRepository()

        # Without ML
        use_case = MLEnhancedSprintHealthUseCase(
            issue_repo, sprint_repo, project_key="TEST-123", enable_ml=False
        )
        assert use_case.lookback_optimizer is None

        # With ML
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                use_case = MLEnhancedSprintHealthUseCase(
                    issue_repo, sprint_repo, project_key="TEST-123", enable_ml=True
                )
                assert use_case.lookback_optimizer is not None
                assert use_case.project_key == "TEST-123"

    def test_execute_without_ml(self):
        """Test execution without ML enabled."""
        # Create test data
        issue_repo = InMemoryIssueRepository()
        sprint_repo = InMemorySprintRepository()

        # Add some sprints
        base_date = datetime.now() - timedelta(days=180)
        for i in range(10):
            sprint = Sprint(
                name=f"Sprint {i + 1}",
                start_date=base_date + timedelta(days=i * 14),
                end_date=base_date + timedelta(days=(i + 1) * 14),
                completed_points=20 + i,
            )
            sprint_repo.add_sprints([sprint])

        use_case = MLEnhancedSprintHealthUseCase(
            issue_repo, sprint_repo, project_key="TEST-123", enable_ml=False
        )

        health_analysis, ml_decisions = use_case.execute()

        assert isinstance(health_analysis, SprintHealthAnalysis)
        assert ml_decisions.has_ml_decisions() is False

    def test_execute_with_ml(self):
        """Test execution with ML enabled."""
        # Create test data
        issue_repo = InMemoryIssueRepository()
        sprint_repo = InMemorySprintRepository()

        # Add many sprints to trigger ML
        base_date = datetime.now() - timedelta(days=400)
        for i in range(30):
            sprint = Sprint(
                name=f"Sprint {i + 1}",
                start_date=base_date + timedelta(days=i * 14),
                end_date=base_date + timedelta(days=(i + 1) * 14),
                completed_points=20 + (i % 5) * 5,  # Variable velocity
            )
            sprint_repo.add_sprints([sprint])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                use_case = MLEnhancedSprintHealthUseCase(
                    issue_repo, sprint_repo, project_key="TEST-123", enable_ml=True
                )

                health_analysis, ml_decisions = use_case.execute()

                assert isinstance(health_analysis, SprintHealthAnalysis)
                assert ml_decisions.has_ml_decisions() is True

                # Check ML decision details
                decisions = ml_decisions.get_decisions_by_type("sprint_health_lookback")
                assert len(decisions) > 0
                decision = decisions[0]
                assert decision.model_name == "SprintHealthLookbackOptimizer"
                assert decision.value > 0  # Should have a lookback value

    def test_ml_decision_recording(self):
        """Test that ML decisions are properly recorded."""
        issue_repo = InMemoryIssueRepository()
        sprint_repo = InMemorySprintRepository()

        # Add sprints
        base_date = datetime.now() - timedelta(days=300)
        for i in range(25):
            sprint = Sprint(
                name=f"Sprint {i + 1}",
                start_date=base_date + timedelta(days=i * 14),
                end_date=base_date + timedelta(days=(i + 1) * 14),
                completed_points=25,
            )
            sprint_repo.add_sprints([sprint])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                use_case = MLEnhancedSprintHealthUseCase(
                    issue_repo, sprint_repo, project_key="TEST-123", enable_ml=True
                )

                _, ml_decisions = use_case.execute()

                # Verify decision structure
                decisions = ml_decisions.get_decisions_by_type("sprint_health_lookback")
                assert len(decisions) == 1

                decision = decisions[0]
                assert decision.decision_type == "sprint_health_lookback"
                assert "confidence" in dir(decision)
                assert "primary_factor" in dir(decision)
                assert "factors" in dir(decision)

    def test_fallback_to_heuristic(self):
        """Test fallback to heuristic when insufficient data."""
        issue_repo = InMemoryIssueRepository()
        sprint_repo = InMemorySprintRepository()

        # Add only a few sprints (less than min required)
        base_date = datetime.now() - timedelta(days=60)
        for i in range(5):
            sprint = Sprint(
                name=f"Sprint {i + 1}",
                start_date=base_date + timedelta(days=i * 14),
                end_date=base_date + timedelta(days=(i + 1) * 14),
                completed_points=20,
            )
            sprint_repo.add_sprints([sprint])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                use_case = MLEnhancedSprintHealthUseCase(
                    issue_repo, sprint_repo, project_key="TEST-123", enable_ml=True
                )

                _, ml_decisions = use_case.execute()

                # Should have a decision but using fallback
                decisions = ml_decisions.get_decisions_by_type("sprint_health_lookback")
                assert len(decisions) == 1
                assert decisions[0].method == "fallback_heuristic"

    def test_custom_lookback_override(self):
        """Test that custom lookback overrides ML optimization."""
        issue_repo = InMemoryIssueRepository()
        sprint_repo = InMemorySprintRepository()

        # Add sprints
        base_date = datetime.now() - timedelta(days=200)
        for i in range(20):
            sprint = Sprint(
                name=f"Sprint {i + 1}",
                start_date=base_date + timedelta(days=i * 14),
                end_date=base_date + timedelta(days=(i + 1) * 14),
                completed_points=25,
            )
            sprint_repo.add_sprints([sprint])

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                use_case = MLEnhancedSprintHealthUseCase(
                    issue_repo, sprint_repo, project_key="TEST-123", enable_ml=True
                )

                # Execute with custom lookback
                health_analysis, ml_decisions = use_case.execute(lookback_sprints=5)

                # Should use the custom lookback, no ML decision
                assert len(health_analysis.sprint_metrics) <= 5
                # ML decisions might still be created but won't affect the lookback used
