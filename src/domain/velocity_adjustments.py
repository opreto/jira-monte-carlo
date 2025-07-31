"""Domain models for velocity adjustments and team capacity changes"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple


class ProductivityCurve(Enum):
    """Types of productivity curves for team changes"""

    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    STEP = "step"


@dataclass
class VelocityAdjustment:
    """Represents a velocity change for a sprint range"""

    sprint_start: int
    sprint_end: Optional[int]  # None means "forever"
    factor: float  # 0.5 = 50% capacity, 1.5 = 150% capacity
    reason: Optional[str] = None

    def applies_to_sprint(self, sprint_number: int) -> bool:
        """Check if this adjustment applies to a given sprint"""
        if sprint_number < self.sprint_start:
            return False
        if self.sprint_end is None:  # Forever
            return True
        return sprint_number <= self.sprint_end

    def get_description(self) -> str:
        """Get human-readable description of the adjustment"""
        # Use relative descriptions instead of absolute sprint numbers
        if self.sprint_start == 1:
            sprint_range = "next sprint"
        elif self.sprint_start == 2:
            sprint_range = "sprint after next"
        else:
            sprint_range = f"sprint +{self.sprint_start - 1}"

        if self.sprint_end is None:
            sprint_range = f"from {sprint_range} onwards"
        elif self.sprint_end != self.sprint_start:
            if self.sprint_end == self.sprint_start + 1:
                sprint_range = f"next {self.sprint_end - self.sprint_start + 1} sprints"
            else:
                end_desc = f"sprint +{self.sprint_end - 1}" if self.sprint_end > 2 else "sprint after next"
                sprint_range = f"{sprint_range} through {end_desc}"

        percentage = int(self.factor * 100)
        change_desc = f"{percentage}% capacity"

        if self.reason:
            return f"{change_desc} for {sprint_range} ({self.reason})"
        return f"{change_desc} for {sprint_range}"


@dataclass
class TeamChange:
    """Represents a team size change"""

    sprint: int
    change: int  # +2 for additions, -2 for departures
    ramp_up_sprints: int = 3
    productivity_curve: ProductivityCurve = ProductivityCurve.LINEAR

    def get_productivity_factor(self, sprints_since_change: int) -> float:
        """Calculate productivity factor for new team members"""
        if self.change < 0:  # Team reduction
            return 1.0

        if sprints_since_change >= self.ramp_up_sprints:
            return 1.0

        if self.productivity_curve == ProductivityCurve.LINEAR:
            # Linear ramp from 0.25 to 1.0
            return 0.25 + (0.75 * sprints_since_change / self.ramp_up_sprints)
        elif self.productivity_curve == ProductivityCurve.EXPONENTIAL:
            # Exponential curve starting slow, accelerating
            progress = sprints_since_change / self.ramp_up_sprints
            return 0.25 + 0.75 * (progress**2)
        else:  # STEP
            # Step function: 25%, 50%, 75%, 100%
            steps = min(3, int(sprints_since_change * 4 / self.ramp_up_sprints))
            return 0.25 + (0.25 * steps)

    def get_description(self) -> str:
        """Get human-readable description of the team change"""
        # Use relative sprint descriptions
        if self.sprint == 1:
            sprint_desc = "next sprint"
            after_desc = "after this sprint"
        elif self.sprint == 2:
            sprint_desc = "sprint after next"
            after_desc = "after next sprint"
        else:
            sprint_desc = f"sprint +{self.sprint - 1}"
            after_desc = f"after sprint +{self.sprint - 1}"

        if self.change > 0:
            return (
                f"Adding {self.change} developer{'s' if self.change > 1 else ''} "
                f"starting {sprint_desc} (ramp-up: {self.ramp_up_sprints} sprints)"
            )
        else:
            return f"Removing {abs(self.change)} developer{'s' if abs(self.change) > 1 else ''} {after_desc}"


@dataclass
class VelocityScenario:
    """Collection of adjustments forming a scenario"""

    name: str
    adjustments: List[VelocityAdjustment]
    team_changes: List[TeamChange]

    def get_adjusted_velocity(self, sprint_number: int, base_velocity: float, team_size: int) -> Tuple[float, str]:
        """
        Calculate adjusted velocity for a given sprint
        Returns: (adjusted_velocity, reason_description)
        """
        adjusted_velocity = base_velocity
        reasons = []

        # Apply velocity adjustments
        for adjustment in self.adjustments:
            if adjustment.applies_to_sprint(sprint_number):
                adjusted_velocity *= adjustment.factor
                reasons.append(adjustment.get_description())

        # Apply team changes
        current_team_size = team_size
        for change in self.team_changes:
            if sprint_number >= change.sprint:
                # Apply team size change
                sprints_since = sprint_number - change.sprint

                if change.change > 0:
                    # Adding team members - apply ramp-up
                    productivity = change.get_productivity_factor(sprints_since)
                    # Calculate velocity impact
                    new_capacity = change.change * productivity
                    team_factor = (current_team_size + new_capacity) / current_team_size
                    adjusted_velocity *= team_factor

                    if sprints_since < change.ramp_up_sprints:
                        reasons.append(f"New team member(s) at {int(productivity * 100)}% productivity")
                    else:
                        reasons.append(f"Team scaled up by {change.change}")
                else:
                    # Removing team members
                    team_factor = (current_team_size + change.change) / current_team_size
                    adjusted_velocity *= team_factor
                    reasons.append(f"Team reduced by {abs(change.change)}")

                current_team_size += change.change

        reason_desc = "; ".join(reasons) if reasons else "No adjustments"
        return adjusted_velocity, reason_desc

    def get_summary(self) -> str:
        """Get a summary of all adjustments in this scenario"""
        summaries = []

        for adj in self.adjustments:
            summaries.append(adj.get_description())

        for change in self.team_changes:
            summaries.append(change.get_description())

        if not summaries:
            return "No adjustments applied"

        return " • ".join(summaries)


@dataclass
class ScenarioComparison:
    """Comparison between baseline and adjusted scenarios"""

    baseline_p50_sprints: int
    baseline_p85_sprints: int
    adjusted_p50_sprints: int
    adjusted_p85_sprints: int
    velocity_impact_percentage: float
    scenario_description: str

    def get_impact_summary(self) -> str:
        """Get a summary of the scenario's impact"""
        p50_diff = self.adjusted_p50_sprints - self.baseline_p50_sprints
        p85_diff = self.adjusted_p85_sprints - self.baseline_p85_sprints

        if p50_diff == 0 and p85_diff == 0:
            return "No significant impact on timeline"

        impact_parts = []
        if p50_diff > 0:
            impact_parts.append(f"{p50_diff} sprint{'s' if p50_diff != 1 else ''} delay at 50% confidence")
        elif p50_diff < 0:
            impact_parts.append(f"{abs(p50_diff)} sprint{'s' if abs(p50_diff) != 1 else ''} earlier at 50% confidence")

        if p85_diff > 0:
            impact_parts.append(f"{p85_diff} sprint{'s' if p85_diff != 1 else ''} delay at 85% confidence")
        elif p85_diff < 0:
            impact_parts.append(f"{abs(p85_diff)} sprint{'s' if abs(p85_diff) != 1 else ''} earlier at 85% confidence")

        return " and ".join(impact_parts)
