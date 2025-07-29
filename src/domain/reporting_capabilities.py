"""Domain entities for reporting capabilities based on available data"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set


class ReportType(Enum):
    """Types of reports that can be generated"""

    # Core forecasting reports (always available)
    MONTE_CARLO_FORECAST = "monte_carlo_forecast"
    VELOCITY_TREND = "velocity_trend"
    STORY_SIZE_BREAKDOWN = "story_size_breakdown"

    # Process health metrics
    WORK_IN_PROGRESS = "work_in_progress"
    AGING_WORK_ITEMS = "aging_work_items"
    SPRINT_HEALTH = "sprint_health"
    BLOCKED_ITEMS = "blocked_items"

    # Flow metrics
    CYCLE_TIME_DISTRIBUTION = "cycle_time_distribution"
    THROUGHPUT_TREND = "throughput_trend"
    CUMULATIVE_FLOW = "cumulative_flow"

    # Team metrics
    SPRINT_PREDICTABILITY = "sprint_predictability"
    ESTIMATION_ACCURACY = "estimation_accuracy"


class DataRequirement(Enum):
    """Data fields required for different reports"""

    # Basic fields
    KEY = "key"
    STATUS = "status"
    CREATED_DATE = "created_date"
    RESOLVED_DATE = "resolved_date"
    UPDATED_DATE = "updated_date"

    # Estimation fields
    STORY_POINTS = "story_points"
    TIME_ESTIMATE = "time_estimate"
    TIME_SPENT = "time_spent"

    # Sprint fields
    SPRINT = "sprint"
    SPRINT_DATES = "sprint_dates"

    # Additional fields
    ASSIGNEE = "assignee"
    LABELS = "labels"
    BLOCKED_STATUS = "blocked_status"
    ISSUE_TYPE = "issue_type"


@dataclass
class ReportCapability:
    """Describes a report's requirements and availability"""

    report_type: ReportType
    display_name: str
    description: str
    required_fields: Set[DataRequirement]
    optional_fields: Set[DataRequirement] = field(default_factory=set)
    is_available: bool = False
    missing_fields: Set[DataRequirement] = field(default_factory=set)
    degraded_mode: bool = False  # True if report can run with reduced functionality


@dataclass
class ReportingCapabilities:
    """Collection of available reporting capabilities based on data analysis"""

    available_reports: List[ReportCapability]
    all_reports: List[ReportCapability]
    data_quality_score: float  # 0-1, based on how many fields are available
    warnings: List[str] = field(default_factory=list)

    @property
    def available_report_types(self) -> Set[ReportType]:
        """Get set of available report types"""
        return {r.report_type for r in self.available_reports}

    def get_capability(self, report_type: ReportType) -> Optional[ReportCapability]:
        """Get capability for a specific report type"""
        for report in self.all_reports:
            if report.report_type == report_type:
                return report
        return None

    def is_available(self, report_type: ReportType) -> bool:
        """Check if a report type is available"""
        return report_type in self.available_report_types

    @property
    def unavailable_reports(self) -> Dict[str, List[str]]:
        """Get dictionary of unavailable reports and their missing fields"""
        unavailable = {}
        for report in self.all_reports:
            if not report.is_available and report.missing_fields:
                # Convert enum values to human-readable strings
                missing_field_names = []
                for missing_field in report.missing_fields:
                    field_name = missing_field.value.replace("_", " ").title()
                    missing_field_names.append(field_name)
                unavailable[report.display_name] = missing_field_names
        return unavailable


# Define report requirements
REPORT_REQUIREMENTS: Dict[ReportType, ReportCapability] = {
    ReportType.MONTE_CARLO_FORECAST: ReportCapability(
        report_type=ReportType.MONTE_CARLO_FORECAST,
        display_name="Monte Carlo Forecast",
        description="Statistical project completion forecast",
        required_fields={DataRequirement.STATUS, DataRequirement.STORY_POINTS},
        optional_fields={DataRequirement.SPRINT},
    ),
    ReportType.VELOCITY_TREND: ReportCapability(
        report_type=ReportType.VELOCITY_TREND,
        display_name="Velocity Trend",
        description="Historical velocity analysis with trends",
        required_fields={DataRequirement.STATUS, DataRequirement.STORY_POINTS, DataRequirement.SPRINT},
        optional_fields={DataRequirement.SPRINT_DATES},
    ),
    ReportType.WORK_IN_PROGRESS: ReportCapability(
        report_type=ReportType.WORK_IN_PROGRESS,
        display_name="Work In Progress (WIP)",
        description="Current WIP by status with limits",
        required_fields={DataRequirement.STATUS, DataRequirement.CREATED_DATE},
        optional_fields={DataRequirement.ASSIGNEE, DataRequirement.STORY_POINTS},
    ),
    ReportType.AGING_WORK_ITEMS: ReportCapability(
        report_type=ReportType.AGING_WORK_ITEMS,
        display_name="Aging Work Items",
        description="Items that have been in progress too long",
        required_fields={DataRequirement.STATUS, DataRequirement.CREATED_DATE},
        optional_fields={DataRequirement.UPDATED_DATE, DataRequirement.ASSIGNEE},
    ),
    ReportType.SPRINT_HEALTH: ReportCapability(
        report_type=ReportType.SPRINT_HEALTH,
        display_name="Sprint Health Metrics",
        description="Sprint completion rates and scope changes",
        required_fields={DataRequirement.STATUS, DataRequirement.SPRINT, DataRequirement.STORY_POINTS},
        optional_fields={DataRequirement.SPRINT_DATES, DataRequirement.CREATED_DATE},
    ),
    ReportType.BLOCKED_ITEMS: ReportCapability(
        report_type=ReportType.BLOCKED_ITEMS,
        display_name="Blocked Items",
        description="Track blocked items and duration",
        required_fields={DataRequirement.STATUS, DataRequirement.LABELS},
        optional_fields={DataRequirement.UPDATED_DATE, DataRequirement.ASSIGNEE},
    ),
    ReportType.CYCLE_TIME_DISTRIBUTION: ReportCapability(
        report_type=ReportType.CYCLE_TIME_DISTRIBUTION,
        display_name="Cycle Time Distribution",
        description="Distribution of time from start to completion",
        required_fields={DataRequirement.CREATED_DATE, DataRequirement.RESOLVED_DATE},
        optional_fields={DataRequirement.ISSUE_TYPE},
    ),
    ReportType.THROUGHPUT_TREND: ReportCapability(
        report_type=ReportType.THROUGHPUT_TREND,
        display_name="Throughput Trend",
        description="Number of items completed over time",
        required_fields={DataRequirement.STATUS, DataRequirement.RESOLVED_DATE},
        optional_fields={DataRequirement.STORY_POINTS},
    ),
    ReportType.CUMULATIVE_FLOW: ReportCapability(
        report_type=ReportType.CUMULATIVE_FLOW,
        display_name="Cumulative Flow Diagram",
        description="Work items by status over time",
        required_fields={DataRequirement.STATUS, DataRequirement.CREATED_DATE, DataRequirement.UPDATED_DATE},
        optional_fields={DataRequirement.RESOLVED_DATE},
    ),
    ReportType.SPRINT_PREDICTABILITY: ReportCapability(
        report_type=ReportType.SPRINT_PREDICTABILITY,
        display_name="Sprint Predictability",
        description="Consistency of sprint velocity",
        required_fields={DataRequirement.SPRINT, DataRequirement.STORY_POINTS, DataRequirement.STATUS},
        optional_fields={DataRequirement.SPRINT_DATES},
    ),
    ReportType.ESTIMATION_ACCURACY: ReportCapability(
        report_type=ReportType.ESTIMATION_ACCURACY,
        display_name="Estimation Accuracy",
        description="Comparison of estimates vs actuals",
        required_fields={DataRequirement.TIME_ESTIMATE, DataRequirement.TIME_SPENT},
        optional_fields={DataRequirement.STORY_POINTS, DataRequirement.ASSIGNEE},
    ),
}
