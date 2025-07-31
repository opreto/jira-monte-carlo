import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..domain.entities import Issue, Sprint
from ..domain.repositories import ConfigRepository, IssueRepository, SprintRepository
from ..domain.value_objects import DateRange, FieldMapping

logger = logging.getLogger(__name__)


class InMemoryIssueRepository(IssueRepository):
    def __init__(self):
        self.issues: List[Issue] = []
        self._issues_by_status: Dict[str, List[Issue]] = {}

    def add_issues(self, issues: List[Issue]) -> None:
        self.issues = issues
        # Build status index
        self._issues_by_status.clear()
        for issue in issues:
            if issue.status not in self._issues_by_status:
                self._issues_by_status[issue.status] = []
            self._issues_by_status[issue.status].append(issue)

    def save_all(self, issues: List[Issue]) -> None:
        """Alias for add_issues to match the use case expectations"""
        self.add_issues(issues)

    def get_all(self) -> List[Issue]:
        return self.issues

    def get_by_status(self, status: str) -> List[Issue]:
        return self._issues_by_status.get(status, [])

    def get_by_date_range(self, date_range: DateRange) -> List[Issue]:
        return [issue for issue in self.issues if date_range.contains(issue.created)]

    def get_completed_in_range(self, date_range: DateRange) -> List[Issue]:
        return [issue for issue in self.issues if issue.resolved and date_range.contains(issue.resolved)]


class InMemorySprintRepository(SprintRepository):
    def __init__(self):
        self.sprints: List[Sprint] = []

    def add_sprints(self, sprints: List[Sprint]) -> None:
        # Add new sprints to existing ones
        self.sprints.extend(sprints)
        # Sort by start_date, handling None values
        self.sprints = sorted(self.sprints, key=lambda s: s.start_date if s.start_date else datetime.min)

    def get_all(self) -> List[Sprint]:
        return self.sprints

    def get_by_date_range(self, date_range: DateRange) -> List[Sprint]:
        return [
            sprint
            for sprint in self.sprints
            if date_range.contains(sprint.start_date) or date_range.contains(sprint.end_date)
        ]

    def get_last_n_sprints(self, n: int) -> List[Sprint]:
        # Handle timezone-aware comparisons
        now = datetime.now()
        completed_sprints = []
        for sprint in self.sprints:
            if sprint.end_date:
                # Make both dates timezone-naive for comparison
                end_date = sprint.end_date.replace(tzinfo=None) if sprint.end_date.tzinfo else sprint.end_date
                now_naive = now.replace(tzinfo=None)
                if end_date < now_naive:
                    completed_sprints.append(sprint)
        return completed_sprints[-n:] if len(completed_sprints) >= n else completed_sprints


class FileConfigRepository(ConfigRepository):
    def __init__(self, config_dir: Path = Path.home() / ".jira-monte-carlo"):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self.field_mapping_file = self.config_dir / "field_mapping.json"
        self.status_mapping_file = self.config_dir / "status_mapping.json"

    def save_field_mapping(self, mapping: FieldMapping) -> None:
        try:
            with open(self.field_mapping_file, "w") as f:
                json.dump(mapping.to_dict(), f, indent=2)
            logger.info(f"Saved field mapping to {self.field_mapping_file}")
        except Exception as e:
            logger.error(f"Error saving field mapping: {str(e)}")
            raise

    def load_field_mapping(self) -> Optional[FieldMapping]:
        if not self.field_mapping_file.exists():
            return None

        try:
            with open(self.field_mapping_file, "r") as f:
                data = json.load(f)
            return FieldMapping(**data)
        except Exception as e:
            logger.error(f"Error loading field mapping: {str(e)}")
            return None

    def save_status_mapping(self, status_mapping: Dict[str, List[str]]) -> None:
        try:
            with open(self.status_mapping_file, "w") as f:
                json.dump(status_mapping, f, indent=2)
            logger.info(f"Saved status mapping to {self.status_mapping_file}")
        except Exception as e:
            logger.error(f"Error saving status mapping: {str(e)}")
            raise

    def load_status_mapping(self) -> Optional[Dict[str, List[str]]]:
        if not self.status_mapping_file.exists():
            return None

        try:
            with open(self.status_mapping_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading status mapping: {str(e)}")
            return None


class SprintExtractor:
    @staticmethod
    def extract_sprints_from_issues(issues: List[Issue], sprint_field: str, done_statuses: List[str]) -> List[Sprint]:
        sprint_issues: Dict[str, List[Issue]] = {}

        # Group issues by sprint
        for issue in issues:
            if issue.status in done_statuses or issue.resolved:
                # First check for the _last_sprint custom field (from multiple Sprint columns)
                sprint_name = issue.custom_fields.get("_last_sprint")

                # Fallback to regular sprint field lookup
                if not sprint_name:
                    sprint_name = issue.custom_fields.get(sprint_field, "No Sprint")

                if sprint_name and sprint_name != "None" and sprint_name != "No Sprint":
                    # Handle multiple sprints (Jira can have comma-separated sprints)
                    sprint_names = [s.strip() for s in str(sprint_name).split(",")]
                    for name in sprint_names:
                        if name not in sprint_issues:
                            sprint_issues[name] = []
                        sprint_issues[name].append(issue)

        # Create Sprint objects
        sprints = []
        for sprint_name, issues in sprint_issues.items():
            if not issues:
                continue

            # Estimate sprint dates from issue resolved dates
            resolved_dates = [i.resolved for i in issues if i.resolved]
            if not resolved_dates:
                continue

            end_date = max(resolved_dates)
            start_date = min(resolved_dates)

            # Calculate completed points
            completed_points = sum(issue.story_points for issue in issues if issue.story_points is not None)

            sprint = Sprint(
                name=sprint_name,
                start_date=start_date,
                end_date=end_date,
                completed_points=completed_points,
                completed_issues=issues,
            )
            sprints.append(sprint)

        return sorted(sprints, key=lambda s: s.start_date)
