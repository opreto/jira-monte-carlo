"""Domain entities and value objects for multi-project/CSV support"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .entities import Issue, SimulationResult, Sprint
from .value_objects import VelocityMetrics


@dataclass
class ProjectData:
    """Data from a single CSV file/project"""

    name: str  # Derived from filename or explicitly provided
    file_path: Path  # Standardize on file_path
    total_issues: int = 0
    completed_issues: int = 0
    remaining_work: float = 0.0
    completion_percentage: float = 0.0
    velocity_metrics: Optional[VelocityMetrics] = None
    simulation_result: Optional[SimulationResult] = None
    historical_data: Optional[object] = None  # HistoricalData type
    sprints: List[Sprint] = field(default_factory=list)
    story_size_breakdown: Optional[Dict[float, int]] = None
    # Legacy support
    issues: List[Issue] = field(default_factory=list)
    source_path: Optional[Path] = None  # Backward compatibility

    def __post_init__(self):
        # Support legacy initialization with issues list
        if self.issues and not self.total_issues:
            self.total_issues = len(self.issues)
            done_statuses = {"Done", "Released", "Closed", "Resolved", "Complete"}
            self.completed_issues = len(
                [i for i in self.issues if i.status in done_statuses]
            )
            if self.total_issues > 0:
                self.completion_percentage = (
                    self.completed_issues / self.total_issues
                ) * 100
        # Support legacy source_path
        if self.source_path and not self.file_path:
            self.file_path = self.source_path

    @property
    def done_issues(self) -> int:
        # Legacy property for backward compatibility
        return self.completed_issues

    @property
    def todo_issues(self) -> int:
        # Check common todo statuses
        if self.issues:
            todo_statuses = {"To Do", "Open", "Backlog", "Ready"}
            return len([i for i in self.issues if i.status in todo_statuses])
        return self.total_issues - self.completed_issues

    @property
    def in_progress_issues(self) -> int:
        # Check common in-progress statuses
        if self.issues:
            progress_statuses = {
                "In Progress",
                "In Development",
                "In Review",
                "Analysis",
            }
            return len([i for i in self.issues if i.status in progress_statuses])
        return 0


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across multiple projects"""

    total_projects: int
    total_issues: int
    total_completed_issues: int
    total_remaining_work: float
    combined_velocity: float  # Sum of all team velocities
    combined_simulation_result: Optional[SimulationResult] = None

    @property
    def overall_completion_percentage(self) -> float:
        if self.total_issues == 0:
            return 0.0
        return (self.total_completed_issues / self.total_issues) * 100


@dataclass
class MultiProjectReport:
    """Container for multi-project simulation results"""

    projects: List[ProjectData]
    aggregated_metrics: AggregatedMetrics
    generated_at: datetime = field(default_factory=datetime.now)

    @property
    def has_multiple_projects(self) -> bool:
        return len(self.projects) > 1

    def get_project_by_name(self, name: str) -> Optional[ProjectData]:
        """Get a specific project by name"""
        for project in self.projects:
            if project.name == name:
                return project
        return None
