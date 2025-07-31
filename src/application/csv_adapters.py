"""Adapters to bridge infrastructure implementations with domain interfaces"""

from datetime import datetime
from typing import Dict, List

import pandas as pd

from ..domain.csv_processing import SprintExtractor
from ..domain.entities import Issue, Sprint
from ..domain.value_objects import FieldMapping


class EnhancedSprintExtractorAdapter(SprintExtractor):
    """
    Adapter that wraps the infrastructure EnhancedSprintExtractor to comply with
    the domain SprintExtractor interface.
    """

    def __init__(
        self, status_mapping: Dict[str, List[str]], field_mapping: FieldMapping
    ):
        """
        Initialize with dependencies needed by the infrastructure implementation.

        Args:
            status_mapping: Mapping of status categories to actual statuses
            field_mapping: Field mapping configuration
        """
        self.status_mapping = status_mapping
        self.field_mapping = field_mapping

    def extract_from_issues(self, issues: List[Issue]) -> List[Sprint]:
        """Extract sprint information from issues"""
        # Group issues by sprint
        sprints_data = {}

        for issue in issues:
            sprint_names = issue.custom_fields.get("sprint", [])
            if not sprint_names:
                continue

            for sprint_name in sprint_names:
                if sprint_name not in sprints_data:
                    sprints_data[sprint_name] = {
                        "name": sprint_name,
                        "completed_points": 0,
                        "total_points": 0,
                        "completed_issues": [],
                        "total_issues": [],
                    }

                sprints_data[sprint_name]["total_issues"].append(issue)
                if issue.story_points:
                    sprints_data[sprint_name]["total_points"] += issue.story_points

                if issue.status in self.status_mapping.get("done", []):
                    sprints_data[sprint_name]["completed_issues"].append(issue)
                    if issue.story_points:
                        sprints_data[sprint_name]["completed_points"] += (
                            issue.story_points
                        )

        # Convert to Sprint entities
        sprints = []
        for sprint_name, data in sprints_data.items():
            # Try to infer dates from issues
            start_date = None
            end_date = None

            if data["total_issues"]:
                # Use earliest created date as approximate start
                start_date = min(issue.created for issue in data["total_issues"])

            if data["completed_issues"]:
                # Use latest resolved date as approximate end
                resolved_dates = [
                    issue.resolved
                    for issue in data["completed_issues"]
                    if issue.resolved
                ]
                if resolved_dates:
                    end_date = max(resolved_dates)

            sprint = Sprint(
                name=sprint_name,
                start_date=start_date or datetime.now(),
                end_date=end_date or datetime.now(),
                completed_points=data["completed_points"],
                committed_points=data["total_points"],  # Approximation
            )
            sprints.append(sprint)

        return sorted(sprints, key=lambda s: s.name)

    def extract_from_dataframe(
        self, df: pd.DataFrame, sprint_field: str, velocity_field: str = "Story Points"
    ) -> List[Sprint]:
        """
        Extract sprint information directly from DataFrame.

        This adapter method converts the infrastructure call to match the interface.
        """
        # Import here to avoid circular dependency
        # Convert pandas to polars as expected by infrastructure
        import polars as pl

        from ..infrastructure.csv_analyzer import EnhancedSprintExtractor

        df_polars = pl.from_pandas(df)

        # Call the infrastructure implementation with required parameters
        sprint_velocities = EnhancedSprintExtractor.extract_from_dataframe(
            df_polars,
            sprint_field,
            self.field_mapping.status_field,
            self.status_mapping.get("done", []),
            self.field_mapping.story_points_field or velocity_field,
        )

        # Convert the dictionary result to Sprint entities
        sprints = []
        for sprint_name, metrics in sprint_velocities.items():
            sprint = Sprint(
                name=sprint_name,
                start_date=datetime.now(),  # Would need actual dates
                end_date=datetime.now(),  # Would need actual dates
                completed_points=metrics.get("completed_points", 0),
                committed_points=metrics.get(
                    "committed_points", metrics.get("completed_points", 0)
                ),
            )
            sprints.append(sprint)

        return sorted(sprints, key=lambda s: s.name)
