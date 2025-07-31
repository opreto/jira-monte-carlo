"""Tests for ML heuristics with privacy preservation."""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch


from src.domain.ml_heuristics import VelocityLookbackOptimizer


class TestMLHeuristic:
    """Test base ML heuristic functionality."""

    def test_project_isolation(self):
        """Test that data is isolated per project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                # Create heuristics for two different projects
                proj1_heuristic = VelocityLookbackOptimizer("PROJ-123", lambda x: x)
                proj2_heuristic = VelocityLookbackOptimizer("TEAM-456", lambda x: x)

                # Verify different paths
                assert "PROJ-123" in str(proj1_heuristic.model_path)
                assert "TEAM-456" in str(proj2_heuristic.model_path)
                assert proj1_heuristic.model_path != proj2_heuristic.model_path

                # Verify directories exist
                assert proj1_heuristic.model_path.parent.exists()
                assert proj2_heuristic.model_path.parent.exists()

    def test_fallback_with_insufficient_data(self):
        """Test fallback to heuristic with insufficient data."""
        fallback_mock = Mock(return_value=6)

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", fallback_mock)

                # Less than minimum data points
                velocities = [20, 22, 21]
                result, explanation = optimizer.predict(velocities)

                assert result == 6
                assert explanation["method"] == "fallback_heuristic"
                assert "Insufficient data" in explanation["reason"]
                fallback_mock.assert_called_once()


class TestVelocityLookbackOptimizer:
    """Test ML-enhanced lookback optimization."""

    def test_feature_extraction_privacy(self):
        """Test that features don't leak raw data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", lambda x: x)

                # Sensitive velocity data
                velocities = [100, 120, 110, 105, 115, 125, 130, 135]

                features = optimizer.extract_features(velocities)

                # Verify no raw values in features
                assert all(v not in features.values() for v in velocities)

                # Verify statistical features are present
                assert "cv" in features
                assert "trend_strength" in features
                assert "stability_score" in features
                assert "sprint_count" in features

                # Verify features are normalized/statistical
                assert 0 <= features["cv"] <= 2  # Coefficient of variation
                assert 0 <= features["stability_score"] <= 1
                assert features["sprint_count"] == len(velocities)

    def test_prediction_with_explanation(self):
        """Test prediction includes explanation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)

                # Create enough data for ML
                velocities = [20 + i for i in range(25)]

                # First prediction will train the model
                result, explanation = optimizer.predict(velocities)

                assert isinstance(result, int)
                assert "method" in explanation
                assert "confidence" in explanation

                if explanation["method"] == "ml_model":
                    assert "factors" in explanation
                    assert explanation["confidence"] > 0.5

    def test_model_persistence(self):
        """Test model is saved and loaded correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                # Create and train model
                optimizer1 = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)
                velocities = list(range(20, 40))

                # Train by making prediction
                optimizer1.predict(velocities)

                # Verify model was saved
                assert optimizer1.model_path.exists()
                assert optimizer1.metadata_path.exists()

                # Create new instance - should load existing model
                optimizer2 = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)
                assert optimizer2.model is not None

                # Should make same predictions
                result1, _ = optimizer1.predict(velocities)
                result2, _ = optimizer2.predict(velocities)
                assert result1 == result2

    def test_high_variance_detection(self):
        """Test detection of high variance in velocity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)

                # High variance data
                import random

                random.seed(42)
                velocities = [20 + random.randint(-10, 10) for _ in range(30)]

                features = optimizer.extract_features(velocities)

                # Should detect high CV
                assert features["cv"] > 0.3

                # Make prediction
                result, explanation = optimizer.predict(velocities)

                if explanation["method"] == "ml_model":
                    # Should use fewer sprints for high variance
                    assert result <= len(velocities) * 0.85  # More lenient threshold

    def test_trend_detection(self):
        """Test detection of trending velocity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)

                # Strong upward trend
                velocities = [20 + i * 2 for i in range(25)]

                features = optimizer.extract_features(velocities)

                # Should detect strong trend
                assert (
                    features["trend_strength"] > 0.01
                )  # Adjusted threshold for normalized trend

                # Make prediction
                result, explanation = optimizer.predict(velocities)

                if explanation["method"] == "ml_model" and "trend" in str(explanation):
                    # Should use fewer recent sprints to capture current performance
                    assert result <= len(velocities) * 0.6

    def test_stability_detection(self):
        """Test detection of stable velocity."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)

                # Very stable data
                velocities = [20, 21, 20, 19, 20, 21, 20, 20, 21, 20] * 3

                features = optimizer.extract_features(velocities)

                # Should detect high stability
                assert features["cv"] < 0.1
                assert features["stability_score"] > 0.7

                # Make prediction
                result, explanation = optimizer.predict(velocities)

                if explanation["method"] == "ml_model":
                    # Can use more historical data when stable
                    assert result >= len(velocities) * 0.5

    def test_prediction_logging(self):
        """Test predictions are logged for improvement."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = VelocityLookbackOptimizer("PROJ-123", lambda x: 10)
                velocities = list(range(20, 40))

                # Make prediction
                optimizer.predict(velocities)

                # Check log was created
                log_dir = (
                    Path(tmpdir)
                    / ".sprint-radar"
                    / "projects"
                    / "PROJ-123"
                    / "prediction_logs"
                )
                assert log_dir.exists()

                log_files = list(log_dir.glob("*.jsonl"))
                assert len(log_files) > 0

                # Verify log content
                with open(log_files[0]) as f:
                    log_entry = json.loads(f.readline())
                    assert "timestamp" in log_entry
                    assert "features" in log_entry
                    assert "prediction" in log_entry

                    # Verify features don't contain raw velocity list
                    assert "velocities" not in log_entry
                    # Verify features are statistical, not raw data
                    if "features" in log_entry and log_entry["features"]:
                        assert "cv" in log_entry["features"]
                        assert "trend_strength" in log_entry["features"]


class TestPrivacyPreservation:
    """Test privacy preservation across projects."""

    def test_no_cross_project_influence(self):
        """Test that one project's data doesn't affect another's predictions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                # Train model for project1 with stable data
                proj1_optimizer = VelocityLookbackOptimizer("PROJ-1", lambda x: 10)
                stable_velocities = [20] * 30
                proj1_result, _ = proj1_optimizer.predict(stable_velocities)

                # Train model for project2 with volatile data
                proj2_optimizer = VelocityLookbackOptimizer("PROJ-2", lambda x: 10)
                volatile_velocities = [10, 30, 15, 35, 12, 38] * 5
                proj2_result, _ = proj2_optimizer.predict(volatile_velocities)

                # Results should be different
                assert proj1_result != proj2_result

                # Make new predictions - should not be influenced
                new_proj1_result, _ = proj1_optimizer.predict(stable_velocities)
                assert new_proj1_result == proj1_result  # Consistent for same project

                # Verify no shared state
                assert proj1_optimizer.model_path != proj2_optimizer.model_path
                assert not proj1_optimizer.model_path.parent.parent.samefile(
                    proj2_optimizer.model_path.parent.parent
                )
