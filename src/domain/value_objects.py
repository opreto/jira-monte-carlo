from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass(frozen=True)
class FieldMapping:
    key_field: str = "Issue key"
    summary_field: str = "Summary"
    issue_type_field: str = "Issue Type"
    status_field: str = "Status"
    created_field: str = "Created"
    updated_field: str = "Updated"
    resolved_field: str = "Resolved"
    story_points_field: Optional[str] = "Custom field (Story Points)"
    time_estimate_field: Optional[str] = "Original estimate"
    time_spent_field: Optional[str] = "Time Spent"
    assignee_field: str = "Assignee"
    reporter_field: str = "Reporter"
    labels_field: str = "Labels"
    sprint_field: Optional[str] = "Sprint"

    def to_dict(self) -> Dict[str, str]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass(frozen=True)
class VelocityMetrics:
    average: float
    median: float
    std_dev: float
    min_value: float
    max_value: float
    trend: float  # Positive for increasing, negative for decreasing


@dataclass(frozen=True)
class DateRange:
    start: datetime
    end: datetime

    @property
    def days(self) -> int:
        return (self.end - self.start).days

    def contains(self, date: datetime) -> bool:
        # Handle timezone-aware vs naive datetime comparison
        if date.tzinfo is not None and self.start.tzinfo is None:
            # Make date naive if it has timezone info
            date = date.replace(tzinfo=None)
        elif date.tzinfo is None and self.start.tzinfo is not None:
            # Make self dates naive if they have timezone info
            start = self.start.replace(tzinfo=None)
            end = self.end.replace(tzinfo=None)
            return start <= date <= end
        return self.start <= date <= self.end


@dataclass(frozen=True)
class HistoricalData:
    velocities: List[float]
    cycle_times: List[float]
    throughput: List[int]  # Number of issues completed per period
    dates: List[datetime]
    sprint_names: Optional[List[str]] = None  # Sprint names for X-axis labels
