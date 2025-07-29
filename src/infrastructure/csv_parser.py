import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set

import polars as pl

from ..domain.entities import Issue
from ..domain.value_objects import FieldMapping

logger = logging.getLogger(__name__)


class JiraCSVParser:
    def __init__(self, field_mapping: FieldMapping):
        self.field_mapping = field_mapping

    def parse_dataframe(self, df: pl.DataFrame) -> List[Issue]:
        """Parse issues from a pre-processed DataFrame"""
        logger.info(f"Parsing DataFrame with {df.height} rows")

        issues = []
        for row in df.iter_rows(named=True):
            try:
                issue = self._create_issue_from_row(row)
                if issue:
                    issues.append(issue)
            except Exception as e:
                logger.warning(f"Error processing row: {str(e)}")
                continue

        logger.info(f"Successfully parsed {len(issues)} issues")
        return issues

    def parse_file(self, file_path: Path, batch_size: int = 10000) -> List[Issue]:
        logger.info(f"Parsing CSV file: {file_path}")

        # Use Polars for high-performance CSV reading
        try:
            # Read CSV with Polars lazy evaluation for memory efficiency
            df = pl.scan_csv(file_path, infer_schema_length=10000, ignore_errors=True, truncate_ragged_lines=True)

            # Select only needed columns
            needed_columns = self._get_needed_columns()
            available_columns = df.columns

            columns_to_select = [col for col in needed_columns if col in available_columns]
            df = df.select(columns_to_select)

            # Process in batches
            issues = []
            offset = 0

            while True:
                batch_df = df.slice(offset, batch_size).collect()

                if batch_df.height == 0:
                    break

                batch_issues = self._process_batch(batch_df)
                issues.extend(batch_issues)

                offset += batch_size
                logger.info(f"Processed {offset} rows")

                if batch_df.height < batch_size:
                    break

            logger.info(f"Successfully parsed {len(issues)} issues")
            return issues

        except Exception as e:
            logger.error(f"Error parsing CSV: {str(e)}")
            raise

    def _get_needed_columns(self) -> Set[str]:
        mapping_dict = self.field_mapping.to_dict()
        return set(mapping_dict.values())

    def _process_batch(self, df: pl.DataFrame) -> List[Issue]:
        issues = []

        for row in df.iter_rows(named=True):
            try:
                issue = self._create_issue_from_row(row)
                if issue:
                    issues.append(issue)
            except Exception as e:
                logger.warning(f"Error processing row: {str(e)}")
                continue

        return issues

    def _create_issue_from_row(self, row: Dict) -> Optional[Issue]:
        try:
            # Parse dates
            created = self._parse_date(row.get(self.field_mapping.created_field))
            if not created:
                # Use a default date if created field is missing
                # This will be detected by capability analyzer as fake data
                created = datetime.now() - timedelta(days=365)  # Default to 1 year ago

            updated = self._parse_date(row.get(self.field_mapping.updated_field))
            resolved = self._parse_date(row.get(self.field_mapping.resolved_field))

            # Parse numeric fields
            story_points = (
                self._parse_float(row.get(self.field_mapping.story_points_field))
                if self.field_mapping.story_points_field
                else None
            )

            time_estimate = (
                self._parse_float(row.get(self.field_mapping.time_estimate_field))
                if self.field_mapping.time_estimate_field
                else None
            )

            time_spent = (
                self._parse_float(row.get(self.field_mapping.time_spent_field))
                if self.field_mapping.time_spent_field
                else None
            )

            # Parse labels
            labels = self._parse_labels(row.get(self.field_mapping.labels_field, ""))

            # Extract custom fields (including sprint data)
            custom_fields = self._extract_custom_fields(row)

            # For Sprint field, check all columns named "Sprint" and use the last non-empty one
            sprint_value = None
            if self.field_mapping.sprint_field:
                # Look for all keys that match the sprint field name
                sprint_values = []
                for key, value in row.items():
                    if key == self.field_mapping.sprint_field and value and str(value).strip():
                        sprint_values.append(str(value).strip())

                # Use the last sprint value (most recent)
                if sprint_values:
                    sprint_value = sprint_values[-1]
                    custom_fields["_last_sprint"] = sprint_value

            # Create issue
            issue = Issue(
                key=str(row.get(self.field_mapping.key_field, "")),
                summary=str(row.get(self.field_mapping.summary_field, "")),
                issue_type=str(row.get(self.field_mapping.issue_type_field, "")),
                status=str(row.get(self.field_mapping.status_field, "")),
                created=created,
                updated=updated,
                resolved=resolved,
                story_points=story_points,
                time_estimate=time_estimate,
                time_spent=time_spent,
                assignee=str(row.get(self.field_mapping.assignee_field, "")),
                reporter=str(row.get(self.field_mapping.reporter_field, "")),
                labels=labels,
                custom_fields=custom_fields,
            )

            return issue

        except Exception as e:
            logger.warning(f"Error creating issue: {str(e)}")
            return None

    def _parse_date(self, value: Optional[str]) -> Optional[datetime]:
        if not value or value == "" or value == "None":
            return None

        # Try common Jira date formats
        date_formats = [
            "%d/%b/%y %I:%M %p",  # 13/Jun/25 6:20 AM
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%d",
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(str(value), fmt)
            except ValueError:
                continue

        return None

    def _parse_float(self, value: Optional[str]) -> Optional[float]:
        if not value or value == "" or value == "None":
            return None

        try:
            # Handle time formats like "3d 4h"
            if isinstance(value, str) and ("d" in value or "h" in value):
                total_hours = 0.0
                parts = value.split()
                for part in parts:
                    if "d" in part:
                        days = float(part.replace("d", ""))
                        total_hours += days * 8  # Assume 8-hour workday
                    elif "h" in part:
                        hours = float(part.replace("h", ""))
                        total_hours += hours
                return total_hours

            return float(value)
        except (ValueError, TypeError):
            return None

    def _parse_labels(self, value: str) -> List[str]:
        if not value:
            return []

        # Handle comma-separated labels
        labels = [label.strip() for label in str(value).split(",")]
        return [label for label in labels if label]

    def _extract_custom_fields(self, row: Dict) -> Dict[str, str]:
        custom_fields = {}

        for key, value in row.items():
            if key.startswith("Custom field"):
                field_name = key.replace("Custom field (", "").replace(")", "")
                if value and str(value) != "None":
                    custom_fields[field_name] = str(value)

        return custom_fields


class CSVFieldAnalyzer:
    @staticmethod
    def analyze_headers(file_path: Path) -> Dict[str, List[str]]:
        # Read just the headers
        df = pl.read_csv(file_path, n_rows=0)
        headers = df.columns

        # Categorize headers
        categorized = {
            "key_candidates": [],
            "summary_candidates": [],
            "status_candidates": [],
            "date_candidates": [],
            "numeric_candidates": [],
            "user_candidates": [],
            "sprint_candidates": [],
            "custom_fields": [],
        }

        for header in headers:
            header_lower = header.lower()

            # Key candidates
            if "key" in header_lower or "id" in header_lower:
                categorized["key_candidates"].append(header)

            # Summary candidates
            if "summary" in header_lower or "title" in header_lower or "name" in header_lower:
                categorized["summary_candidates"].append(header)

            # Status candidates
            if "status" in header_lower or "state" in header_lower:
                categorized["status_candidates"].append(header)

            # Date candidates
            if any(word in header_lower for word in ["date", "created", "updated", "resolved", "time"]):
                categorized["date_candidates"].append(header)

            # Numeric candidates (for velocity)
            if any(word in header_lower for word in ["points", "estimate", "effort", "size", "hours"]):
                categorized["numeric_candidates"].append(header)

            # User candidates
            if any(word in header_lower for word in ["assignee", "reporter", "owner", "user"]):
                categorized["user_candidates"].append(header)

            # Sprint candidates
            if "sprint" in header_lower:
                categorized["sprint_candidates"].append(header)

            # Custom fields
            if header.startswith("Custom field"):
                categorized["custom_fields"].append(header)

        return categorized
