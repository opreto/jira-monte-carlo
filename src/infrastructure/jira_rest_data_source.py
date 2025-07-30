"""Jira REST API data source implementation"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..domain.data_sources import DataSource, DataSourceInfo, DataSourceType
from ..domain.entities import Issue, Sprint
from ..domain.value_objects import FieldMapping

logger = logging.getLogger(__name__)


class JiraRESTDataSource(DataSource):
    """Data source for Jira REST API"""

    def __init__(
        self,
        base_url: str,
        auth_token: str,
        field_mapping: Optional[FieldMapping] = None,
    ):
        """
        Initialize Jira REST data source

        Args:
            base_url: Jira instance base URL (e.g., https://company.atlassian.net)
            auth_token: Authentication token or API key
            field_mapping: Optional field mapping override
        """
        self.base_url = base_url.rstrip("/")
        self.auth_token = auth_token
        self.field_mapping = field_mapping
        self._session = None

    def get_info(self) -> DataSourceInfo:
        """Get information about this data source"""
        return DataSourceInfo(
            type=DataSourceType.JIRA_REST,
            name="Jira REST API",
            description="Direct integration with Jira via REST API",
            supported_features=[
                "real-time data",
                "sprint data",
                "custom fields",
                "attachments",
                "comments",
                "history",
            ],
            file_extensions=[],  # No files, uses API
        )

    def detect_format(self, file_path: Path) -> bool:
        """
        Detect if the 'file_path' is actually a Jira project key or URL

        Args:
            file_path: Path that might contain project key or URL

        Returns:
            True if this looks like a Jira REST endpoint
        """
        path_str = str(file_path)

        # Check if it's a URL pointing to Jira
        if path_str.startswith(("http://", "https://")) and "atlassian.net" in path_str:
            return True

        # Check if it's a project key (e.g., "PROJ-123" or just "PROJ")
        if path_str.isupper() and (len(path_str) <= 10 or "-" in path_str):
            return True

        return False

    def parse(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        """
        Parse data from Jira REST API

        Args:
            file_path: Project key or URL to fetch data from

        Returns:
            Tuple of (issues, sprints)
        """
        project_key = self._extract_project_key(file_path)

        # Initialize session if needed
        if not self._session:
            self._init_session()

        # Fetch issues
        issues = self._fetch_all_issues(project_key)

        # Fetch sprints
        sprints = self._fetch_all_sprints(project_key)

        return issues, sprints

    def analyze(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Jira project structure"""
        project_key = self._extract_project_key(file_path)

        # Get project metadata
        project_info = self._fetch_project_info(project_key)

        # Get field information
        fields = self._fetch_custom_fields()

        # Get statuses
        statuses = self._fetch_statuses(project_key)

        return {
            "project_key": project_key,
            "project_name": project_info.get("name", "Unknown"),
            "total_issues": project_info.get("insight", {}).get("totalIssueCount", 0),
            "custom_fields": [f["name"] for f in fields],
            "statuses": statuses,
            "has_sprints": self._check_agile_enabled(project_key),
        }

    def get_default_field_mapping(self) -> FieldMapping:
        """Get default field mapping for Jira REST API"""
        return FieldMapping(
            key_field="key",
            summary_field="fields.summary",
            issue_type_field="fields.issuetype.name",
            status_field="fields.status.name",
            created_field="fields.created",
            updated_field="fields.updated",
            resolved_field="fields.resolutiondate",
            story_points_field="fields.customfield_10016",  # Common story points field
            time_estimate_field="fields.timeoriginalestimate",
            time_spent_field="fields.timespent",
            assignee_field="fields.assignee.displayName",
            reporter_field="fields.reporter.displayName",
            labels_field="fields.labels",
            sprint_field="fields.customfield_10020",  # Common sprint field
        )

    def get_default_status_mapping(self) -> Dict[str, List[str]]:
        """Get default status mapping for Jira"""
        return {
            "done": ["Done", "Closed", "Resolved", "Released", "Completed"],
            "in_progress": ["In Progress", "In Development", "In Review", "In Testing"],
            "todo": ["To Do", "Open", "Backlog", "Selected for Development", "Ready"],
        }

    # Private helper methods
    def _init_session(self):
        """Initialize HTTP session with authentication"""
        import requests

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _extract_project_key(self, file_path: Path) -> str:
        """Extract project key from file path"""
        path_str = str(file_path)

        # If it's a URL, extract project key from it
        if path_str.startswith(("http://", "https://")):
            # Simple extraction - in reality would be more robust
            parts = path_str.split("/")
            for part in parts:
                if part.isupper() and len(part) <= 10:
                    return part

        # Otherwise assume it's the project key directly
        return path_str.upper()

    def _fetch_all_issues(self, project_key: str) -> List[Issue]:
        """Fetch all issues for a project"""
        # This would implement pagination and convert Jira issues to domain Issues
        # Simplified for example
        logger.info(f"Fetching issues for project {project_key}")

        # In reality, this would make API calls
        # For now, return empty list to show structure
        return []

    def _fetch_all_sprints(self, project_key: str) -> List[Sprint]:
        """Fetch all sprints for a project"""
        logger.info(f"Fetching sprints for project {project_key}")

        # Would use Jira Agile API
        return []

    def _fetch_project_info(self, project_key: str) -> Dict[str, Any]:
        """Fetch project information"""
        # GET /rest/api/3/project/{projectKey}
        return {}

    def _fetch_custom_fields(self) -> List[Dict[str, Any]]:
        """Fetch custom field definitions"""
        # GET /rest/api/3/field
        return []

    def _fetch_statuses(self, project_key: str) -> List[str]:
        """Fetch available statuses for project"""
        # GET /rest/api/3/project/{projectKey}/statuses
        return []

    def _check_agile_enabled(self, project_key: str) -> bool:
        """Check if project has agile boards"""
        # GET /rest/agile/1.0/board?projectKeyOrId={projectKey}
        return True
