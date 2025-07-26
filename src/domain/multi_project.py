"""Domain entities and value objects for multi-project/CSV support"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from .entities import Issue, Sprint, SimulationResult
from .value_objects import VelocityMetrics, FieldMapping


@dataclass
class ProjectData:
    """Data from a single CSV file/project"""
    name: str  # Derived from filename or explicitly provided
    source_path: Path
    issues: List[Issue] = field(default_factory=list)
    sprints: List[Sprint] = field(default_factory=list)
    velocity_metrics: Optional[VelocityMetrics] = None
    simulation_result: Optional[SimulationResult] = None
    remaining_work: float = 0.0
    
    @property
    def total_issues(self) -> int:
        return len(self.issues)
    
    @property
    def done_issues(self) -> int:
        # Check common done statuses
        done_statuses = {'Done', 'Released', 'Closed', 'Resolved', 'Complete'}
        return len([i for i in self.issues if i.status in done_statuses])
    
    @property
    def todo_issues(self) -> int:
        # Check common todo statuses
        todo_statuses = {'To Do', 'Open', 'Backlog', 'Ready'}
        return len([i for i in self.issues if i.status in todo_statuses])
    
    @property
    def in_progress_issues(self) -> int:
        # Check common in-progress statuses
        progress_statuses = {'In Progress', 'In Development', 'In Review', 'Analysis'}
        return len([i for i in self.issues if i.status in progress_statuses])
    
    @property
    def completion_percentage(self) -> float:
        if self.total_issues == 0:
            return 0.0
        return (self.done_issues / self.total_issues) * 100


@dataclass
class AggregatedMetrics:
    """Aggregated metrics across multiple projects"""
    total_projects: int
    total_issues: int
    total_done_issues: int
    total_remaining_work: float
    average_velocity: float
    combined_velocity: float  # Sum of all team velocities
    earliest_completion_date: datetime
    latest_completion_date: datetime
    confidence_intervals: Dict[float, int]  # confidence level -> sprints
    
    @property
    def overall_completion_percentage(self) -> float:
        if self.total_issues == 0:
            return 0.0
        return (self.total_done_issues / self.total_issues) * 100


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