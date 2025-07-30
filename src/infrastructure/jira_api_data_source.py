"""Jira API data source implementation"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests
from atlassian import Jira
from requests.auth import HTTPBasicAuth

from ..domain.entities import Issue, Sprint
from ..domain.exceptions import ProcessingError
from .cache import APICache
from .config import JiraConfig

logger = logging.getLogger(__name__)


class JiraApiDataSource:
    """
    Data source for fetching data from Jira API.

    Uses the atlassian-python-api library for robust API interaction.
    Supports both Jira Cloud and Server instances.
    """

    def __init__(
        self, config: Optional[JiraConfig] = None, cache_ttl_hours: float = 1.0
    ):
        """
        Initialize Jira API connection.

        Args:
            config: JiraConfig object. If None, will load from environment.
            cache_ttl_hours: Cache time-to-live in hours. Default is 1 hour.
        """
        self.config = config or JiraConfig.from_env()
        self.config.validate()

        # Determine if this is a cloud instance
        self.is_cloud = "atlassian.net" in self.config.url

        # Initialize Jira client
        self.jira = Jira(
            url=self.config.url,
            username=self.config.username,
            password=self.config.api_token,
            cloud=self.is_cloud,
        )

        # Cache for field metadata
        self._field_map: Optional[Dict[str, str]] = None
        self._custom_field_map: Optional[Dict[str, str]] = None

        # Initialize API cache
        self.cache = APICache(ttl_hours=cache_ttl_hours)

        # Store project info
        self._project_info: Optional[Dict[str, str]] = None

    def parse(self) -> Tuple[List[Issue], List[Sprint]]:
        """
        Fetch issues and sprints from Jira API.

        Returns:
            Tuple of (issues, sprints)
        """
        try:
            # Build JQL query
            jql = self._build_jql_query()
            logger.info(f"Fetching issues with JQL: {jql}")

            # Create cache key based on JQL and project
            # Use hash for long JQL queries to avoid filesystem path length limits
            import hashlib

            jql_hash = hashlib.sha256(jql.encode()).hexdigest()[:16]
            cache_key = f"jira_issues_{self.config.url.replace('https://', '').replace('/', '_')}_{jql_hash}"

            # Check cache first
            cached_data = self.cache.get(cache_key)
            if cached_data is not None:
                logger.info("Using cached Jira data")
                issues = cached_data["issues"]
                sprints = cached_data["sprints"]
                return issues, sprints

            # Fetch issues from API
            logger.info("Cache miss, fetching from Jira API")
            issues = self._fetch_all_issues(jql)
            logger.info(f"Fetched {len(issues)} issues from Jira")

            # Extract sprints from issues
            sprints = self._extract_sprints(issues)
            logger.info(f"Extracted {len(sprints)} sprints from issues")

            # Cache the results
            self.cache.set(cache_key, {"issues": issues, "sprints": sprints})

            return issues, sprints

        except Exception as e:
            if hasattr(e, "response") and hasattr(e.response, "status_code"):
                logger.error(f"Jira API error (status {e.response.status_code}): {e}")
            else:
                logger.error(f"Jira API error: {e}")
            raise ProcessingError(f"Failed to fetch data from Jira: {e}")

    def _build_jql_query(self) -> str:
        """Build JQL query based on configuration"""
        if self.config.jql_filter:
            return self.config.jql_filter

        # Build default query
        parts = []

        if self.config.project_key:
            parts.append(f"project = {self.config.project_key}")

        # Don't add time restriction by default - get all issues
        # parts.append("created >= -26w")

        # Order by created date
        if parts:
            jql = " AND ".join(parts)
        else:
            # If no filters specified, get recent issues as fallback
            jql = "created >= -26w"
        jql += " ORDER BY created DESC"

        return jql

    def _fetch_all_issues(self, jql: str) -> List[Issue]:
        """
        Fetch all issues matching the JQL query.

        Handles pagination automatically for both Cloud and Server.
        """
        issues = []

        # Initialize field mapping
        if not self._field_map:
            self._initialize_field_mapping()

        if self.is_cloud:
            # Use token-based pagination for Jira Cloud
            logger.info("Using token-based pagination for Jira Cloud")
            next_page_token = None
            page_num = 0

            while True:
                page_num += 1
                logger.info(f"Fetching page {page_num}...")

                # Calculate start position
                start = (page_num - 1) * 100

                # Use direct REST API call for reliable pagination
                try:
                    # The jql method should work with start parameter
                    result = self.jira.jql(
                        jql, start=start, limit=100, expand="changelog"
                    )
                except ValueError as e:
                    if "deprecated" in str(e) and page_num == 1:
                        # Try enhanced_jql only for first page to see if it works
                        logger.info(
                            "JQL deprecated, trying enhanced_jql for first batch"
                        )
                        result = self.jira.enhanced_jql(jql)
                        batch_issues = result.get("issues", [])
                        if batch_issues:
                            issues.extend(self._parse_issues(batch_issues))
                            logger.info(
                                f"Enhanced JQL returned {len(batch_issues)} issues"
                            )
                        # Enhanced JQL has limits, continue with regular pagination
                        if len(batch_issues) < 100:
                            break
                        continue
                    else:
                        # For subsequent pages, fall back to REST API
                        logger.warning(
                            f"Cannot fetch page {page_num} with JQL method, switching to REST API"
                        )
                        # Get all remaining issues via REST
                        raw_issues = self._fetch_all_issues_rest(jql)
                        # Parse all issues
                        issues = self._parse_issues(raw_issues)
                        return issues

                batch_issues = result.get("issues", [])
                if not batch_issues:
                    break

                issues.extend(self._parse_issues(batch_issues))
                logger.info(
                    f"Fetched {len(batch_issues)} issues in this batch, total so far: {len(issues)}"
                )

                # Check if this is the last page
                if result.get("isLast", False):
                    break

                # For standard pagination, check if we've fetched all
                total = result.get("total")
                if total and len(issues) >= total:
                    break

                # Continue to next page
                next_page_token = result.get("nextPageToken")
                if not next_page_token and len(batch_issues) < 100:
                    # No more results
                    break

        else:
            # Use offset-based pagination for Jira Server
            logger.info("Using offset-based pagination for Jira Server")
            start = 0
            limit = 100

            while True:
                result = self.jira.jql(
                    jql, start=start, limit=limit, expand="changelog"
                )

                batch_issues = result.get("issues", [])
                if not batch_issues:
                    break

                issues.extend(self._parse_issues(batch_issues))

                # Check if there are more issues
                total = result.get("total", 0)
                logger.info(
                    f"Batch complete. Total available: {total}, fetched so far: {len(issues)}"
                )
                if start + limit >= total:
                    break

                start += limit

        return issues

    def _fetch_all_issues_rest(self, jql: str) -> List[Dict[str, Any]]:
        """
        Fallback method using direct REST API calls for complete pagination.
        Used when the atlassian-python-api methods fail.
        """
        logger.info("Using direct REST API for pagination")
        all_issues = []
        start_at = 0
        max_results = 100

        auth = HTTPBasicAuth(self.config.username, self.config.api_token)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        base_url = f"{self.config.url}/rest/api/2"

        while True:
            url = f"{base_url}/search"
            params = {
                "jql": jql,
                "startAt": start_at,
                "maxResults": max_results,
                "expand": "changelog",
                "fields": "*all",
            }

            logger.info(f"REST API: Fetching issues at offset {start_at}")

            try:
                response = requests.get(url, auth=auth, headers=headers, params=params)
                response.raise_for_status()

                data = response.json()
                issues = data.get("issues", [])
                total = data.get("total", 0)

                logger.info(
                    f"REST API: Received {len(issues)} issues. Total available: {total}"
                )

                if not issues:
                    break

                all_issues.extend(issues)

                # Check if we've fetched all issues
                if start_at + len(issues) >= total:
                    logger.info(f"REST API: Fetched all {len(all_issues)} issues")
                    break

                start_at += max_results

            except Exception as e:
                logger.error(f"REST API error: {e}")
                raise ProcessingError(f"Failed to fetch issues via REST API: {e}")

        return all_issues

    def _initialize_field_mapping(self):
        """Initialize field ID mapping for custom fields"""
        try:
            fields = self.jira.get_all_fields()
            self._field_map = {}
            self._custom_field_map = {}

            for field in fields:
                field_id = field.get("id")
                field_name = field.get("name")

                self._field_map[field_name] = field_id

                # Map common custom field names
                if field_name and field_id.startswith("customfield_"):
                    name_lower = field_name.lower()
                    if "story point" in name_lower:
                        self._custom_field_map["story_points"] = field_id
                    elif "sprint" in name_lower:
                        self._custom_field_map["sprint"] = field_id
                    elif "epic link" in name_lower:
                        self._custom_field_map["epic_link"] = field_id

            logger.info(f"Initialized field mapping with {len(self._field_map)} fields")
            logger.debug(f"Custom field mapping: {self._custom_field_map}")

        except Exception as e:
            logger.warning(f"Failed to initialize field mapping: {e}")
            self._field_map = {}
            self._custom_field_map = {}

    def _parse_issues(self, jira_issues: List[Dict]) -> List[Issue]:
        """Parse Jira API issue data into Issue objects"""
        issues = []

        for jira_issue in jira_issues:
            try:
                issue = self._parse_single_issue(jira_issue)
                if issue:
                    issues.append(issue)
            except Exception as e:
                logger.warning(f"Failed to parse issue {jira_issue.get('key')}: {e}")
                continue

        return issues

    def _parse_single_issue(self, jira_issue: Dict) -> Optional[Issue]:
        """Parse a single Jira issue"""
        fields = jira_issue.get("fields", {})

        # Extract basic fields
        key = jira_issue.get("key")
        if not key:
            return None

        # Parse dates
        created = self._parse_date(fields.get("created"))
        updated = self._parse_date(fields.get("updated"))
        resolved = self._parse_date(fields.get("resolutiondate"))

        # Extract story points from custom field
        story_points = None
        if self._custom_field_map and "story_points" in self._custom_field_map:
            story_points = fields.get(self._custom_field_map["story_points"])
            if story_points is not None:
                try:
                    story_points = float(story_points)
                except (ValueError, TypeError):
                    story_points = None

        # Get time tracking fields (in seconds, convert to hours)
        time_estimate = fields.get("timeoriginalestimate")
        if time_estimate:
            time_estimate = time_estimate / 3600.0  # Convert seconds to hours

        time_spent = fields.get("timespent")
        if time_spent:
            time_spent = time_spent / 3600.0  # Convert seconds to hours

        # Create Issue object
        issue = Issue(
            key=key,
            summary=fields.get("summary", ""),
            issue_type=fields.get("issuetype", {}).get("name", "Unknown"),
            status=fields.get("status", {}).get("name", "Unknown"),
            created=created,
            updated=updated,
            resolved=resolved,
            story_points=story_points,
            time_estimate=time_estimate,
            time_spent=time_spent,
            assignee=fields.get("assignee", {}).get("displayName")
            if fields.get("assignee")
            else None,
            reporter=fields.get("reporter", {}).get("displayName")
            if fields.get("reporter")
            else None,
            labels=fields.get("labels", []),
        )

        # Add custom fields
        # Sprint information
        if self._custom_field_map and "sprint" in self._custom_field_map:
            sprints = fields.get(self._custom_field_map["sprint"], [])
            if sprints and isinstance(sprints, list):
                # Get the latest sprint
                latest_sprint = sprints[-1]
                if isinstance(latest_sprint, dict):
                    issue.custom_fields["sprint"] = latest_sprint.get("name")
                    # Store full sprint data for date extraction
                    issue.custom_fields["sprint_data"] = latest_sprint
                elif isinstance(latest_sprint, str):
                    # Parse sprint string format:
                    # "com.atlassian.greenhopper.service.sprint.Sprint@1234[name=Sprint 1,...]"
                    import re

                    match = re.search(r"name=([^,\]]+)", latest_sprint)
                    if match:
                        issue.custom_fields["sprint"] = match.group(1)

        # Priority
        if fields.get("priority"):
            issue.custom_fields["priority"] = fields["priority"].get("name")

        # Description
        if fields.get("description"):
            issue.custom_fields["description"] = fields["description"]

        # Epic link
        if self._custom_field_map and "epic_link" in self._custom_field_map:
            epic_link = fields.get(self._custom_field_map["epic_link"])
            if epic_link:
                issue.custom_fields["epic_link"] = epic_link

        return issue

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse Jira date string to datetime"""
        if not date_str:
            return None

        # Jira dates are typically in ISO format
        try:
            # Handle timezone-aware strings
            if "T" in date_str:
                # Remove microseconds if present
                if "." in date_str:
                    date_str = date_str.split(".")[0] + "Z"
                # Parse ISO format
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                return datetime.fromisoformat(date_str)
        except Exception:
            try:
                # Fallback to basic parsing
                return datetime.strptime(date_str[:19], "%Y-%m-%dT%H:%M:%S")
            except Exception as e:
                logger.warning(f"Failed to parse date '{date_str}': {e}")
                return None

    def _fetch_sprint_data(self) -> Dict[str, Dict[str, Any]]:
        """Fetch actual sprint data from Jira Agile API"""
        sprint_map = {}

        try:
            # Get all boards for the project
            if not self.config.project_key:
                return sprint_map

            boards_url = "rest/agile/1.0/board"
            params = {"projectKeyOrId": self.config.project_key}

            try:
                response = self.jira.get(boards_url, params=params)
                boards = response.get("values", [])
            except Exception as e:
                logger.debug(f"Could not fetch boards: {e}")
                return sprint_map

            # Get sprints from each board
            for board in boards:
                board_id = board.get("id")
                if not board_id:
                    continue

                try:
                    # Get all sprints for this board
                    sprints_url = f"rest/agile/1.0/board/{board_id}/sprint"
                    sprint_response = self.jira.get(sprints_url)
                    sprints = sprint_response.get("values", [])

                    # Map sprints by name
                    for sprint in sprints:
                        sprint_name = sprint.get("name")
                        if sprint_name:
                            sprint_map[sprint_name] = sprint

                except Exception as e:
                    logger.debug(f"Could not fetch sprints for board {board_id}: {e}")
                    continue

        except Exception as e:
            logger.debug(f"Error fetching sprint data from Agile API: {e}")

        logger.info(f"Fetched {len(sprint_map)} sprints from Jira Agile API")
        return sprint_map

    def _extract_sprints(self, issues: List[Issue]) -> List[Sprint]:
        """Extract sprint information from issues"""
        # First, get actual sprint data from Jira Agile API if available
        sprint_data_map = self._fetch_sprint_data()

        # Group issues by sprint
        sprints_dict = {}

        for issue in issues:
            sprint_name = issue.custom_fields.get("sprint")
            if not sprint_name:
                continue

            if sprint_name not in sprints_dict:
                # Check if we have sprint data embedded in the issue
                sprint_data_from_issue = issue.custom_fields.get("sprint_data", {})
                sprints_dict[sprint_name] = {
                    "name": sprint_name,
                    "issues": [],
                    "start_date": self._parse_date(
                        sprint_data_from_issue.get("startDate")
                    ),
                    "end_date": self._parse_date(sprint_data_from_issue.get("endDate")),
                }

            sprints_dict[sprint_name]["issues"].append(issue)

        # Create Sprint objects
        sprints = []
        for sprint_name, sprint_data in sprints_dict.items():
            if not sprint_data["issues"]:
                continue

            # Use dates from sprint data if available
            start_date = sprint_data.get("start_date")
            end_date = sprint_data.get("end_date")

            # Try API sprint data map as second option
            if (not start_date or not end_date) and sprint_name in sprint_data_map:
                actual_sprint = sprint_data_map[sprint_name]
                if not start_date:
                    start_date = self._parse_date(actual_sprint.get("startDate"))
                if not end_date:
                    end_date = self._parse_date(actual_sprint.get("endDate"))

            # Last resort: infer from issues
            if not start_date or not end_date:
                created_dates = [i.created for i in sprint_data["issues"] if i.created]
                resolved_dates = [
                    i.resolved for i in sprint_data["issues"] if i.resolved
                ]

                if not start_date and created_dates:
                    start_date = min(created_dates)
                if not end_date and resolved_dates:
                    end_date = max(resolved_dates)

            # Get completed issues
            completed_issues = [i for i in sprint_data["issues"] if i.resolved]

            # Calculate completed points
            completed_points = sum(
                i.story_points or 0 for i in completed_issues if i.story_points
            )

            sprint = Sprint(
                name=sprint_name,
                start_date=start_date,
                end_date=end_date,
                completed_points=completed_points,
                completed_issues=completed_issues,
            )
            sprints.append(sprint)

        return sorted(sprints, key=lambda s: s.start_date or datetime.min)

    def test_connection(self) -> bool:
        """Test the Jira API connection"""
        try:
            # Try to get server info
            info = self.jira.get_server_info()
            logger.info(
                f"Successfully connected to Jira: {info.get('serverTitle', 'Unknown')}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Jira: {e}")
            return False

    def get_projects(self) -> List[Dict[str, str]]:
        """Get list of accessible projects"""
        try:
            projects = self.jira.projects()
            return [
                {
                    "key": p.get("key"),
                    "name": p.get("name"),
                    "id": p.get("id"),
                }
                for p in projects
            ]
        except Exception as e:
            logger.error(f"Failed to fetch projects: {e}")
            return []

    def get_project_info(self) -> Optional[Dict[str, str]]:
        """Get current project information"""
        if self._project_info:
            return self._project_info

        if not self.config.project_key:
            return None

        try:
            project = self.jira.get_project(self.config.project_key)
            self._project_info = {
                "key": project.get("key"),
                "name": project.get("name"),
                "description": project.get("description", ""),
                "id": project.get("id"),
            }
            return self._project_info
        except Exception as e:
            logger.error(f"Error getting project info: {e}")
            return None

    def get_jql_query(self) -> str:
        """Get the JQL query being used"""
        return self._build_jql_query()
