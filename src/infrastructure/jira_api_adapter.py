"""Adapter for Jira API data source to comply with DataSource interface"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..domain.data_sources import DataSource, DataSourceInfo, DataSourceType
from ..domain.entities import Issue, Sprint
from ..domain.exceptions import ValidationError
from ..domain.value_objects import FieldMapping
from .config import JiraConfig
from .jira_api_data_source import JiraApiDataSource

logger = logging.getLogger(__name__)


class JiraApiDataSourceAdapter(DataSource):
    """Adapter for JiraApiDataSource to implement DataSource interface"""

    def __init__(self, field_mapping: Optional[FieldMapping] = None):
        # Field mapping is handled internally by the API
        self.field_mapping = field_mapping or self._get_default_field_mapping()
        self._api_source: Optional[JiraApiDataSource] = None

    def parse_file(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        """
        Parse "file" path which is actually a special URL for API access.

        Expected format: jira-api:// or jira-api://project-key
        """
        path_str = str(file_path)

        # Initialize API source if needed
        if not self._api_source:
            try:
                config = JiraConfig.from_env()

                # Override project key if specified in path
                if path_str.startswith("jira-api://") and len(path_str) > 11:
                    project_key = path_str[11:]
                    if project_key:
                        config.project_key = project_key
                        logger.info(f"Using project key from URL: {project_key}")

                self._api_source = JiraApiDataSource(config)
            except Exception as e:
                raise ValidationError(f"Failed to initialize Jira API: {e}")

        # Fetch data from API
        return self._api_source.parse()

    def detect_format(self, file_path: Path) -> bool:
        """Detect if this is a Jira API "path" """
        path_str = str(file_path)
        # Handle both with and without // (Path strips it)
        return path_str.startswith("jira-api:") or path_str.startswith("jira-api://")

    def get_info(self) -> DataSourceInfo:
        """Get information about this data source"""
        return DataSourceInfo(
            source_type=DataSourceType.JIRA_API,
            name="Jira API",
            description="Direct connection to Jira via REST API",
            file_extensions=["jira-api://"],
            default_field_mapping=self._get_default_field_mapping(),
        )

    def analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze the Jira instance structure"""
        try:
            # Initialize API source
            if not self._api_source:
                config = JiraConfig.from_env()
                self._api_source = JiraApiDataSource(config)

            # Test connection
            connected = self._api_source.test_connection()

            # Get projects
            projects = self._api_source.get_projects() if connected else []

            # Get current project info
            project_info = self._api_source.get_project_info() if connected else None

            # Get field information
            field_info = {}
            if connected and hasattr(self._api_source, "_field_map"):
                self._api_source._initialize_field_mapping()
                field_info = {
                    "total_fields": len(self._api_source._field_map or {}),
                    "custom_fields": self._api_source._custom_field_map or {},
                }

            # Get JQL query
            jql_query = self._api_source.get_jql_query() if self._api_source and connected else None

            return {
                "format": "Jira API",
                "connected": connected,
                "url": self._api_source.config.url if self._api_source else "Not configured",
                "is_cloud": self._api_source.is_cloud if self._api_source else None,
                "project_info": project_info,
                "projects": projects[:10],  # First 10 projects
                "project_count": len(projects),
                "field_info": field_info,
                "configuration": {
                    "has_project_filter": bool(self._api_source.config.project_key) if self._api_source else False,
                    "has_jql_filter": bool(self._api_source.config.jql_filter) if self._api_source else False,
                },
                "jql_query": jql_query,
            }

        except Exception as e:
            logger.error(f"Error analyzing Jira API structure: {e}")
            return {
                "format": "Jira API",
                "error": str(e),
                "connected": False,
            }

    def _get_default_field_mapping(self) -> FieldMapping:
        """Get default field mapping for Jira API"""
        # These are handled internally by the API
        return FieldMapping(
            key_field="key",
            summary_field="summary",
            issue_type_field="issuetype",
            status_field="status",
            created_field="created",
            updated_field="updated",
            resolved_field="resolutiondate",
            story_points_field="customfield_story_points",
            sprint_field="customfield_sprint",
            assignee_field="assignee",
            reporter_field="reporter",
            labels_field="labels",
        )
