"""Request models for presentation layer"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class ImportDataRequest:
    """Request model for data import operation"""
    file_paths: List[Path]
    source_type: str = "auto"
    field_mapping: Optional[Dict[str, str]] = None
    analyze_only: bool = False
    
    # Field mapping details
    key_field: str = "Issue key"
    summary_field: str = "Summary"
    points_field: str = "Story Points"
    velocity_field: str = "Story Points"
    sprint_field: str = "Sprint"
    status_field: str = "Status"
    created_field: str = "Created"
    resolved_field: str = "Resolved"
    labels_field: str = "Labels"
    type_field: str = "Issue Type"
    assignee_field: str = "Assignee"
    project_field: str = "Project"
    blocked_field: Optional[str] = None
    
    def __post_init__(self):
        """Build field mapping from individual fields"""
        if self.field_mapping is None:
            self.field_mapping = {
                'id_field': self.key_field,
                'title_field': self.summary_field,
                'estimation_field': self.points_field,
                'velocity_field': self.velocity_field,
                'sprint_field': self.sprint_field,
                'status_field': self.status_field,
                'created_date_field': self.created_field,
                'resolved_date_field': self.resolved_field,
                'labels_field': self.labels_field,
                'issue_type_field': self.type_field,
                'assignee_field': self.assignee_field,
                'project_field': self.project_field,
                'blocked_field': self.blocked_field
            }


@dataclass
class ForecastRequest:
    """Request model for forecast operation"""
    project_name: Optional[str] = None
    remaining_work: Optional[float] = None
    velocity_field: str = "Story Points"
    lookback_sprints: int = 6
    sprint_length: int = 14
    simulations: int = 10000
    confidence_levels: List[int] = field(default_factory=lambda: [50, 70, 85, 95])
    done_statuses: List[str] = field(default_factory=lambda: ["Done", "Closed", "Resolved"])
    
    # Monte Carlo parameters
    use_historical_pattern: bool = True
    min_velocity_factor: float = 0.7
    max_velocity_factor: float = 1.3
    
    # Velocity scenario parameters
    velocity_adjustments: Optional[Dict[str, float]] = None
    scenario_name: Optional[str] = None
    scenario_description: Optional[str] = None


@dataclass
class ReportRequest:
    """Request model for report generation"""
    output_path: Optional[Path] = None
    project_name: Optional[str] = None
    theme: str = "opreto"
    open_browser: bool = False
    include_health_metrics: bool = True
    jira_url: Optional[str] = None
    jql_query: Optional[str] = None
    
    # Process health parameters
    stale_threshold_days: int = 30
    abandoned_threshold_days: int = 90
    wip_limits: Optional[Dict[str, int]] = None
    
    # Report customization
    include_charts: List[str] = field(default_factory=lambda: [
        "probability_distribution",
        "confidence_intervals",
        "velocity_trend",
        "forecast_timeline",
        "story_size_breakdown"
    ])
    
    custom_sections: Optional[Dict[str, Any]] = None


@dataclass
class MultiProjectRequest:
    """Request model for multi-project operations"""
    project_files: List[Path]
    aggregate_results: bool = True
    generate_dashboard: bool = True
    generate_individual_reports: bool = True
    output_directory: Optional[Path] = None
    theme: str = "opreto"


@dataclass
class ScenarioComparisonRequest:
    """Request model for scenario comparison"""
    baseline_name: str = "Current Velocity"
    scenarios: List[Dict[str, Any]] = field(default_factory=list)
    compare_charts: bool = True
    generate_combined_report: bool = True
    highlight_differences: bool = True


@dataclass
class AnalysisRequest:
    """Request model for data analysis operation"""
    file_path: Path
    source_type: str = "auto"
    detailed_analysis: bool = True
    suggest_mappings: bool = True
    validate_data_quality: bool = True