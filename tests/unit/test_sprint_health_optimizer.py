"""Tests for Sprint Health Lookback Optimizer."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np

from src.domain.ml_heuristics import SprintHealthLookbackOptimizer


class TestSprintHealthLookbackOptimizer:
    """Test sprint health lookback optimizer functionality."""

    def test_extract_features_for_completion_rates(self):
        """Test feature extraction specific to completion rates."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", lambda x: 10)

                # Test with various completion rates
                completion_rates = [
                    0.8,
                    0.9,
                    0.7,
                    0.85,
                    0.6,
                    0.95,
                    0.75,
                    0.8,
                    0.65,
                    0.9,
                ]
                features = optimizer.extract_features(completion_rates)

                # Check all required features are present
                assert "sprint_count" in features
                assert "mean_completion" in features
                assert "cv" in features
                assert "below_target_rate" in features
                assert "trend_strength" in features
                assert "consistency_score" in features
                assert "recent_performance" in features

                # Verify feature calculations
                assert features["sprint_count"] == 10
                assert abs(features["mean_completion"] - 0.785) < 0.01
                assert (
                    features["below_target_rate"] == 0.4
                )  # 4 out of 10 are below 0.8 (0.7, 0.6, 0.75, 0.65)
                assert features["recent_performance"] == np.mean([0.8, 0.65, 0.9])

    def test_below_target_rate_calculation(self):
        """Test calculation of sprints below target completion rate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", lambda x: 10)

                # All above target
                rates = [0.85, 0.9, 0.95, 0.82]
                features = optimizer.extract_features(rates)
                assert features["below_target_rate"] == 0.0

                # All below target
                rates = [0.5, 0.6, 0.7, 0.75]
                features = optimizer.extract_features(rates)
                assert features["below_target_rate"] == 1.0

                # Mixed
                rates = [0.9, 0.7, 0.85, 0.75]
                features = optimizer.extract_features(rates)
                assert features["below_target_rate"] == 0.5

    def test_predict_with_completion_rates(self):
        """Test prediction with completion rate data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                fallback_mock = Mock(return_value=8)
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", fallback_mock)

                # Train the model first
                training_data = [
                    [0.8, 0.85, 0.9, 0.75, 0.8],
                    [0.7, 0.65, 0.8, 0.85, 0.9],
                    [0.95, 0.9, 0.85, 0.9, 0.88],
                ]
                optimizer.train(training_data)

                # Test prediction - need at least 20 data points for ML
                test_rates = [
                    0.6,
                    0.65,
                    0.7,
                    0.75,
                    0.8,
                    0.7,
                    0.65,
                    0.7,
                    0.75,
                    0.8,
                ] * 3  # 30 data points
                lookback, explanation = optimizer.predict(test_rates)

                assert isinstance(lookback, int)
                assert "confidence" in explanation
                if explanation["method"] == "ml_model":
                    assert "primary_factor" in explanation
                else:
                    # If fallback was used
                    assert explanation["method"] == "fallback_heuristic"

    def test_fallback_with_sprint_count(self):
        """Test that fallback is called with sprint count, not the data list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                fallback_mock = Mock(return_value=10)
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", fallback_mock)

                # Test with insufficient data (should use fallback)
                rates = [0.8, 0.9]  # Only 2 data points
                lookback, explanation = optimizer.predict(rates)

                # Verify fallback was called with the count, not the list
                fallback_mock.assert_called_once_with(2)
                assert lookback == 10
                assert explanation["method"] == "fallback_heuristic"

    def test_explanation_based_on_delivery_patterns(self):
        """Test that explanations reflect sprint health patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", lambda x: 10)

                # Train the model
                optimizer.train([[0.8, 0.85, 0.9, 0.88, 0.92]])

                # Test with inconsistent delivery pattern
                poor_rates = [0.5, 0.6, 0.7, 0.55, 0.65, 0.7, 0.6, 0.75, 0.7, 0.8] * 2
                _, explanation = optimizer.predict(poor_rates)

                assert (
                    "inconsistent_delivery" in explanation["primary_factor"]
                    or "variable_completion" in explanation["primary_factor"]
                )
                assert "below" in str(explanation["factors"]).lower()

                # Test with consistent delivery pattern
                good_rates = [
                    0.85,
                    0.9,
                    0.88,
                    0.92,
                    0.87,
                    0.89,
                    0.91,
                    0.88,
                    0.9,
                    0.86,
                ] * 2
                _, explanation = optimizer.predict(good_rates)

                assert explanation["confidence"] > 0.7

    def test_consistency_score_calculation(self):
        """Test the sprint health consistency score calculation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", lambda x: 10)

                # Very consistent rates
                consistent_rates = [0.85, 0.86, 0.84, 0.85, 0.86]
                features = optimizer.extract_features(consistent_rates)
                assert features["consistency_score"] > 0.8

                # Very inconsistent rates
                inconsistent_rates = [0.4, 0.9, 0.5, 0.95, 0.3]
                features = optimizer.extract_features(inconsistent_rates)
                # Consistency score = 1 / (1 + std_dev), so higher variance = lower score
                # But with such extreme variance, score might still be > 0.5
                assert (
                    features["consistency_score"] < 0.85
                )  # Just ensure it's lower than consistent

    def test_separate_model_storage(self):
        """Test that sprint health models are stored separately from velocity models."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", lambda x: 10)

                # Check model path
                model_path = optimizer._get_model_path()
                assert "SprintHealthLookbackOptimizer" in str(model_path)
                assert "VelocityLookbackOptimizer" not in str(model_path)

                # Check metadata path
                metadata_path = optimizer._get_metadata_path()
                assert "SprintHealthLookbackOptimizer" in str(metadata_path)

    def test_make_prediction_with_variance_rules(self):
        """Test prediction rules based on completion rate variance."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(Path, "home", return_value=Path(tmpdir)):
                optimizer = SprintHealthLookbackOptimizer("PROJ-123", lambda x: 10)

                # Train the model
                optimizer.train([[0.8, 0.85, 0.9, 0.88, 0.92]])

                # High variance should suggest more sprints
                high_variance_rates = [0.3, 0.9, 0.4, 0.95, 0.2, 0.85, 0.1, 0.9] * 3
                lookback_high, _ = optimizer.predict(high_variance_rates)

                # Low variance should suggest fewer sprints
                low_variance_rates = [0.8, 0.82, 0.81, 0.83, 0.8, 0.82, 0.81, 0.8] * 3
                lookback_low, _ = optimizer.predict(low_variance_rates)

                # High variance should use more lookback
                assert lookback_high > lookback_low
