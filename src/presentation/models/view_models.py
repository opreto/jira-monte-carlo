"""View models for presentation layer - optimized for rendering"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


@dataclass
class ChartViewModel:
    """View model for chart rendering"""
    chart_id: str
    chart_type: str  # 'bar', 'line', 'pie', 'scatter', 'gauge'
    title: str
    description: str
    data: Dict[str, Any]  # Plotly-ready data
    layout: Dict[str, Any]  # Plotly layout configuration
    
    # Additional metadata
    insights: List[str] = field(default_factory=list)
    interactive: bool = True
    responsive: bool = True


@dataclass
class MetricCardViewModel:
    """View model for metric card display"""
    label: str
    value: str
    unit: Optional[str] = None
    trend: Optional[str] = None  # 'up', 'down', 'stable'
    trend_value: Optional[str] = None
    color: str = "primary"  # 'primary', 'success', 'warning', 'error'
    icon: Optional[str] = None


@dataclass
class TableRowViewModel:
    """View model for table rows"""
    cells: List[str]
    row_class: Optional[str] = None
    is_header: bool = False
    clickable: bool = False
    link: Optional[str] = None


@dataclass
class ProgressBarViewModel:
    """View model for progress bars"""
    label: str
    value: float  # 0-100
    color: str = "primary"
    show_percentage: bool = True
    striped: bool = False
    animated: bool = False


@dataclass
class AlertViewModel:
    """View model for alerts/notifications"""
    message: str
    type: str = "info"  # 'info', 'success', 'warning', 'error'
    dismissible: bool = True
    icon: Optional[str] = None
    actions: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class TimelineEventViewModel:
    """View model for timeline events"""
    date: datetime
    title: str
    description: Optional[str] = None
    type: str = "default"  # 'default', 'milestone', 'risk', 'success'
    icon: Optional[str] = None


@dataclass
class HealthScoreViewModel:
    """View model for health score display"""
    overall_score: float  # 0-100
    score_label: str  # 'Excellent', 'Good', 'Fair', 'Poor'
    score_color: str  # Color based on score
    
    # Breakdown components
    components: List['HealthComponentViewModel'] = field(default_factory=list)
    
    # Gauge chart data
    gauge_chart: Optional[ChartViewModel] = None


@dataclass
class HealthComponentViewModel:
    """View model for health score components"""
    name: str
    score: float  # 0-100
    weight: float  # Component weight in overall score
    description: str
    
    # Visual properties
    color: str
    icon: Optional[str] = None
    
    # Details
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    affected_items: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ForecastSummaryViewModel:
    """View model for forecast summary display"""
    project_name: str
    remaining_work_display: str
    velocity_display: str
    
    # Key dates
    confidence_levels: List[Tuple[str, str, str]]  # (level, sprints, date)
    
    # Risk assessment
    risk_level: str  # 'low', 'medium', 'high'
    risk_color: str
    risk_message: str
    
    # Visual elements
    summary_cards: List[MetricCardViewModel] = field(default_factory=list)
    timeline_chart: Optional[ChartViewModel] = None


@dataclass
class ReportViewModel:
    """Main view model for report rendering"""
    # Header
    title: str
    subtitle: Optional[str] = None
    generated_date: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    
    # Metadata
    project_name: Optional[str] = None
    theme_name: str = "opreto"
    
    # Sections
    has_scenario_banner: bool = False
    scenario_banner: Optional[Dict[str, Any]] = None
    
    has_jql_query: bool = False
    jql_query: Optional[str] = None
    jira_url: Optional[str] = None
    
    # Metrics
    metric_cards: List[MetricCardViewModel] = field(default_factory=list)
    
    # Charts
    charts: Dict[str, ChartViewModel] = field(default_factory=dict)
    
    # Tables
    summary_table: Optional[List[TableRowViewModel]] = None
    
    # Process health
    has_health_metrics: bool = False
    health_score: Optional[HealthScoreViewModel] = None
    health_charts: Dict[str, ChartViewModel] = field(default_factory=dict)
    
    # Footer
    footer_text: str = "Sprint Radar - Agile Analytics Platform by Opreto"
    methodology_description: Optional[str] = None
    simulation_count: Optional[str] = None
    
    # Reporting capabilities
    has_reporting_info: bool = False
    available_reports_count: int = 0
    total_reports_count: int = 0
    data_quality_percentage: int = 0
    unavailable_reports: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class DashboardViewModel:
    """View model for multi-project dashboard"""
    title: str = "Sprint Radar Multi-Project Dashboard"
    subtitle: str = ""
    
    # Summary metrics
    summary_cards: List[MetricCardViewModel] = field(default_factory=list)
    
    # Project table
    project_table_headers: List[str] = field(default_factory=list)
    project_table_rows: List[TableRowViewModel] = field(default_factory=list)
    
    # Comparison charts
    comparison_charts: Dict[str, ChartViewModel] = field(default_factory=dict)
    
    # Navigation
    project_links: Dict[str, str] = field(default_factory=dict)


@dataclass
class ScenarioComparisonViewModel:
    """View model for scenario comparison display"""
    title: str
    baseline_name: str
    scenario_names: List[str]
    
    # Scenario switcher
    has_scenario_switcher: bool = True
    current_scenario: str = "baseline"
    
    # Comparison data
    scenario_data: Dict[str, Any] = field(default_factory=dict)
    
    # Charts that update based on scenario
    dynamic_charts: Dict[str, ChartViewModel] = field(default_factory=dict)
    
    # Impact analysis
    impact_summary: List[MetricCardViewModel] = field(default_factory=list)
    comparison_table: List[TableRowViewModel] = field(default_factory=list)
    
    # Insights
    key_insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)