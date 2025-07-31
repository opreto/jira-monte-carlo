"""Response models for presentation layer"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path


@dataclass
class ImportDataResponse:
    """Response model for data import operation"""

    success: bool
    issues_count: int
    sprints_count: int
    source_type: str
    field_mapping_used: Dict[str, str]
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    # Data quality metrics
    missing_fields: Dict[str, int] = field(default_factory=dict)
    data_quality_score: float = 0.0

    # Analysis results (if analyze_only was true)
    analysis_results: Optional[Dict[str, Any]] = None


@dataclass
class ForecastResponse:
    """Response model for forecast operation"""

    success: bool
    project_name: str
    remaining_work: float
    velocity_field: str

    # Forecast results
    percentile_50: int  # Sprints to complete at 50% confidence
    percentile_70: int  # Sprints to complete at 70% confidence
    percentile_85: int  # Sprints to complete at 85% confidence
    percentile_95: int  # Sprints to complete at 95% confidence

    # Dates (calculated based on sprint length)
    completion_date_50: Optional[datetime] = None
    completion_date_70: Optional[datetime] = None
    completion_date_85: Optional[datetime] = None
    completion_date_95: Optional[datetime] = None

    # Velocity metrics
    average_velocity: float = 0.0
    median_velocity: float = 0.0
    velocity_std_dev: float = 0.0
    velocity_trend: Optional[float] = None

    # Simulation details
    simulations_run: int = 0
    model_type: str = "Monte Carlo"

    # Additional insights
    confidence_intervals: Dict[int, Dict[str, Any]] = field(default_factory=dict)
    risk_assessment: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ReportResponse:
    """Response model for report generation"""

    success: bool
    report_path: Path
    report_url: Optional[str] = None
    generation_time: datetime = field(default_factory=datetime.now)

    # Report metadata
    charts_included: List[str] = field(default_factory=list)
    sections_included: List[str] = field(default_factory=list)
    theme_used: str = "opreto"

    # Process health summary (if included)
    health_score: Optional[float] = None
    health_insights: List[str] = field(default_factory=list)
    health_recommendations: List[str] = field(default_factory=list)

    # Warnings
    warnings: List[str] = field(default_factory=list)


@dataclass
class AnalysisResponse:
    """Response model for data analysis operation"""

    success: bool
    file_path: Path
    source_type_detected: str

    # Structure analysis
    total_rows: int
    total_columns: int
    column_names: List[str]

    # Field detection
    detected_mappings: Dict[str, str] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)

    # Data quality
    data_quality_score: float
    quality_issues: List[Dict[str, Any]] = field(default_factory=list)

    # Recommendations
    field_suggestions: Dict[str, List[str]] = field(default_factory=dict)
    mapping_recommendations: List[str] = field(default_factory=list)


@dataclass
class MultiProjectResponse:
    """Response model for multi-project operations"""

    success: bool
    projects_processed: int
    dashboard_path: Optional[Path] = None
    individual_report_paths: Dict[str, Path] = field(default_factory=dict)

    # Aggregated metrics
    total_issues: int = 0
    total_remaining_work: float = 0.0
    overall_completion_percentage: float = 0.0
    combined_velocity: float = 0.0

    # Project summaries
    project_summaries: List[Dict[str, Any]] = field(default_factory=list)

    # Errors by project
    project_errors: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ScenarioComparisonResponse:
    """Response model for scenario comparison"""

    success: bool
    baseline_results: Dict[str, Any]
    scenario_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Comparison metrics
    impact_analysis: Dict[str, Any] = field(default_factory=dict)
    best_case_scenario: Optional[str] = None
    worst_case_scenario: Optional[str] = None

    # Report paths
    comparison_report_path: Optional[Path] = None
    individual_scenario_paths: Dict[str, Path] = field(default_factory=dict)

    # Key insights
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
