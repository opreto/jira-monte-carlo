"""Infrastructure implementation of CSV analysis with column aggregation"""
import logging
from typing import Dict, List, Any, Optional, Tuple
import polars as pl
from datetime import datetime, timedelta

from ..domain.analysis import AggregationStrategy, ColumnGroup
from ..domain.value_objects import FieldMapping

logger = logging.getLogger(__name__)


class SmartCSVParser:
    """Enhanced CSV parser that handles column aggregation based on analysis results"""
    
    def __init__(self, field_mapping: FieldMapping, column_groups: Dict[str, ColumnGroup]):
        self.field_mapping = field_mapping
        self.column_groups = column_groups
        self._column_aggregators = self._build_aggregators()
    
    def parse_file(self, file_path, batch_size: int = 10000) -> pl.DataFrame:
        """Parse CSV file with smart column aggregation"""
        logger.info(f"Parsing CSV with smart aggregation: {file_path}")
        
        # Read CSV with Polars
        df = pl.read_csv(file_path, infer_schema_length=10000)
        
        # Apply column aggregations
        aggregated_df = self._apply_aggregations(df)
        
        return aggregated_df
    
    def _build_aggregators(self) -> Dict[str, callable]:
        """Build aggregation functions for each column group"""
        aggregators = {}
        
        for group_name, group in self.column_groups.items():
            if len(group.columns) > 1:
                # Multiple columns need aggregation
                column_names = [col.name for col in group.columns]
                
                if group.aggregation_strategy == AggregationStrategy.LAST:
                    aggregators[group_name] = lambda df, cols=column_names: self._aggregate_last(df, cols)
                elif group.aggregation_strategy == AggregationStrategy.FIRST:
                    aggregators[group_name] = lambda df, cols=column_names: self._aggregate_first(df, cols)
                elif group.aggregation_strategy == AggregationStrategy.SUM:
                    aggregators[group_name] = lambda df, cols=column_names: self._aggregate_sum(df, cols)
                elif group.aggregation_strategy == AggregationStrategy.CONCATENATE:
                    aggregators[group_name] = lambda df, cols=column_names: self._aggregate_concat(df, cols)
        
        return aggregators
    
    def _apply_aggregations(self, df: pl.DataFrame) -> pl.DataFrame:
        """Apply all aggregations to create virtual columns"""
        result_df = df
        
        for group_name, aggregator in self._column_aggregators.items():
            try:
                # Create aggregated column
                aggregated_col = aggregator(df)
                result_df = result_df.with_columns(aggregated_col.alias(f"_agg_{group_name}"))
                logger.debug(f"Created aggregated column: _agg_{group_name}")
            except Exception as e:
                logger.warning(f"Failed to aggregate {group_name}: {str(e)}")
        
        return result_df
    
    def _aggregate_last(self, df: pl.DataFrame, column_names: List[str]) -> pl.Series:
        """Take the last non-null value across columns"""
        # Create a combined column that takes the last non-null value
        result = pl.lit(None)
        
        for col_name in column_names:
            if col_name in df.columns:
                result = pl.when(df[col_name].is_not_null()).then(df[col_name]).otherwise(result)
        
        return result
    
    def _aggregate_first(self, df: pl.DataFrame, column_names: List[str]) -> pl.Series:
        """Take the first non-null value across columns"""
        result = pl.lit(None)
        
        for col_name in reversed(column_names):  # Reverse to get first
            if col_name in df.columns:
                result = pl.when(df[col_name].is_not_null()).then(df[col_name]).otherwise(result)
        
        return result
    
    def _aggregate_sum(self, df: pl.DataFrame, column_names: List[str]) -> pl.Series:
        """Sum numeric values across columns"""
        result = pl.lit(0.0)
        
        for col_name in column_names:
            if col_name in df.columns:
                # Try to cast to float, use 0 if fails
                numeric_col = df[col_name].cast(pl.Float64, strict=False).fill_null(0)
                result = result + numeric_col
        
        return result
    
    def _aggregate_concat(self, df: pl.DataFrame, column_names: List[str]) -> pl.Series:
        """Concatenate non-null values across columns"""
        parts = []
        
        for col_name in column_names:
            if col_name in df.columns:
                parts.append(df[col_name].fill_null(""))
        
        if parts:
            # Join with semicolon separator
            result = parts[0]
            for part in parts[1:]:
                result = result + pl.lit("; ") + part
            return result
        
        return pl.lit("")
    

class EnhancedSprintExtractor:
    """Extract sprints with support for aggregated columns"""
    
    @staticmethod
    def extract_from_dataframe(df: pl.DataFrame, 
                             sprint_column: str,
                             status_column: str,
                             done_statuses: List[str],
                             story_points_column: str) -> Dict[str, Dict[str, float]]:
        """Extract sprint velocities from enhanced dataframe"""
        
        # Check for aggregated sprint column first
        if f"_agg_{sprint_column.lower().replace(' ', '_')}" in df.columns:
            sprint_col = f"_agg_{sprint_column.lower().replace(' ', '_')}"
        else:
            sprint_col = sprint_column
        
        # Filter completed issues
        if "Resolved" in df.columns:
            completed_df = df.filter(
                (pl.col(status_column).is_in(done_statuses)) | 
                (pl.col("Resolved").is_not_null())
            )
        else:
            completed_df = df.filter(
                pl.col(status_column).is_in(done_statuses)
            )
        
        # Group by sprint and calculate velocities
        sprint_velocities = {}
        
        if sprint_col in completed_df.columns and story_points_column in completed_df.columns:
            # Filter to only issues with sprints and story points
            valid_df = completed_df.filter(
                (pl.col(sprint_col).is_not_null()) & 
                (pl.col(story_points_column).is_not_null())
            )
            
            if valid_df.height > 0:
                grouped = valid_df.group_by(sprint_col).agg([
                    pl.col(story_points_column).cast(pl.Float64, strict=False).sum().alias("total_points"),
                    pl.count().alias("issue_count")
                ])
                
                for row in grouped.iter_rows(named=True):
                    sprint_name = row[sprint_col]
                    if sprint_name and str(sprint_name) != "null":
                        sprint_velocities[str(sprint_name)] = {
                            "completed_points": row["total_points"] or 0.0,
                            "issue_count": row["issue_count"]
                        }
                
                logger.info(f"Extracted velocities for {len(sprint_velocities)} sprints from {valid_df.height} issues")
            else:
                logger.warning(f"No valid issues found with both sprint and story points")
        else:
            logger.warning(f"Sprint column '{sprint_col}' or story points column '{story_points_column}' not found")
        
        return sprint_velocities


class VelocityExtractor:
    """Extract velocity data points from issues"""
    
    @staticmethod
    def extract_velocity_data(df: pl.DataFrame,
                            sprint_velocities: Dict[str, Dict[str, float]],
                            resolved_date_column: str) -> List:
        """Extract velocity data points with dates"""
        from ..domain.analysis import VelocityDataPoint
        
        velocity_data = []
        
        # Check if we have sprint and date columns available
        has_sprint_column = "_agg_sprint" in df.columns or "Sprint" in df.columns
        has_date_column = resolved_date_column in df.columns
        
        if has_sprint_column and has_date_column:
            # Try to extract dates from resolved column
            sprint_col = "_agg_sprint" if "_agg_sprint" in df.columns else "Sprint"
            
            for sprint_name, data in sprint_velocities.items():
                # Find the latest resolved date for this sprint
                sprint_issues = df.filter(pl.col(sprint_col).eq(sprint_name))
                
                if len(sprint_issues) > 0:
                    resolved_dates = sprint_issues[resolved_date_column].drop_nulls()
                    
                    if len(resolved_dates) > 0:
                        # Use the latest resolved date as sprint end date
                        latest_date_str = resolved_dates.max()
                        
                        # Parse date (handle various formats)
                        sprint_date = parse_flexible_date(latest_date_str)
                        
                        if sprint_date:
                            velocity_data.append(VelocityDataPoint(
                                sprint_name=sprint_name,
                                sprint_date=sprint_date,
                                completed_points=data["completed_points"],
                                issue_count=data["issue_count"]
                            ))
                        else:
                            logger.warning(f"Could not parse date for sprint {sprint_name}: {latest_date_str}")
        else:
            # No dates available - create synthetic dates based on sprint order
            logger.warning(f"No date column '{resolved_date_column}' found. Using synthetic dates.")
            
            # Sort sprints by name to get chronological order
            # Use natural sort to handle sprint numbers correctly
            import re
            def natural_sort_key(sprint_name):
                # Extract numbers and convert to int for proper sorting
                parts = []
                for part in re.split(r'(\d+)', sprint_name[0]):
                    if part.isdigit():
                        parts.append(int(part))
                    else:
                        parts.append(part)
                return parts
            
            sorted_sprints = sorted(sprint_velocities.items(), key=natural_sort_key)
            
            # Try to detect sprint duration from sprint names
            sprint_duration = detect_sprint_duration(sorted_sprints)
            
            # Create velocity data with synthetic dates
            base_date = datetime.now() - timedelta(days=len(sorted_sprints) * sprint_duration)
            
            for i, (sprint_name, data) in enumerate(sorted_sprints):
                sprint_date = base_date + timedelta(days=i * sprint_duration)
                velocity_data.append(VelocityDataPoint(
                    sprint_name=sprint_name,
                    sprint_date=sprint_date,
                    completed_points=data["completed_points"],
                    issue_count=data["issue_count"]
                ))
        
        # Sort by date
        velocity_data.sort(key=lambda v: v.sprint_date)
        
        return velocity_data


def parse_flexible_date(date_str: Any) -> Optional[datetime]:
    """Parse dates in various formats"""
    if not date_str or str(date_str) == "nan":
        return None
    
    date_str = str(date_str)
    
    # Common Jira date formats
    date_formats = [
        "%d/%b/%y %I:%M %p",    # 13/Jun/25 6:20 AM
        "%d/%b/%Y %I:%M %p",    # 13/Jun/2025 6:20 AM (4-digit year)
        "%Y-%m-%d %H:%M:%S",    # 2025-06-13 18:20:00
        "%Y-%m-%dT%H:%M:%S.%f%z",  # ISO format with timezone
        "%Y-%m-%d",             # Simple date
        "%m/%d/%Y",             # US format
        "%d/%m/%Y",             # EU format
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.split(".")[0], fmt)  # Remove milliseconds if present
        except ValueError:
            continue
    
    # Try pandas parser as fallback
    try:
        import pandas as pd
        return pd.to_datetime(date_str).to_pydatetime()
    except:
        logger.warning(f"Could not parse date: {date_str}")
        return None


def detect_sprint_duration(sprint_data: List[Tuple[str, Dict]]) -> int:
    """Detect sprint duration from sprint names or default to 14 days"""
    import re
    
    # Common patterns for sprint duration
    # Look for patterns like "Sprint 1W", "Sprint 2W", "Sprint 1 Week", etc.
    one_week_patterns = [r'1\s*W(?:eek)?', r'Weekly', r'1Week']
    two_week_patterns = [r'2\s*W(?:eek)?', r'Bi-?weekly', r'2Week', r'Fortnight']
    three_week_patterns = [r'3\s*W(?:eek)?', r'3Week']
    four_week_patterns = [r'4\s*W(?:eek)?', r'Monthly', r'4Week']
    
    for sprint_name, _ in sprint_data:
        # Check for duration indicators in sprint names
        if any(re.search(pattern, sprint_name, re.IGNORECASE) for pattern in one_week_patterns):
            logger.info("Detected 1-week sprints from sprint names")
            return 7
        elif any(re.search(pattern, sprint_name, re.IGNORECASE) for pattern in two_week_patterns):
            logger.info("Detected 2-week sprints from sprint names")
            return 14
        elif any(re.search(pattern, sprint_name, re.IGNORECASE) for pattern in three_week_patterns):
            logger.info("Detected 3-week sprints from sprint names")
            return 21
        elif any(re.search(pattern, sprint_name, re.IGNORECASE) for pattern in four_week_patterns):
            logger.info("Detected 4-week sprints from sprint names")
            return 28
    
    # Default to 2-week sprints (most common in Agile)
    logger.info("Using default 2-week sprint duration")
    return 14