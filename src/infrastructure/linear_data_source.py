"""Linear CSV data source implementation"""

import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import polars as pl

from ..domain.data_sources import DataSource, DataSourceInfo, DataSourceType
from ..domain.entities import Issue, IssueStatus, Sprint
from ..domain.value_objects import FieldMapping

logger = logging.getLogger(__name__)


class LinearCSVDataSource(DataSource):
    """Data source for Linear CSV exports"""

    # Linear status to our status mapping
    LINEAR_STATUS_MAPPING = {
        # Todo statuses
        "backlog": IssueStatus.TODO,
        "todo": IssueStatus.TODO,
        "triage": IssueStatus.TODO,
        "icebox": IssueStatus.TODO,
        "planned": IssueStatus.TODO,
        # In Progress statuses
        "in progress": IssueStatus.IN_PROGRESS,
        "in review": IssueStatus.IN_PROGRESS,
        "in development": IssueStatus.IN_PROGRESS,
        "started": IssueStatus.IN_PROGRESS,
        # Done statuses
        "done": IssueStatus.DONE,
        "completed": IssueStatus.DONE,
        "cancelled": IssueStatus.DONE,
        "canceled": IssueStatus.DONE,
        "duplicate": IssueStatus.DONE,
    }

    def __init__(self, field_mapping: Optional[FieldMapping] = None):
        self.field_mapping = field_mapping or self._get_default_field_mapping()

    def parse_file(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        """Parse Linear CSV file and extract issues and sprints"""
        logger.info(f"Parsing Linear CSV file: {file_path}")

        # Read CSV with Polars
        df = pl.read_csv(
            file_path,
            infer_schema_length=10000,
            ignore_errors=True,
            try_parse_dates=True,
        )

        issues = []

        # Map of cycle names to sprint data
        cycles = {}

        for row in df.iter_rows(named=True):
            try:
                issue = self._create_issue_from_row(row)
                if issue:
                    issues.append(issue)

                    # Track cycle/sprint data
                    cycle_name = row.get(self.field_mapping.sprint_field)
                    if cycle_name and cycle_name.strip():
                        if cycle_name not in cycles:
                            cycles[cycle_name] = {
                                "completed_points": 0.0,
                                "start_date": None,
                                "end_date": None,
                            }

                        # If issue is done and has points, add to cycle
                        if self._is_done_status(
                            row.get(self.field_mapping.status_field)
                        ):
                            points = self._parse_estimate(
                                row.get(self.field_mapping.story_points_field)
                            )
                            if points:
                                cycles[cycle_name]["completed_points"] += points

                            # Track cycle dates from completed issues
                            completed_date = self._parse_date(
                                row.get(self.field_mapping.resolved_field)
                            )
                            if completed_date:
                                if (
                                    not cycles[cycle_name]["end_date"]
                                    or completed_date > cycles[cycle_name]["end_date"]
                                ):
                                    cycles[cycle_name]["end_date"] = completed_date
                                if (
                                    not cycles[cycle_name]["start_date"]
                                    or completed_date < cycles[cycle_name]["start_date"]
                                ):
                                    cycles[cycle_name]["start_date"] = completed_date

            except Exception as e:
                logger.warning(f"Error processing row: {str(e)}")
                continue

        # Convert cycles to sprints
        sprints = []
        for cycle_name, cycle_data in cycles.items():
            # Default dates if not found
            start_date = cycle_data["start_date"] or datetime.now()
            end_date = cycle_data["end_date"] or datetime.now()

            sprint = Sprint(
                name=cycle_name,
                start_date=start_date,
                end_date=end_date,
                completed_points=cycle_data["completed_points"],
            )
            sprints.append(sprint)

        # If no cycles found, try to create synthetic sprints from monthly data
        if not sprints and issues:
            logger.info(
                "No cycles found, creating synthetic monthly sprints from completed work"
            )
            monthly_sprints = self._create_monthly_sprints(issues)
            sprints.extend(monthly_sprints)

        logger.info(f"Parsed {len(issues)} issues and {len(sprints)} cycles/sprints")
        return issues, sprints

    def detect_format(self, file_path: Path) -> bool:
        """Detect if this is a Linear CSV file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                headers = next(reader)

                # Look for typical Linear fields
                linear_indicators = [
                    "ID",
                    "Title",
                    "Status",
                    "Priority",
                    "Estimate",
                    "Assignee",
                    "Labels",
                    "Created",
                    "Updated",
                    "Completed",
                    "Cycle",
                    "Project",
                    "Team",
                    "Parent",
                    "URL",
                    "Lead Time",
                    "Cycle Time",
                ]

                # Count matches
                matches = sum(
                    1
                    for field in linear_indicators
                    if any(field.lower() == h.lower() for h in headers)
                )

                # Linear has very specific field names
                return matches >= 5

        except Exception as e:
            logger.debug(f"Error detecting Linear format: {e}")
            return False

    def get_info(self) -> DataSourceInfo:
        """Get information about this data source"""
        return DataSourceInfo(
            source_type=DataSourceType.LINEAR_CSV,
            name="Linear CSV Export",
            description="CSV export from Linear with issue and cycle data",
            file_extensions=[".csv"],
            default_field_mapping=self._get_default_field_mapping(),
        )

    def analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Linear CSV structure"""
        try:
            df = pl.read_csv(file_path, n_rows=100)  # Sample first 100 rows

            # Get unique values for key fields
            status_values = []
            cycle_values = []

            if self.field_mapping.status_field in df.columns:
                status_values = (
                    df[self.field_mapping.status_field].unique().drop_nulls().to_list()
                )

            if self.field_mapping.sprint_field in df.columns:
                cycle_values = (
                    df[self.field_mapping.sprint_field].unique().drop_nulls().to_list()
                )

            return {
                "total_rows": df.height,
                "total_columns": len(df.columns),
                "columns": df.columns,
                "status_values": status_values,
                "cycle_values": cycle_values,
                "has_estimates": "Estimate" in df.columns,
                "has_cycles": "Cycle" in df.columns,
                "sample_data": df.head(5).to_dicts(),
            }
        except Exception as e:
            logger.error(f"Error analyzing Linear CSV: {e}")
            return {"error": str(e)}

    def _create_issue_from_row(self, row: Dict[str, Any]) -> Optional[Issue]:
        """Create an Issue from a Linear CSV row"""
        try:
            # Extract basic fields
            key = str(row.get(self.field_mapping.key_field, ""))
            if not key:
                return None

            summary = str(row.get(self.field_mapping.summary_field, ""))
            status = str(row.get(self.field_mapping.status_field, ""))

            # Parse dates
            created = self._parse_date(row.get(self.field_mapping.created_field))
            updated = self._parse_date(row.get("Updated"))
            resolved = self._parse_date(row.get(self.field_mapping.resolved_field))

            # Parse estimate (Linear uses T-shirt sizes or numeric)
            story_points = self._parse_estimate(
                row.get(self.field_mapping.story_points_field)
            )

            # Use default value of 1 if no estimate provided and issue is not done
            if story_points is None and not self._is_done_status(status):
                story_points = 1.0

            # Extract other fields
            assignee = str(row.get(self.field_mapping.assignee_field, ""))
            reporter = str(
                row.get("Creator", "")
            )  # Linear uses Creator instead of Reporter
            issue_type = str(
                row.get("Type", "Issue")
            )  # Linear has different issue types

            # Parse labels
            labels = []
            labels_str = str(row.get(self.field_mapping.labels_field, ""))
            if labels_str:
                labels = [label.strip() for label in labels_str.split(",")]

            # Store Linear-specific fields in custom_fields
            custom_fields = {
                "cycle": row.get("Cycle"),
                "project": row.get("Project"),
                "team": row.get("Team"),
                "priority": row.get("Priority"),
                "parent": row.get("Parent"),
                "url": row.get("URL"),
                "lead_time": row.get("Lead Time"),
                "cycle_time": row.get("Cycle Time"),
            }

            return Issue(
                key=key,
                summary=summary,
                issue_type=issue_type,
                status=status,
                created=created or datetime.now(),
                updated=updated,
                resolved=resolved,
                story_points=story_points,
                assignee=assignee,
                reporter=reporter,
                labels=labels,
                custom_fields={k: v for k, v in custom_fields.items() if v is not None},
            )

        except Exception as e:
            logger.warning(f"Error creating issue from row: {e}")
            return None

    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse Linear date format"""
        if not date_value:
            return None

        if isinstance(date_value, datetime):
            return date_value

        date_str = str(date_value)

        # Linear date formats
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                # If the format includes 'Z', it's UTC - make it timezone-naive for consistency
                if date_str.endswith("Z"):
                    return parsed_date.replace(tzinfo=None)
                return parsed_date
            except ValueError:
                continue

        logger.debug(f"Could not parse date: {date_str}")
        return None

    def _parse_estimate(self, estimate_value: Any) -> Optional[float]:
        """Parse Linear estimate (numeric or T-shirt size)"""
        if not estimate_value:
            return None

        estimate_str = str(estimate_value).strip().upper()

        # Try numeric first
        try:
            return float(estimate_str)
        except ValueError:
            pass

        # T-shirt size mapping
        tshirt_mapping = {
            "XS": 1.0,
            "S": 2.0,
            "M": 3.0,
            "L": 5.0,
            "XL": 8.0,
            "XXL": 13.0,
        }

        return tshirt_mapping.get(estimate_str)

    def _is_done_status(self, status: str) -> bool:
        """Check if status is considered done"""
        if not status:
            return False

        status_lower = status.lower()
        return self.LINEAR_STATUS_MAPPING.get(status_lower) == IssueStatus.DONE

    def _get_default_field_mapping(self) -> FieldMapping:
        """Get default field mapping for Linear"""
        return FieldMapping(
            key_field="ID",
            summary_field="Title",
            status_field="Status",
            created_field="Created",
            resolved_field="Completed",  # Linear uses Completed instead of Resolved
            story_points_field="Estimate",
            sprint_field="Cycle Name",  # Linear uses Cycles instead of Sprints
            assignee_field="Assignee",
            reporter_field="Creator",  # Linear uses Creator
            issue_type_field="Type",
            labels_field="Labels",
            time_estimate_field="Estimate",  # Same as story points in Linear
            time_spent_field=None,  # Linear doesn't track time spent in CSV
        )

    def _create_monthly_sprints(self, issues: List[Issue]) -> List[Sprint]:
        """Create synthetic monthly sprints from completed issues"""
        import calendar
        from collections import defaultdict

        monthly_data = defaultdict(
            lambda: {
                "completed_points": 0.0,
                "completed_issues": [],
                "start_date": None,
                "end_date": None,
            }
        )

        # Group completed issues by month
        for issue in issues:
            if issue.resolved and self._is_done_status(issue.status):
                # Create month key
                month_key = issue.resolved.strftime("%Y-%m")

                # Add points if available
                if issue.story_points:
                    monthly_data[month_key]["completed_points"] += issue.story_points

                monthly_data[month_key]["completed_issues"].append(issue)

                # Track date range
                if (
                    not monthly_data[month_key]["start_date"]
                    or issue.resolved < monthly_data[month_key]["start_date"]
                ):
                    # Set to first day of month
                    monthly_data[month_key]["start_date"] = issue.resolved.replace(
                        day=1
                    )

                if (
                    not monthly_data[month_key]["end_date"]
                    or issue.resolved > monthly_data[month_key]["end_date"]
                ):
                    # Set to last day of month
                    last_day = calendar.monthrange(
                        issue.resolved.year, issue.resolved.month
                    )[1]
                    monthly_data[month_key]["end_date"] = issue.resolved.replace(
                        day=last_day
                    )

        # Create sprints from monthly data
        sprints = []
        for month_key, data in sorted(monthly_data.items()):
            # Create sprint if there are any completed issues (for count-based velocity)
            if data["completed_issues"]:
                sprint = Sprint(
                    name=f"Month {month_key}",
                    start_date=data["start_date"],
                    end_date=data["end_date"],
                    completed_points=data["completed_points"],
                    completed_issues=data["completed_issues"],
                )
                sprints.append(sprint)

        return sprints
