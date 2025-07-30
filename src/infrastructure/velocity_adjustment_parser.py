"""Parser for velocity adjustment CLI arguments"""

import logging
from typing import Optional

from ..domain.velocity_adjustments import (
    ProductivityCurve,
    TeamChange,
    VelocityAdjustment,
)

logger = logging.getLogger(__name__)


class VelocityAdjustmentParser:
    """Parse CLI arguments into domain objects"""

    def parse_velocity_change(self, value: str) -> VelocityAdjustment:
        """
        Parse format: 'sprint:N[-M|+],factor:F[,reason:R]'
        Examples:
        - sprint:3,factor:0.5,reason:vacation
        - sprint:5-7,factor:0.7
        - sprint:10+,factor:1.2,reason:new-process
        """
        try:
            # Parse key-value pairs
            parts = {}
            for part in value.split(","):
                if ":" in part:
                    key, val = part.split(":", 1)
                    parts[key.strip()] = val.strip()

            # Parse sprint range
            if "sprint" not in parts:
                raise ValueError("Missing 'sprint' specification")

            sprint_spec = parts["sprint"]
            sprint_start, sprint_end = self._parse_sprint_range(sprint_spec)

            # Parse factor
            if "factor" not in parts:
                raise ValueError("Missing 'factor' specification")

            try:
                factor = float(parts["factor"])
                if factor <= 0:
                    raise ValueError("Factor must be positive")
            except ValueError as e:
                raise ValueError(f"Invalid factor: {parts['factor']}") from e

            # Optional reason
            reason = parts.get("reason")

            return VelocityAdjustment(
                sprint_start=sprint_start,
                sprint_end=sprint_end,
                factor=factor,
                reason=reason,
            )

        except Exception as e:
            logger.error(f"Failed to parse velocity change '{value}': {e}")
            raise ValueError(
                f"Invalid velocity change format '{value}'. "
                f"Expected: 'sprint:N[-M|+],factor:F[,reason:R]'"
            ) from e

    def parse_team_change(self, value: str) -> TeamChange:
        """
        Parse format: 'sprint:N,change:±C[,ramp:R][,curve:TYPE]'
        Examples:
        - sprint:4,change:+1
        - sprint:6,change:+2,ramp:4
        - sprint:8,change:-2
        - sprint:10,change:+1,ramp:3,curve:exponential
        """
        try:
            # Parse key-value pairs
            parts = {}
            for part in value.split(","):
                if ":" in part:
                    key, val = part.split(":", 1)
                    parts[key.strip()] = val.strip()

            # Parse sprint
            if "sprint" not in parts:
                raise ValueError("Missing 'sprint' specification")

            try:
                sprint = int(parts["sprint"])
                if sprint < 1:
                    raise ValueError("Sprint must be positive")
            except ValueError as e:
                raise ValueError(f"Invalid sprint: {parts['sprint']}") from e

            # Parse change
            if "change" not in parts:
                raise ValueError("Missing 'change' specification")

            try:
                change_str = parts["change"]
                # Handle explicit + or - prefix
                if change_str.startswith("+"):
                    change = int(change_str[1:])
                elif change_str.startswith("-"):
                    change = -int(change_str[1:])
                else:
                    change = int(change_str)

                if change == 0:
                    raise ValueError("Change must be non-zero")
            except ValueError as e:
                raise ValueError(f"Invalid change: {parts['change']}") from e

            # Optional ramp-up (only for additions)
            ramp_up = 3  # default
            if "ramp" in parts:
                try:
                    ramp_up = int(parts["ramp"])
                    if ramp_up < 1:
                        raise ValueError("Ramp-up must be at least 1 sprint")
                except ValueError as e:
                    raise ValueError(f"Invalid ramp: {parts['ramp']}") from e

            # Optional productivity curve
            curve = ProductivityCurve.LINEAR
            if "curve" in parts:
                curve_str = parts["curve"].lower()
                if curve_str == "exponential":
                    curve = ProductivityCurve.EXPONENTIAL
                elif curve_str == "step":
                    curve = ProductivityCurve.STEP
                elif curve_str != "linear":
                    raise ValueError(f"Unknown curve type: {parts['curve']}")

            return TeamChange(
                sprint=sprint,
                change=change,
                ramp_up_sprints=ramp_up if change > 0 else 0,
                productivity_curve=curve,
            )

        except Exception as e:
            logger.error(f"Failed to parse team change '{value}': {e}")
            raise ValueError(
                f"Invalid team change format '{value}'. "
                f"Expected: 'sprint:N,change:±C[,ramp:R][,curve:TYPE]'"
            ) from e

    def _parse_sprint_range(self, sprint_spec: str) -> tuple[int, Optional[int]]:
        """Parse sprint range specification"""
        # Handle "N+" format (N onwards/forever)
        if sprint_spec.endswith("+"):
            sprint_start = int(sprint_spec[:-1])
            return sprint_start, None

        # Handle "N-M" format (range)
        if "-" in sprint_spec:
            parts = sprint_spec.split("-", 1)
            sprint_start = int(parts[0])
            sprint_end = int(parts[1])
            if sprint_end < sprint_start:
                raise ValueError(f"Invalid range: {sprint_spec}")
            return sprint_start, sprint_end

        # Handle single sprint
        sprint = int(sprint_spec)
        return sprint, sprint
