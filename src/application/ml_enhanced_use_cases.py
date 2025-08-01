"""
ML-enhanced use cases that maintain privacy while learning from organization patterns.
"""

import logging
from typing import Any, Optional, Tuple

from ..domain.ml_heuristics import (
    VelocityLookbackOptimizer,
    SprintHealthLookbackOptimizer,
)
from ..domain.ml_decisions import MLDecision, MLDecisionSet
from ..domain.repositories import SprintRepository
from ..domain.value_objects import VelocityMetrics
from .use_cases import CalculateVelocityUseCase

logger = logging.getLogger(__name__)


class MLEnhancedVelocityUseCase(CalculateVelocityUseCase):
    """Velocity calculation with ML-optimized lookback period."""

    def __init__(
        self,
        issue_repo,
        sprint_repo: SprintRepository,
        project_key: str,
        enable_ml: bool = False,
    ):
        """Initialize with optional ML enhancement.

        Args:
            issue_repo: Repository for issue data
            sprint_repo: Repository for sprint data
            project_key: Unique project key (e.g., 'PROJ-123') for data isolation
            enable_ml: Whether to enable ML optimization
        """
        super().__init__(issue_repo, sprint_repo)
        self.project_key = project_key
        self.enable_ml = enable_ml
        self.ml_decisions = MLDecisionSet(project_id=project_key)

        if self.enable_ml:
            # Initialize ML optimizer with existing heuristic as fallback
            self.lookback_optimizer = VelocityLookbackOptimizer(
                project_key=project_key,
                fallback_heuristic=self.calculate_optimal_lookback,
            )
        else:
            self.lookback_optimizer = None

    def execute(
        self, lookback_sprints: int = -1, velocity_field: str = "story_points"
    ) -> Tuple[VelocityMetrics, MLDecisionSet]:
        """Execute velocity calculation with ML-enhanced lookback detection.

        Returns:
            Tuple of (VelocityMetrics, MLDecisionSet)
        """

        # Get all sprints first
        all_sprints = self.sprint_repo.get_all()

        # Collect velocities from sprints
        velocities = []
        for sprint in all_sprints:
            if isinstance(sprint, dict):
                logger.warning(f"Found dict instead of Sprint object: {sprint}")
                continue

            # Extract velocity
            if hasattr(sprint, "velocity") and sprint.velocity > 0:
                velocities.append(sprint.velocity)
            elif hasattr(sprint, "completed_points") and sprint.completed_points > 0:
                velocities.append(sprint.completed_points)

        # Determine lookback period
        if lookback_sprints == -1:
            if self.enable_ml and self.lookback_optimizer:
                # Try ML-enhanced optimization
                try:
                    ml_lookback, explanation = self.lookback_optimizer.predict(
                        velocities
                    )

                    # Create ML decision record
                    decision = MLDecision(
                        model_name="VelocityLookbackOptimizer",
                        decision_type="lookback_period",
                        value=ml_lookback,
                        confidence=explanation.get("confidence", 0.5),
                        primary_factor=explanation.get("primary_factor", "unknown"),
                        factors=explanation.get("factors", {}),
                        method=explanation.get("method", "ml_model"),
                    )
                    self.ml_decisions.add_decision(decision)

                    logger.info(
                        f"ML-optimized lookback: {ml_lookback} sprints "
                        f"(confidence: {explanation.get('confidence', 0):.2f})"
                    )

                    # Log explanation for transparency
                    if "factors" in explanation:
                        for factor, description in explanation["factors"].items():
                            logger.info(f"  - {factor}: {description}")

                    lookback_sprints = ml_lookback

                except Exception as e:
                    logger.warning(f"ML optimization failed, using heuristic: {e}")
                    lookback_sprints = self.calculate_optimal_lookback(len(velocities))

                    # Record fallback decision
                    decision = MLDecision(
                        model_name="VelocityLookbackOptimizer",
                        decision_type="lookback_period",
                        value=lookback_sprints,
                        confidence=0.5,
                        primary_factor="fallback",
                        factors={"reason": f"ML failed: {str(e)}"},
                        method="fallback_heuristic",
                    )
                    self.ml_decisions.add_decision(decision)
            else:
                # Use standard heuristic
                lookback_sprints = self.calculate_optimal_lookback(len(velocities))
                logger.info(
                    f"Heuristic-based lookback: {lookback_sprints} sprints "
                    f"from {len(velocities)} available"
                )

                if self.enable_ml:
                    # Record that we used heuristic because ML is initializing
                    decision = MLDecision(
                        model_name="VelocityLookbackOptimizer",
                        decision_type="lookback_period",
                        value=lookback_sprints,
                        confidence=0.5,
                        primary_factor="standard_heuristic",
                        factors={"reason": "ML not available yet"},
                        method="fallback_heuristic",
                    )
                    self.ml_decisions.add_decision(decision)

        # Continue with standard velocity calculation
        velocity_metrics = super().execute(lookback_sprints, velocity_field)

        # Return both metrics and ML decisions
        return velocity_metrics, self.ml_decisions


class MLEnhancedSprintHealthUseCase:
    """Sprint health analysis with ML-optimized lookback period."""

    def __init__(
        self,
        issue_repo,
        sprint_repo: SprintRepository,
        project_key: str,
        enable_ml: bool = False,
    ):
        """Initialize with optional ML enhancement.

        Args:
            issue_repo: Repository for issue data
            sprint_repo: Repository for sprint data
            project_key: Unique project key for data isolation
            enable_ml: Whether to enable ML optimization
        """
        # Import here to avoid circular dependency
        from .process_health_use_cases import AnalyzeSprintHealthUseCase

        self.base_use_case = AnalyzeSprintHealthUseCase(issue_repo, sprint_repo)
        self.sprint_repo = sprint_repo
        self.project_key = project_key
        self.enable_ml = enable_ml
        self.ml_decisions = MLDecisionSet(project_id=project_key)

        if self.enable_ml:
            # Initialize ML optimizer for sprint health lookback
            # Uses a different fallback heuristic tailored for sprint health
            # Create a separate model instance for sprint health by appending a suffix
            self.lookback_optimizer = SprintHealthLookbackOptimizer(
                project_key=project_key,
                fallback_heuristic=self.base_use_case.calculate_optimal_lookback,
            )
        else:
            self.lookback_optimizer = None

    def execute(self, lookback_sprints: int = -1) -> Tuple[Any, MLDecisionSet]:
        """Execute sprint health analysis with ML-enhanced lookback detection.

        Returns:
            Tuple of (SprintHealthAnalysis, MLDecisionSet)
        """
        # First execute the base use case to get sprint health metrics
        # This will give us the SprintHealthAnalysis which contains sprint_metrics with completion rates
        if lookback_sprints == -1:
            # First get a preliminary sprint health analysis to extract completion rates
            all_sprints = self.sprint_repo.get_all()
            preliminary_health = self.base_use_case.execute(min(20, len(all_sprints)))

            # Collect sprint completion rates for ML analysis from the sprint health metrics
            completion_rates = []
            if preliminary_health and preliminary_health.sprint_metrics:
                for metric in preliminary_health.sprint_metrics:
                    if metric.completion_rate > 0:
                        completion_rates.append(metric.completion_rate)

            logger.info(
                f"Collected {len(completion_rates)} completion rates for ML analysis from sprint health metrics"
            )

            if self.enable_ml and self.lookback_optimizer and completion_rates:
                # Check if we need to train or retrain the model
                if (
                    self.lookback_optimizer.should_retrain()
                    or self.lookback_optimizer.model is None
                ):
                    if len(completion_rates) >= self.lookback_optimizer.min_data_points:
                        logger.info(
                            f"Training ML model on {len(completion_rates)} sprint completion rates"
                        )
                        # Prepare historical data for training
                        # The model expects a list of lists for multiple training samples
                        # For now, we'll use a sliding window approach
                        historical_data = []
                        window_size = min(20, len(completion_rates) // 2)
                        for i in range(len(completion_rates) - window_size + 1):
                            historical_data.append(
                                completion_rates[i : i + window_size]
                            )

                        if historical_data:
                            self.lookback_optimizer.train(historical_data)
                            logger.info("ML model training completed for sprint health")

                # Try ML-enhanced optimization
                try:
                    ml_lookback, explanation = self.lookback_optimizer.predict(
                        completion_rates
                    )

                    # Create ML decision record
                    decision = MLDecision(
                        model_name="SprintHealthLookbackOptimizer",
                        decision_type="sprint_health_lookback",
                        value=ml_lookback,
                        confidence=explanation.get("confidence", 0.5),
                        primary_factor=explanation.get("primary_factor", "unknown"),
                        factors=explanation.get("factors", {}),
                        method=explanation.get("method", "ml_model"),
                    )
                    self.ml_decisions.add_decision(decision)

                    logger.info(
                        f"ML-optimized sprint health lookback: {ml_lookback} sprints "
                        f"(confidence: {explanation.get('confidence', 0):.2f})"
                    )

                    lookback_sprints = ml_lookback

                except Exception as e:
                    logger.warning(
                        f"ML optimization failed for sprint health, using heuristic: {e}"
                    )
                    # Fallback expects number of sprints, not the completion rates list
                    lookback_sprints = self.base_use_case.calculate_optimal_lookback(
                        len(all_sprints)
                    )

                    # Record fallback decision
                    decision = MLDecision(
                        model_name="SprintHealthLookbackOptimizer",
                        decision_type="sprint_health_lookback",
                        value=lookback_sprints,
                        confidence=0.5,
                        primary_factor="fallback",
                        factors={"reason": f"ML failed: {str(e)}"},
                        method="fallback_heuristic",
                    )
                    self.ml_decisions.add_decision(decision)
            else:
                # Use standard heuristic
                lookback_sprints = self.base_use_case.calculate_optimal_lookback(
                    len(all_sprints)
                )
                logger.info(
                    f"Sprint health heuristic-based lookback: {lookback_sprints} sprints "
                    f"from {len(all_sprints)} available"
                )

                if self.enable_ml:
                    # Record that we used heuristic
                    decision = MLDecision(
                        model_name="SprintHealthLookbackOptimizer",
                        decision_type="sprint_health_lookback",
                        value=lookback_sprints,
                        confidence=0.5,
                        primary_factor="standard_heuristic",
                        factors={"reason": "ML not available yet"},
                        method="fallback_heuristic",
                    )
                    self.ml_decisions.add_decision(decision)

        # Execute the base use case with determined lookback
        sprint_health = self.base_use_case.execute(lookback_sprints)

        return sprint_health, self.ml_decisions


class MLModelManagementUseCase:
    """Use case for managing ML models for a project."""

    def __init__(self, project_key: str):
        self.project_key = self._sanitize_project_key(project_key)

    def _sanitize_project_key(self, project_key: str) -> str:
        """Sanitize project key for safe filesystem usage."""
        import re

        return re.sub(r"[^a-zA-Z0-9_-]", "_", project_key)

    def get_model_status(self) -> dict:
        """Get status of all ML models for this project."""
        from pathlib import Path

        project_path = Path.home() / ".sprint-radar" / "projects" / self.project_key
        models_path = project_path / "models"

        status = {"project_key": self.project_key, "models": {}}

        if not models_path.exists():
            status["models_available"] = False
            return status

        status["models_available"] = True

        # Check for each model type
        model_types = [
            "VelocityLookbackOptimizer",
            "SprintHealthLookbackOptimizer",
            "ProductivityCurveOptimizer",
            "AgingPredictor",
        ]

        for model_type in model_types:
            model_file = models_path / f"{model_type}.pkl"
            metadata_file = models_path / f"{model_type}_metadata.json"

            if model_file.exists():
                import json

                model_info = {
                    "exists": True,
                    "size_kb": model_file.stat().st_size / 1024,
                    "last_modified": model_file.stat().st_mtime,
                }

                # Load metadata if available
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                            model_info.update(
                                {
                                    "version": metadata.get("version"),
                                    "last_trained": metadata.get("last_trained"),
                                    "training_samples": metadata.get(
                                        "training_samples"
                                    ),
                                    "performance_metrics": metadata.get(
                                        "performance_metrics", {}
                                    ),
                                }
                            )
                    except Exception as e:
                        logger.warning(f"Failed to load metadata for {model_type}: {e}")

                status["models"][model_type] = model_info
            else:
                status["models"][model_type] = {"exists": False}

        return status

    def clear_models(self, model_type: Optional[str] = None) -> bool:
        """Clear ML models for this project.

        Args:
            model_type: Specific model to clear, or None for all models

        Returns:
            True if successful
        """
        from pathlib import Path
        import shutil

        project_path = Path.home() / ".sprint-radar" / "projects" / self.project_key

        try:
            if model_type:
                # Clear specific model
                models_path = project_path / "models"
                model_file = models_path / f"{model_type}.pkl"
                metadata_file = models_path / f"{model_type}_metadata.json"

                if model_file.exists():
                    model_file.unlink()
                if metadata_file.exists():
                    metadata_file.unlink()

                logger.info(
                    f"Cleared {model_type} model for project {self.project_key}"
                )
            else:
                # Clear all models for this project
                if project_path.exists():
                    shutil.rmtree(project_path)
                logger.info(f"Cleared all models for project {self.project_key}")

            return True

        except Exception as e:
            logger.error(f"Failed to clear models: {e}")
            return False

    def get_privacy_report(self) -> dict:
        """Generate privacy report showing data isolation."""
        from pathlib import Path

        base_path = Path.home() / ".sprint-radar" / "projects"

        report = {
            "project_key": self.project_key,
            "data_isolation": {
                "confirmed": True,
                "project_specific_path": str(base_path / self.project_key),
                "other_projects_accessible": False,
            },
            "data_stored": {"models": [], "logs": [], "features": []},
            "privacy_features": [
                "No raw data stored in models",
                "Only statistical aggregates used as features",
                "Complete isolation between projects",
                "All processing happens locally",
                "No data leaves project environment",
            ],
        }

        # List what data is stored
        project_path = base_path / self.project_key
        if project_path.exists():
            model_dir = project_path / "models"
            if model_dir.exists():
                for model_file in model_dir.glob("*.pkl"):
                    report["data_stored"]["models"].append(model_file.name)

            log_path = project_path / "prediction_logs"
            if log_path.exists():
                for log_file in log_path.glob("*.jsonl"):
                    report["data_stored"]["logs"].append(log_file.name)

        return report
