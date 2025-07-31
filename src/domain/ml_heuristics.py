"""
Privacy-preserving machine learning heuristics for Sprint Radar.

This module provides ML-enhanced heuristics that learn from organization-specific
patterns while maintaining complete data isolation between organizations.
"""

import json
import logging
import pickle
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class MLHeuristic(ABC):
    """Base class for all ML-enhanced heuristics with privacy preservation."""

    def __init__(self, project_key: str, fallback_heuristic, min_data_points: int = 10):
        """Initialize ML heuristic with project isolation.

        Args:
            project_key: Unique project identifier for data isolation
            fallback_heuristic: Function to use when ML is unavailable
            min_data_points: Minimum data points needed for ML predictions
        """
        self.project_key = self._sanitize_project_key(project_key)
        self.fallback = fallback_heuristic
        self.min_data_points = min_data_points
        self.model_path = self._get_model_path()
        self.metadata_path = self._get_metadata_path()
        self.model = self._load_model()
        self.metadata = self._load_metadata()

    def _sanitize_project_key(self, project_key: str) -> str:
        """Sanitize project key for safe filesystem usage."""
        # Replace any characters that might cause filesystem issues
        import re

        return re.sub(r"[^a-zA-Z0-9_-]", "_", project_key)

    def _get_project_base_path(self) -> Path:
        """Get project-specific base directory."""
        base = Path.home() / ".sprint-radar" / "projects" / self.project_key
        base.mkdir(parents=True, exist_ok=True)
        return base

    def _get_model_path(self) -> Path:
        """Get path for model storage (isolated per project)."""
        models_dir = self._get_project_base_path() / "models"
        models_dir.mkdir(exist_ok=True)

        # Check for legacy model name first (backward compatibility)
        if self.__class__.__name__ == "VelocityLookbackOptimizer":
            legacy_path = models_dir / "LookbackOptimizer.pkl"
            if legacy_path.exists():
                return legacy_path

        return models_dir / f"{self.__class__.__name__}.pkl"

    def _get_metadata_path(self) -> Path:
        """Get path for model metadata."""
        models_dir = self._get_project_base_path() / "models"

        # Check for legacy metadata name first (backward compatibility)
        if self.__class__.__name__ == "VelocityLookbackOptimizer":
            legacy_path = models_dir / "LookbackOptimizer_metadata.json"
            if legacy_path.exists():
                return legacy_path

        return models_dir / f"{self.__class__.__name__}_metadata.json"

    def _load_model(self) -> Optional[Any]:
        """Load existing model if available."""
        if self.model_path.exists():
            try:
                with open(self.model_path, "rb") as f:
                    model = pickle.load(f)
                logger.info(f"Loaded existing model for project {self.project_key}")
                return model
            except Exception as e:
                logger.warning(f"Failed to load model: {e}")
        return None

    def _load_metadata(self) -> Dict[str, Any]:
        """Load model metadata."""
        if self.metadata_path.exists():
            try:
                with open(self.metadata_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")

        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_trained": None,
            "training_samples": 0,
            "performance_metrics": {},
        }

    def _save_model(self) -> None:
        """Save model to disk."""
        try:
            with open(self.model_path, "wb") as f:
                pickle.dump(self.model, f)
            logger.info(f"Saved model for project {self.project_key}")
        except Exception as e:
            logger.error(f"Failed to save model: {e}")

    def _save_metadata(self) -> None:
        """Save model metadata."""
        try:
            with open(self.metadata_path, "w") as f:
                json.dump(self.metadata, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")

    @abstractmethod
    def extract_features(self, data: Any) -> Dict[str, float]:
        """Extract privacy-preserving features from data.

        Features should be statistical aggregates that don't reveal
        specific values or allow reverse engineering of raw data.
        """
        pass

    @abstractmethod
    def train(self, historical_data: Any) -> None:
        """Train the model on historical data."""
        pass

    @abstractmethod
    def explain_prediction(
        self, features: Dict[str, float], prediction: Any
    ) -> Dict[str, Any]:
        """Generate human-readable explanation for prediction."""
        pass

    def has_sufficient_data(self, data: Any) -> bool:
        """Check if we have enough data for ML predictions."""
        return len(data) >= self.min_data_points

    def should_retrain(self) -> bool:
        """Determine if model should be retrained."""
        if not self.metadata.get("last_trained"):
            return True

        last_trained = datetime.fromisoformat(self.metadata["last_trained"])
        days_since_training = (datetime.now() - last_trained).days

        # Retrain monthly or if explicitly requested
        return days_since_training > 30

    def predict(
        self, data: Any, allow_fallback: bool = True
    ) -> Tuple[Any, Dict[str, Any]]:
        """Make prediction with explanation and privacy preservation.

        Args:
            data: Input data for prediction
            allow_fallback: Whether to use fallback heuristic if ML fails

        Returns:
            Tuple of (prediction, explanation)
        """
        # Check if we have sufficient data
        if not self.has_sufficient_data(data):
            if allow_fallback:
                # For sprint health, fallback expects number of sprints, not the data itself
                if hasattr(self, "_num_sprints"):
                    result = self.fallback(self._num_sprints)
                else:
                    result = self.fallback(
                        len(data) if isinstance(data, list) else data
                    )
                explanation = {
                    "method": "fallback_heuristic",
                    "reason": f"Insufficient data (need {self.min_data_points} points)",
                    "confidence": 0.5,
                }
                return result, explanation
            else:
                raise ValueError("Insufficient data for ML prediction")

        # Try ML prediction
        try:
            features = self.extract_features(data)

            if self.model is None:
                # First time - train the model
                self.train(data)

            if self.model is not None:
                prediction = self._make_prediction(features)
                explanation = self.explain_prediction(features, prediction)
                explanation["method"] = "ml_model"

                # Log prediction locally for future improvement
                self._log_prediction(features, prediction)

                return prediction, explanation

        except Exception as e:
            logger.warning(f"ML prediction failed: {e}")

        # Fallback to heuristic
        if allow_fallback:
            # For sprint health, fallback expects number of sprints, not the data itself
            if hasattr(self, "_num_sprints"):
                result = self.fallback(self._num_sprints)
            else:
                result = self.fallback(len(data) if isinstance(data, list) else data)
            explanation = {
                "method": "fallback_heuristic",
                "reason": "ML prediction failed",
                "confidence": 0.5,
            }
            return result, explanation
        else:
            raise

    @abstractmethod
    def _make_prediction(self, features: Dict[str, float]) -> Any:
        """Make actual prediction using the model."""
        pass

    def _log_prediction(self, features: Dict[str, float], prediction: Any) -> None:
        """Log prediction locally for model improvement."""
        # Store in project-specific location
        log_dir = self._get_project_base_path() / "prediction_logs"
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"{self.__class__.__name__}_{datetime.now():%Y%m}.jsonl"

        try:
            with open(log_file, "a") as f:
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "features": features,
                    "prediction": prediction,
                }
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to log prediction: {e}")


class VelocityLookbackOptimizer(MLHeuristic):
    """ML-enhanced optimizer for velocity-based sprint lookback period."""

    def __init__(self, project_key: str, fallback_heuristic):
        super().__init__(project_key, fallback_heuristic, min_data_points=20)

    def extract_features(self, velocity_history: List[float]) -> Dict[str, float]:
        """Extract privacy-preserving features from velocity history."""
        velocities = np.array(velocity_history)

        # Only statistical features, no raw values
        features = {
            "sprint_count": len(velocities),
            "cv": np.std(velocities) / np.mean(velocities)
            if np.mean(velocities) > 0
            else 0,
            "trend_strength": self._calculate_trend_strength(velocities),
            "autocorrelation": self._calculate_autocorrelation(velocities),
            "stability_score": self._calculate_stability_score(velocities),
            "recency_weight": self._calculate_recency_weight(velocities),
        }

        return features

    def _calculate_trend_strength(self, velocities: np.ndarray) -> float:
        """Calculate trend strength (normalized slope)."""
        if len(velocities) < 2:
            return 0.0

        x = np.arange(len(velocities))
        slope, _ = np.polyfit(x, velocities, 1)

        # Normalize by mean to make it scale-independent
        return abs(slope) / np.mean(velocities) if np.mean(velocities) > 0 else 0

    def _calculate_autocorrelation(self, velocities: np.ndarray) -> float:
        """Calculate lag-1 autocorrelation."""
        if len(velocities) < 2:
            return 0.0

        return np.corrcoef(velocities[:-1], velocities[1:])[0, 1]

    def _calculate_stability_score(self, velocities: np.ndarray) -> float:
        """Calculate stability score based on rolling variance."""
        if len(velocities) < 6:
            return 1.0

        window_size = min(6, len(velocities) // 2)
        rolling_cvs = []

        for i in range(len(velocities) - window_size + 1):
            window = velocities[i : i + window_size]
            cv = np.std(window) / np.mean(window) if np.mean(window) > 0 else 0
            rolling_cvs.append(cv)

        # Lower variance in CV = more stable
        return 1 / (1 + np.std(rolling_cvs))

    def _calculate_recency_weight(self, velocities: np.ndarray) -> float:
        """Calculate how much recent data differs from older data."""
        if len(velocities) < 6:
            return 0.5

        mid_point = len(velocities) // 2
        old_mean = np.mean(velocities[:mid_point])
        new_mean = np.mean(velocities[mid_point:])

        # Normalized difference
        return abs(new_mean - old_mean) / old_mean if old_mean > 0 else 0

    def train(self, historical_data: List[List[float]]) -> None:
        """Train a simple decision tree for lookback optimization."""
        # For demo purposes, using a rule-based model
        # In production, would use sklearn DecisionTreeRegressor

        # Simple rules learned from features
        self.model = {
            "type": "rule_based",
            "rules": [
                {
                    "condition": "high_variance",
                    "cv_threshold": 0.4,
                    "lookback_factor": 0.5,
                },
                {
                    "condition": "high_trend",
                    "trend_threshold": 0.1,
                    "lookback_factor": 0.6,
                },
                {
                    "condition": "stable",
                    "stability_threshold": 0.8,
                    "lookback_factor": 0.8,
                },
                {"condition": "default", "lookback_factor": 0.7},
            ],
        }

        self.metadata["last_trained"] = datetime.now().isoformat()
        self.metadata["training_samples"] = len(historical_data)

        self._save_model()
        self._save_metadata()

    def _make_prediction(self, features: Dict[str, float]) -> int:
        """Apply rules to make prediction."""
        sprint_count = features["sprint_count"]

        # Apply rules in order
        for rule in self.model["rules"]:
            if (
                rule["condition"] == "high_variance"
                and features["cv"] > rule["cv_threshold"]
            ):
                return int(sprint_count * rule["lookback_factor"])
            elif (
                rule["condition"] == "high_trend"
                and features["trend_strength"] > rule["trend_threshold"]
            ):
                return int(sprint_count * rule["lookback_factor"])
            elif (
                rule["condition"] == "stable"
                and features["stability_score"] > rule["stability_threshold"]
            ):
                return int(sprint_count * rule["lookback_factor"])
            elif rule["condition"] == "default":
                return int(sprint_count * rule["lookback_factor"])

        # Should never reach here
        return self.fallback(features["sprint_count"])

    def explain_prediction(
        self, features: Dict[str, float], prediction: int
    ) -> Dict[str, Any]:
        """Generate explanation for the prediction."""
        explanation = {"lookback_sprints": prediction, "confidence": 0.0, "factors": {}}

        # Determine which rule was applied
        for rule in self.model["rules"]:
            if rule["condition"] == "high_variance" and features["cv"] > rule.get(
                "cv_threshold", 0
            ):
                explanation["primary_factor"] = "high_variance"
                explanation["factors"]["variance"] = (
                    f"CV={features['cv']:.2f} indicates high variability"
                )
                explanation["confidence"] = 0.75
                break
            elif rule["condition"] == "high_trend" and features[
                "trend_strength"
            ] > rule.get("trend_threshold", 0):
                explanation["primary_factor"] = "trending_velocity"
                explanation["factors"]["trend"] = (
                    f"Strong trend detected (strength={features['trend_strength']:.2f})"
                )
                explanation["confidence"] = 0.80
                break
            elif rule["condition"] == "stable" and features[
                "stability_score"
            ] > rule.get("stability_threshold", 0):
                explanation["primary_factor"] = "stable_velocity"
                explanation["factors"]["stability"] = (
                    f"Stable velocity pattern (score={features['stability_score']:.2f})"
                )
                explanation["confidence"] = 0.85
                break
            else:
                explanation["primary_factor"] = "default"
                explanation["confidence"] = 0.60

        # Add supporting factors
        if features["recency_weight"] > 0.2:
            explanation["factors"]["recency"] = (
                "Recent velocity differs from historical pattern"
            )

        if features["autocorrelation"] > 0.7:
            explanation["factors"]["correlation"] = (
                "Velocities show strong sprint-to-sprint correlation"
            )

        return explanation


class SprintHealthLookbackOptimizer(VelocityLookbackOptimizer):
    """ML-enhanced optimizer specifically for sprint health metrics."""

    def __init__(self, project_key: str, fallback_heuristic):
        # Call parent init but override the model filename
        super().__init__(project_key, fallback_heuristic)
        # This will use a different model file name
        # Store the number of sprints for fallback use
        self._num_sprints = 0

    def _get_model_path(self) -> Path:
        """Get path for model storage (isolated per project and metric type)."""
        models_dir = self._get_project_base_path() / "models"
        models_dir.mkdir(exist_ok=True)
        # Use a different filename for sprint health models
        return models_dir / "SprintHealthLookbackOptimizer.pkl"

    def _get_metadata_path(self) -> Path:
        """Get path for model metadata."""
        return (
            self._get_project_base_path()
            / "models"
            / "SprintHealthLookbackOptimizer_metadata.json"
        )

    def extract_features(self, completion_rates: List[float]) -> Dict[str, float]:
        """Extract features specific to sprint completion rates."""
        rates = np.array(completion_rates)

        # Features tailored for completion rate analysis
        features = {
            "sprint_count": len(rates),
            "mean_completion": np.mean(rates),
            "cv": np.std(rates) / np.mean(rates) if np.mean(rates) > 0 else 0,
            "below_target_rate": np.sum(rates < 0.8)
            / len(rates),  # % of sprints below 80% target
            "trend_strength": self._calculate_trend_strength(rates),
            "consistency_score": self._calculate_consistency_score(rates),
            "recent_performance": np.mean(rates[-3:])
            if len(rates) >= 3
            else np.mean(rates),
        }

        return features

    def _calculate_consistency_score(self, rates: np.ndarray) -> float:
        """Calculate how consistent the team is at meeting commitments."""
        if len(rates) < 2:
            return 1.0

        # Lower variance in completion rates = more consistent
        return 1 / (1 + np.std(rates))

    def predict(
        self, completion_rates: List[float], allow_fallback: bool = True
    ) -> Tuple[int, Dict[str, Any]]:
        """Override predict to handle sprint health specific data.

        Args:
            completion_rates: List of completion rates from sprints
            allow_fallback: Whether to use fallback heuristic if ML fails

        Returns:
            Tuple of (lookback_sprints, explanation)
        """
        # Store the number of sprints for fallback use
        self._num_sprints = len(completion_rates)

        # Call parent predict with completion rates
        return super().predict(completion_rates, allow_fallback)

    def has_sufficient_data(self, data: Any) -> bool:
        """Check if we have enough completion rate data."""
        if isinstance(data, list):
            self._num_sprints = len(data)
            return len(data) >= self.min_data_points
        return False

    def _make_prediction(self, features: Dict[str, float]) -> int:
        """Apply rules to make prediction for sprint health."""
        # Use the stored number of sprints (total available sprints)
        # The features contain sprint_count which is the number of completion rates we have
        # For sprint health, we may want to look at more sprints if performance is inconsistent
        num_available_sprints = max(self._num_sprints, features["sprint_count"])

        # Apply rules specific to sprint health
        for rule in self.model["rules"]:
            if (
                rule["condition"] == "high_variance"
                and features["cv"] > rule["cv_threshold"]
            ):
                # High variance in completion rates - need more data
                return min(int(num_available_sprints * 0.8), num_available_sprints)
            elif (
                rule["condition"] == "high_trend"
                and features["below_target_rate"] > 0.3
            ):
                # Many sprints below target - look at more history
                return min(int(num_available_sprints * 0.7), num_available_sprints)
            elif (
                rule["condition"] == "stable"
                and features["consistency_score"] > rule["stability_threshold"]
            ):
                # Stable completion rates - can use fewer sprints
                return min(int(num_available_sprints * 0.5), num_available_sprints)
            elif rule["condition"] == "default":
                return min(int(num_available_sprints * 0.6), num_available_sprints)

        # Fallback to heuristic if no rules match
        return self.fallback(self._num_sprints)

    def explain_prediction(
        self, features: Dict[str, float], prediction: int
    ) -> Dict[str, Any]:
        """Generate explanation for sprint health lookback prediction."""
        explanation = {"lookback_sprints": prediction, "confidence": 0.0, "factors": {}}

        # Determine which rule was applied based on sprint health metrics
        if features["below_target_rate"] > 0.3:
            explanation["primary_factor"] = "inconsistent_delivery"
            explanation["factors"]["delivery"] = (
                f"{features['below_target_rate'] * 100:.0f}% of sprints below 80% target"
            )
            explanation["confidence"] = 0.70
        elif features["cv"] > 0.3:
            explanation["primary_factor"] = "variable_completion"
            explanation["factors"]["variance"] = (
                f"CV={features['cv']:.2f} indicates high variability in completion rates"
            )
            explanation["confidence"] = 0.75
        elif features["consistency_score"] > 0.8:
            explanation["primary_factor"] = "consistent_delivery"
            explanation["factors"]["consistency"] = (
                f"Consistent completion pattern (score={features['consistency_score']:.2f})"
            )
            explanation["confidence"] = 0.85
        else:
            explanation["primary_factor"] = "moderate_performance"
            explanation["confidence"] = 0.65

        # Add supporting factors
        if features["mean_completion"] < 0.8:
            explanation["factors"]["average"] = (
                f"Average completion {features['mean_completion'] * 100:.0f}% is below target"
            )

        if abs(features["recent_performance"] - features["mean_completion"]) > 0.1:
            if features["recent_performance"] > features["mean_completion"]:
                explanation["factors"]["trend"] = "Recent performance improving"
            else:
                explanation["factors"]["trend"] = "Recent performance declining"

        return explanation
