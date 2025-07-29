from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class IssueStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    UNKNOWN = "unknown"


@dataclass
class Issue:
    key: str
    summary: str
    issue_type: str
    status: str
    created: datetime
    updated: Optional[datetime] = None
    resolved: Optional[datetime] = None
    story_points: Optional[float] = None
    time_estimate: Optional[float] = None
    time_spent: Optional[float] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    labels: List[str] = field(default_factory=list)
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    @property
    def cycle_time(self) -> Optional[float]:
        if self.resolved and self.created:
            return (self.resolved - self.created).days
        return None

    @property
    def age(self) -> float:
        # Use timezone-naive datetime for consistency
        if self.resolved:
            end_date = self.resolved
            if end_date and end_date.tzinfo:
                end_date = end_date.replace(tzinfo=None)
        else:
            end_date = datetime.now().replace(tzinfo=None)
            
        if self.created:
            created = self.created
            if created.tzinfo:
                # Remove timezone info if present
                created = created.replace(tzinfo=None)
            return (end_date - created).days
        else:
            return 0


@dataclass
class Sprint:
    name: str
    start_date: datetime
    end_date: datetime
    completed_points: float = 0.0
    completed_issues: List[Issue] = field(default_factory=list)

    @property
    def velocity(self) -> float:
        return self.completed_points

    @property
    def duration_days(self) -> int:
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 14  # Default sprint duration


@dataclass
class Team:
    name: str
    members: List[str]
    historical_velocities: List[float] = field(default_factory=list)

    @property
    def average_velocity(self) -> float:
        if not self.historical_velocities:
            return 0.0
        return sum(self.historical_velocities) / len(self.historical_velocities)

    @property
    def velocity_std_dev(self) -> float:
        if len(self.historical_velocities) < 2:
            return 0.0
        # Calculate standard deviation manually to avoid numpy dependency in domain
        mean = self.average_velocity
        variance = sum((x - mean) ** 2 for x in self.historical_velocities) / len(self.historical_velocities)
        return variance**0.5


@dataclass
class SimulationConfig:
    num_simulations: int = 10000
    confidence_levels: List[float] = field(default_factory=lambda: [0.5, 0.7, 0.85, 0.95])
    velocity_field: str = "story_points"
    done_statuses: List[str] = field(default_factory=lambda: ["Done", "Closed"])
    in_progress_statuses: List[str] = field(default_factory=lambda: ["In Progress"])
    todo_statuses: List[str] = field(default_factory=lambda: ["To Do", "Open"])
    sprint_duration_days: int = 14


@dataclass
class SimulationResult:
    percentiles: Dict[float, float]
    mean_completion_date: datetime
    std_dev_days: float
    probability_distribution: List[float]
    completion_dates: List[datetime]
    confidence_intervals: Dict[float, tuple]
    completion_sprints: List[int] = field(default_factory=list)
