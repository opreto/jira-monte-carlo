"""Use cases for CSV analysis and field detection"""
import logging
import random
from typing import List, Dict, Optional, Set, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
import statistics

from ..domain.analysis import (
    ColumnType, AggregationStrategy, ColumnPattern, ColumnMetadata,
    ColumnGroup, CSVAnalysisResult, VelocityDataPoint, 
    VelocityAnalysisConfig, VelocityAnalysisResult
)

logger = logging.getLogger(__name__)


class AnalyzeCSVStructureUseCase:
    """Analyze CSV structure to detect column types and relationships"""
    
    # Define patterns for column type detection
    COLUMN_PATTERNS = [
        ColumnPattern(pattern_type="key", keywords=["key", "id", "identifier"]),
        ColumnPattern(pattern_type="status", keywords=["status", "state", "stage"]),
        ColumnPattern(pattern_type="sprint", keywords=["sprint", "iteration"]),
        ColumnPattern(pattern_type="date", keywords=["date", "created", "updated", "resolved", "due", "time"]),
        ColumnPattern(pattern_type="numeric", keywords=["points", "story", "estimate", "hours", "days", "effort", "size"]),
        ColumnPattern(pattern_type="user", keywords=["assignee", "reporter", "owner", "user", "developer", "creator"]),
    ]
    
    def __init__(self, sample_size: int = 100):
        self.sample_size = sample_size
    
    def execute(self, headers: List[str], rows: List[List[str]]) -> CSVAnalysisResult:
        """Analyze CSV structure by sampling rows"""
        logger.info(f"Analyzing CSV with {len(headers)} columns and {len(rows)} rows")
        
        # Sample rows for analysis
        sample_rows = self._sample_rows(rows)
        
        # Analyze each column
        column_metadata = self._analyze_columns(headers, sample_rows)
        
        # Group related columns
        column_groups = self._group_related_columns(column_metadata)
        
        # Extract specific values
        status_values = self._extract_unique_values(sample_rows, column_groups.get("status"))
        sprint_values = self._extract_sprint_values(sample_rows, column_groups.get("sprint"))
        
        # Suggest field mappings
        field_mappings = self._suggest_field_mappings(column_groups)
        
        # Analyze date formats
        date_formats = self._analyze_date_formats(sample_rows, column_metadata)
        
        # Find numeric field candidates
        numeric_candidates = [
            col.name for col in column_metadata 
            if col.column_type == ColumnType.NUMERIC or 
            (col.column_type == ColumnType.CUSTOM_FIELD and "point" in col.name.lower())
        ]
        
        return CSVAnalysisResult(
            total_rows=len(rows),
            total_columns=len(headers),
            column_groups=column_groups,
            field_mapping_suggestions=field_mappings,
            status_values=status_values,
            sprint_values=sprint_values,
            date_format_samples=date_formats,
            numeric_field_candidates=numeric_candidates
        )
    
    def _sample_rows(self, rows: List[List[str]]) -> List[List[str]]:
        """Sample rows for analysis"""
        if len(rows) <= self.sample_size:
            return rows
        return random.sample(rows, self.sample_size)
    
    def _analyze_columns(self, headers: List[str], sample_rows: List[List[str]]) -> List[ColumnMetadata]:
        """Analyze each column to determine type and characteristics"""
        column_metadata = []
        
        for idx, header in enumerate(headers):
            # Get sample values for this column
            sample_values = []
            non_empty_count = 0
            
            for row in sample_rows:
                if idx < len(row) and row[idx] is not None:
                    # Convert to string and strip whitespace
                    value_str = str(row[idx]).strip()
                    if value_str and value_str != 'nan':  # Skip empty and NaN values
                        sample_values.append(value_str)
                        non_empty_count += 1
            
            # Determine column type
            col_type = self._detect_column_type(header, sample_values)
            
            # Guess data type from samples
            data_type = self._guess_data_type(sample_values[:10])
            
            metadata = ColumnMetadata(
                index=idx,
                name=header,
                column_type=col_type,
                sample_values=sample_values[:5],  # Keep first 5 samples
                non_empty_count=non_empty_count,
                unique_values_count=len(set(sample_values)),
                data_type_guess=data_type
            )
            column_metadata.append(metadata)
        
        return column_metadata
    
    def _detect_column_type(self, header: str, sample_values: List[str]) -> ColumnType:
        """Detect column type based on header and sample values"""
        header_lower = header.lower()
        
        # Check header patterns
        for pattern in self.COLUMN_PATTERNS:
            if pattern.matches(header):
                return ColumnType(pattern.pattern_type)
        
        # Check for custom fields
        if header.startswith("Custom field"):
            # Further analyze custom field type
            if any(word in header_lower for word in ["story", "point", "estimate", "size"]):
                return ColumnType.NUMERIC
            elif "sprint" in header_lower:
                return ColumnType.SPRINT
            return ColumnType.CUSTOM_FIELD
        
        # Analyze sample values if header doesn't match
        if sample_values:
            # Check if values look like dates
            if self._looks_like_dates(sample_values[:5]):
                return ColumnType.DATE
            # Check if values are mostly numeric
            elif self._mostly_numeric(sample_values[:10]):
                return ColumnType.NUMERIC
        
        return ColumnType.UNKNOWN
    
    def _group_related_columns(self, columns: List[ColumnMetadata]) -> Dict[str, ColumnGroup]:
        """Group columns that appear to be related (e.g., multiple Sprint columns)"""
        groups = {}
        
        # First, handle Polars duplicate column naming pattern
        base_name_groups = defaultdict(list)
        
        for col in columns:
            # Check if this is a Polars-renamed duplicate column
            if "_duplicated_" in col.name:
                # Extract base name (e.g., "Sprint_duplicated_0" -> "Sprint")
                base_name = col.name.split("_duplicated_")[0]
                base_name_groups[base_name].append(col)
            else:
                # Check if there are duplicated versions of this column
                has_duplicates = any(
                    other.name.startswith(f"{col.name}_duplicated_") 
                    for other in columns
                )
                if has_duplicates:
                    base_name_groups[col.name].append(col)
                else:
                    # Single column, no duplicates
                    base_name_groups[col.name].append(col)
        
        # Create column groups
        for base_name, cols in base_name_groups.items():
            normalized_name = base_name.lower().replace(" ", "_")
            
            if len(cols) > 1:
                # Multiple columns - determine aggregation strategy
                if "sprint" in base_name.lower():
                    strategy = AggregationStrategy.LAST  # Use most recent sprint
                elif any(col.column_type == ColumnType.NUMERIC for col in cols):
                    strategy = AggregationStrategy.SUM
                else:
                    strategy = AggregationStrategy.LAST
                
                groups[normalized_name] = ColumnGroup(
                    base_name=normalized_name,
                    columns=cols,
                    aggregation_strategy=strategy
                )
            else:
                # Single column
                groups[normalized_name] = ColumnGroup(
                    base_name=normalized_name,
                    columns=cols,
                    aggregation_strategy=AggregationStrategy.FIRST
                )
        
        return groups
    
    def _suggest_field_mappings(self, column_groups: Dict[str, ColumnGroup]) -> Dict[str, str]:
        """Suggest field mappings based on column analysis"""
        suggestions = {}
        
        # Map standard fields
        for group_name, group in column_groups.items():
            if group.columns and group.columns[0].column_type == ColumnType.KEY:
                if "issue" in group_name:
                    suggestions["key_field"] = group.columns[0].name
            elif group.columns and group.columns[0].column_type == ColumnType.STATUS:
                suggestions["status_field"] = group.columns[0].name
            elif group.columns and group.columns[0].column_type == ColumnType.SPRINT:
                suggestions["sprint_field"] = group.columns[0].name
            elif group.columns and group.columns[0].column_type == ColumnType.DATE:
                if "created" in group_name:
                    suggestions["created_field"] = group.columns[0].name
                elif "resolved" in group_name:
                    suggestions["resolved_field"] = group.columns[0].name
                elif "updated" in group_name:
                    suggestions["updated_field"] = group.columns[0].name
        
        # Find story points field
        for group_name, group in column_groups.items():
            col = group.columns[0]
            if col.column_type == ColumnType.NUMERIC or col.column_type == ColumnType.CUSTOM_FIELD:
                if any(word in col.name.lower() for word in ["story", "point", "estimate"]):
                    suggestions["story_points_field"] = col.name
                    break
        
        return suggestions
    
    def _extract_unique_values(self, rows: List[List[str]], column_group: Optional[ColumnGroup]) -> List[str]:
        """Extract unique values from a column group"""
        if not column_group:
            return []
        
        values = set()
        for row in rows:
            for col in column_group.columns:
                if col.index < len(row) and row[col.index] is not None:
                    value_str = str(row[col.index]).strip()
                    if value_str and value_str != 'nan':
                        values.add(value_str)
        
        return sorted(list(values))
    
    def _extract_sprint_values(self, rows: List[List[str]], sprint_group: Optional[ColumnGroup]) -> List[str]:
        """Extract sprint values using the aggregation strategy"""
        if not sprint_group:
            return []
        
        sprint_values = set()
        for row in rows:
            # Apply aggregation strategy
            if sprint_group.aggregation_strategy == AggregationStrategy.LAST:
                # Get last non-empty sprint value
                for col in reversed(sprint_group.columns):
                    if col.index < len(row) and row[col.index] is not None:
                        value_str = str(row[col.index]).strip()
                        if value_str and value_str != 'nan':
                            sprint_values.add(value_str)
                            break
            else:
                # Get all sprint values
                for col in sprint_group.columns:
                    if col.index < len(row) and row[col.index] is not None:
                        value_str = str(row[col.index]).strip()
                        if value_str and value_str != 'nan':
                            sprint_values.add(value_str)
        
        return sorted(list(sprint_values))
    
    def _analyze_date_formats(self, rows: List[List[str]], columns: List[ColumnMetadata]) -> Dict[str, List[str]]:
        """Analyze date formats in date columns"""
        date_formats = {}
        
        for col in columns:
            if col.column_type == ColumnType.DATE:
                samples = []
                for row in rows[:5]:  # Sample first 5 rows
                    if col.index < len(row) and row[col.index] is not None:
                        value_str = str(row[col.index]).strip()
                        if value_str and value_str != 'nan':
                            samples.append(value_str)
                
                if samples:
                    date_formats[col.name] = samples
        
        return date_formats
    
    def _looks_like_dates(self, values: List[str]) -> bool:
        """Check if values look like dates"""
        date_patterns = [
            r'\d{1,2}/\w{3}/\d{2}',  # 13/Jun/25
            r'\d{4}-\d{2}-\d{2}',    # 2025-06-13
            r'\d{1,2}/\d{1,2}/\d{4}', # 06/13/2025
        ]
        
        matches = 0
        for value in values:
            for pattern in date_patterns:
                if re.search(pattern, value):
                    matches += 1
                    break
        
        return matches >= len(values) * 0.5
    
    def _mostly_numeric(self, values: List[str]) -> bool:
        """Check if values are mostly numeric"""
        numeric_count = 0
        for value in values:
            try:
                float(str(value))
                numeric_count += 1
            except:
                pass
        
        return numeric_count >= len(values) * 0.7
    
    def _guess_data_type(self, values: List[str]) -> str:
        """Guess the data type from sample values"""
        if not values:
            return "string"
        
        # Check for numeric
        if self._mostly_numeric(values):
            return "numeric"
        
        # Check for dates
        if self._looks_like_dates(values):
            return "date"
        
        # Check for boolean
        unique_values = set(v.lower() for v in values)
        if unique_values.issubset({"true", "false", "yes", "no", "1", "0", ""}):
            return "boolean"
        
        return "string"


class AnalyzeVelocityUseCase:
    """Analyze velocity data with outlier detection and time filtering"""
    
    def execute(self, 
                velocity_data: List[VelocityDataPoint],
                config: VelocityAnalysisConfig) -> VelocityAnalysisResult:
        """Analyze velocity data and filter outliers"""
        
        if not velocity_data:
            return VelocityAnalysisResult(
                all_velocities=[],
                filtered_velocities=[],
                outliers_removed=[],
                average_velocity=0.0,
                std_dev=0.0,
                median_velocity=0.0,
                trend=0.0,
                confidence_level=0.0
            )
        
        # Filter by age
        age_filtered = [
            v for v in velocity_data 
            if v.age_days <= config.max_age_days
        ]
        
        if not age_filtered:
            age_filtered = velocity_data  # Use all if none meet criteria
        
        # Filter by min/max bounds
        bound_filtered = [
            v for v in age_filtered
            if config.min_velocity <= v.completed_points <= config.max_velocity
        ]
        
        if not bound_filtered:
            bound_filtered = age_filtered
        
        # Calculate statistics for outlier detection
        velocities = [v.completed_points for v in bound_filtered]
        mean = statistics.mean(velocities) if velocities else 0
        std_dev = statistics.stdev(velocities) if len(velocities) > 1 else 0
        
        # Filter outliers using z-score
        filtered_velocities = []
        outliers = []
        
        for v in bound_filtered:
            if std_dev > 0:
                z_score = abs((v.completed_points - mean) / std_dev)
                if z_score <= config.outlier_std_devs:
                    filtered_velocities.append(v)
                else:
                    outliers.append(v)
            else:
                filtered_velocities.append(v)
        
        # Take most recent sprints if configured
        if config.lookback_sprints > 0 and len(filtered_velocities) > config.lookback_sprints:
            filtered_velocities = sorted(
                filtered_velocities, 
                key=lambda v: v.sprint_date, 
                reverse=True
            )[:config.lookback_sprints]
        
        # Calculate final statistics
        final_velocities = [v.completed_points for v in filtered_velocities]
        
        if final_velocities:
            final_mean = statistics.mean(final_velocities)
            final_std = statistics.stdev(final_velocities) if len(final_velocities) > 1 else 0
            final_median = statistics.median(final_velocities)
            
            # Calculate trend
            if len(final_velocities) >= 2:
                x = list(range(len(final_velocities)))
                x_mean = sum(x) / len(x)
                y_mean = final_mean
                
                numerator = sum((x[i] - x_mean) * (final_velocities[i] - y_mean) for i in range(len(x)))
                denominator = sum((x[i] - x_mean) ** 2 for i in range(len(x)))
                
                trend = numerator / denominator if denominator != 0 else 0.0
            else:
                trend = 0.0
            
            # Calculate confidence level based on data quality
            confidence = self._calculate_confidence(filtered_velocities, outliers, config)
        else:
            final_mean = final_std = final_median = trend = confidence = 0.0
        
        # Detect sprint duration from filtered velocities
        sprint_duration = self._detect_sprint_duration(filtered_velocities)
        
        return VelocityAnalysisResult(
            all_velocities=velocity_data,
            filtered_velocities=filtered_velocities,
            outliers_removed=outliers,
            average_velocity=final_mean,
            std_dev=final_std,
            median_velocity=final_median,
            trend=trend,
            confidence_level=confidence,
            sprint_duration_days=sprint_duration
        )
    
    def _calculate_confidence(self, 
                            filtered: List[VelocityDataPoint],
                            outliers: List[VelocityDataPoint],
                            config: VelocityAnalysisConfig) -> float:
        """Calculate confidence level in the velocity data"""
        if not filtered:
            return 0.0
        
        confidence = 1.0
        
        # Reduce confidence for too few data points
        if len(filtered) < 3:
            confidence *= 0.5
        elif len(filtered) < 6:
            confidence *= 0.8
        
        # Reduce confidence for high outlier ratio
        total_points = len(filtered) + len(outliers)
        if total_points > 0:
            outlier_ratio = len(outliers) / total_points
            if outlier_ratio > 0.3:
                confidence *= 0.7
            elif outlier_ratio > 0.2:
                confidence *= 0.85
        
        # Reduce confidence for high variance
        if filtered:
            velocities = [v.completed_points for v in filtered]
            if velocities:
                mean_vel = statistics.mean(velocities)
                std_vel = statistics.stdev(velocities) if len(velocities) > 1 else 0
                cv = std_vel / mean_vel if mean_vel > 0 else 1
                if cv > 0.5:  # Coefficient of variation > 50%
                    confidence *= 0.8
        
        return min(max(confidence, 0.0), 1.0)
    
    def _detect_sprint_duration(self, velocities: List[VelocityDataPoint]) -> int:
        """Detect sprint duration from velocity data points"""
        if len(velocities) < 2:
            return 14  # Default to 2 weeks
        
        # Calculate date differences between consecutive sprints
        sorted_velocities = sorted(velocities, key=lambda v: v.sprint_date)
        date_diffs = []
        
        for i in range(1, len(sorted_velocities)):
            diff = (sorted_velocities[i].sprint_date - sorted_velocities[i-1].sprint_date).days
            if diff > 0:  # Only consider positive differences
                date_diffs.append(diff)
        
        if not date_diffs:
            return 14
        
        # Find the most common difference (mode)
        from collections import Counter
        diff_counts = Counter(date_diffs)
        most_common_diff = diff_counts.most_common(1)[0][0]
        
        # Round to nearest week
        weeks = round(most_common_diff / 7)
        sprint_duration = weeks * 7
        
        # Validate it's a reasonable sprint duration (1-4 weeks)
        if sprint_duration < 7:
            sprint_duration = 7
        elif sprint_duration > 28:
            sprint_duration = 14  # Default to 2 weeks if unreasonable
        
        logger.info(f"Detected sprint duration: {sprint_duration} days ({sprint_duration // 7} weeks)")
        return sprint_duration