"""Domain models for ML decision tracking and explanations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class MLDecision:
    """Represents a single ML model decision with explanation."""

    model_name: str  # e.g., "LookbackOptimizer"
    decision_type: str  # e.g., "lookback_period", "productivity_curve"
    value: Any  # The actual decision value
    confidence: float  # 0.0 to 1.0
    primary_factor: str  # Main reason for decision
    factors: Dict[str, str] = field(default_factory=dict)  # Detailed factors
    method: str = "ml_model"  # "ml_model" or "fallback_heuristic"
    timestamp: datetime = field(default_factory=datetime.now)

    def get_summary(self) -> str:
        """Get a concise summary of this decision."""
        if self.method == "fallback_heuristic":
            return f"Using standard heuristic ({self.factors.get('reason', 'ML unavailable')})"

        confidence_pct = int(self.confidence * 100)
        return f"{self.primary_factor.replace('_', ' ').title()} (confidence: {confidence_pct}%)"

    def get_detailed_explanation(self) -> List[str]:
        """Get detailed explanation as bullet points."""
        explanation = []

        if self.method == "ml_model":
            explanation.append(f"Model: {self.model_name}")
            explanation.append(f"Decision: {self.decision_type} = {self.value}")
            explanation.append(f"Confidence: {int(self.confidence * 100)}%")
            explanation.append(
                f"Primary factor: {self.primary_factor.replace('_', ' ')}"
            )

            if self.factors:
                explanation.append("Contributing factors:")
                for factor, description in self.factors.items():
                    explanation.append(f"  • {description}")
        else:
            explanation.append("Using fallback heuristic")
            if "reason" in self.factors:
                explanation.append(f"Reason: {self.factors['reason']}")

        return explanation


@dataclass
class MLDecisionSet:
    """Collection of ML decisions made during a forecasting session."""

    decisions: List[MLDecision] = field(default_factory=list)
    project_id: Optional[str] = None
    session_id: Optional[str] = None

    def add_decision(self, decision: MLDecision) -> None:
        """Add a decision to the set."""
        self.decisions.append(decision)

    def get_decisions_by_type(self, decision_type: str) -> List[MLDecision]:
        """Get all decisions of a specific type."""
        return [d for d in self.decisions if d.decision_type == decision_type]

    def get_decisions_by_model(self, model_name: str) -> List[MLDecision]:
        """Get all decisions made by a specific model."""
        return [d for d in self.decisions if d.model_name == model_name]

    def has_ml_decisions(self) -> bool:
        """Check if any ML decisions were made (vs all fallback)."""
        return any(d.method == "ml_model" for d in self.decisions)

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all decisions."""
        summary = {
            "total_decisions": len(self.decisions),
            "ml_decisions": sum(1 for d in self.decisions if d.method == "ml_model"),
            "fallback_decisions": sum(
                1 for d in self.decisions if d.method == "fallback_heuristic"
            ),
            "models_used": list(
                set(d.model_name for d in self.decisions if d.method == "ml_model")
            ),
            "average_confidence": 0.0,
        }

        ml_decisions = [d for d in self.decisions if d.method == "ml_model"]
        if ml_decisions:
            summary["average_confidence"] = sum(
                d.confidence for d in ml_decisions
            ) / len(ml_decisions)

        return summary
