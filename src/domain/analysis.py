"""Domain entities and value objects for CSV analysis"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class ColumnType(Enum):
    """Types of columns we can identify in CSV"""

    KEY = "key"
    STATUS = "status"
    NUMERIC = "numeric"
    DATE = "date"
    TEXT = "text"
    SPRINT = "sprint"
    USER = "user"
    CUSTOM_FIELD = "custom_field"
    UNKNOWN = "unknown"


class AggregationStrategy(Enum):
    """How to aggregate multiple columns of the same type"""

    FIRST = "first"  # Use first non-empty value
    LAST = "last"  # Use last non-empty value
    CONCATENATE = "concatenate"  # Join all values
    SUM = "sum"  # Sum numeric values
    MAX = "max"  # Take maximum value
    MIN = "min"  # Take minimum value


@dataclass
class ColumnPattern:
    """Pattern for identifying column types"""

    pattern_type: str
    keywords: List[str]
    regex_pattern: Optional[str] = None

    def matches(self, column_name: str) -> bool:
        column_lower = column_name.lower()
        return any(keyword in column_lower for keyword in self.keywords)


@dataclass
class ColumnMetadata:
    """Metadata about a CSV column"""

    index: int
    name: str
    column_type: ColumnType
    sample_values: List[str] = field(default_factory=list)
    non_empty_count: int = 0
    unique_values_count: int = 0
    data_type_guess: str = "string"  # string, numeric, date, boolean


@dataclass
class ColumnGroup:
    """Group of related columns that should be aggregated"""

    base_name: str
    columns: List[ColumnMetadata]
    aggregation_strategy: AggregationStrategy

    @property
    def indices(self) -> List[int]:
        return [col.index for col in self.columns]


@dataclass
class CSVAnalysisResult:
    """Result of analyzing CSV structure"""

    total_rows: int
    total_columns: int
    column_groups: Dict[str, ColumnGroup]
    field_mapping_suggestions: Dict[str, str]
    status_values: List[str]
    sprint_values: List[str]
    date_format_samples: Dict[str, List[str]]
    numeric_field_candidates: List[str]

    def get_aggregated_columns(self) -> Dict[str, List[int]]:
        """Get mapping of field names to column indices for aggregation"""
        return {name: group.indices for name, group in self.column_groups.items()}


@dataclass
class VelocityDataPoint:
    """Single velocity measurement"""

    sprint_name: str
    sprint_date: datetime
    completed_points: float
    issue_count: int

    @property
    def age_days(self) -> int:
        return (datetime.now() - self.sprint_date).days


@dataclass
class VelocityAnalysisConfig:
    """Configuration for velocity analysis"""

    lookback_sprints: int = 6
    outlier_std_devs: float = 2.0
    max_age_days: int = 240  # 8 months
    min_velocity: float = 1.0
    max_velocity: float = 200.0


@dataclass
class VelocityAnalysisResult:
    """Result of velocity analysis with outlier detection"""

    all_velocities: List[VelocityDataPoint]
    filtered_velocities: List[VelocityDataPoint]
    outliers_removed: List[VelocityDataPoint]
    average_velocity: float
    std_dev: float
    median_velocity: float
    trend: float
    confidence_level: float  # 0-1, how confident we are in the data
    sprint_duration_days: int = 14  # Detected or default sprint duration
