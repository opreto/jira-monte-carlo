"""Tests for Jira API data source"""

from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from src.domain.entities import Issue, Sprint
from src.domain.exceptions import ProcessingError
from src.infrastructure.config import JiraConfig
from src.infrastructure.jira_api_data_source import JiraApiDataSource


@pytest.fixture
def mock_config():
    """Create a mock JiraConfig"""
    config = JiraConfig(
        url="https://test.atlassian.net",
        username="test@example.com",
        api_token="test-token",
        project_key="TEST",
    )
    return config


@pytest.fixture
def mock_jira_client():
    """Create a mock Jira client"""
    with patch("src.infrastructure.jira_api_data_source.Jira") as mock_jira_class:
        mock_client = Mock()
        mock_jira_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def jira_data_source(mock_config, mock_jira_client):
    """Create a JiraApiDataSource instance with mocked dependencies"""
    with patch("src.infrastructure.jira_api_data_source.APICache"):
        data_source = JiraApiDataSource(mock_config)
        data_source.cache = Mock()
        data_source.cache.get.return_value = None  # Default to cache miss
        return data_source


class TestJiraApiDataSource:
    """Test cases for JiraApiDataSource"""

    def test_initialization(self, mock_config):
        """Test data source initialization"""
        with patch("src.infrastructure.jira_api_data_source.Jira") as mock_jira_class:
            with patch("src.infrastructure.jira_api_data_source.APICache"):
                data_source = JiraApiDataSource(mock_config)

                assert data_source.config == mock_config
                assert data_source.is_cloud is True
                mock_jira_class.assert_called_once_with(
                    url="https://test.atlassian.net",
                    username="test@example.com",
                    password="test-token",
                    cloud=True,
                )

    def test_build_jql_query_with_project(self, jira_data_source):
        """Test JQL query building with project key"""
        jql = jira_data_source._build_jql_query()
        assert jql == "project = TEST ORDER BY created DESC"

    def test_build_jql_query_without_project(self, jira_data_source):
        """Test JQL query building without project key"""
        jira_data_source.config.project_key = None
        jql = jira_data_source._build_jql_query()
        assert jql == "created >= -26w ORDER BY created DESC"

    def test_build_jql_query_with_custom_filter(self, jira_data_source):
        """Test JQL query building with custom filter"""
        jira_data_source.config.jql_filter = "project = CUSTOM AND status = Open"
        jql = jira_data_source._build_jql_query()
        assert jql == "project = CUSTOM AND status = Open"

    def test_parse_with_cache_hit(self, jira_data_source):
        """Test parse method with cache hit"""
        # Setup cache hit
        cached_issues = [
            Issue(
                key="TEST-1",
                summary="Test Issue",
                issue_type="Story",
                status="Done",
                created=datetime.now(timezone.utc),
                reporter="test@example.com",
            )
        ]
        cached_sprints = [
            Sprint(
                name="Sprint 1",
                start_date=datetime.now(timezone.utc),
                end_date=datetime.now(timezone.utc),
                completed_points=10.0,
            )
        ]

        jira_data_source.cache.get.return_value = {
            "issues": cached_issues,
            "sprints": cached_sprints,
        }

        issues, sprints = jira_data_source.parse()

        assert issues == cached_issues
        assert sprints == cached_sprints
        jira_data_source.cache.set.assert_not_called()

    @patch("src.infrastructure.jira_api_data_source.requests.get")
    def test_fetch_all_issues_rest(self, mock_get, jira_data_source):
        """Test REST API fallback for fetching issues"""
        # Setup mock responses
        response1 = Mock()
        response1.status_code = 200
        response1.json.return_value = {
            "total": 2,
            "issues": [
                {
                    "key": "TEST-1",
                    "fields": {
                        "summary": "Test Issue 1",
                        "issuetype": {"name": "Story"},
                        "status": {"name": "Done"},
                    },
                }
            ],
        }

        response2 = Mock()
        response2.status_code = 200
        response2.json.return_value = {
            "total": 2,
            "issues": [
                {
                    "key": "TEST-2",
                    "fields": {
                        "summary": "Test Issue 2",
                        "issuetype": {"name": "Bug"},
                        "status": {"name": "Open"},
                    },
                }
            ],
        }

        mock_get.side_effect = [response1, response2]

        issues = jira_data_source._fetch_all_issues_rest("project = TEST")

        assert len(issues) == 2
        assert issues[0]["key"] == "TEST-1"
        assert issues[1]["key"] == "TEST-2"

        # Verify authentication
        calls = mock_get.call_args_list
        for call in calls:
            assert call[1]["auth"].username == "test@example.com"
            assert call[1]["auth"].password == "test-token"

    def test_parse_issue_basic_fields(self, jira_data_source):
        """Test parsing of basic issue fields"""
        raw_issue = {
            "key": "TEST-123",
            "fields": {
                "summary": "Test Summary",
                "issuetype": {"name": "Story"},
                "status": {"name": "In Progress"},
                "created": "2024-01-01T10:00:00.000+0000",
                "updated": "2024-01-02T10:00:00.000+0000",
                "resolutiondate": None,
                "assignee": {"displayName": "John Doe"},
                "reporter": {"displayName": "Jane Smith"},
                "labels": ["backend", "api"],
            },
        }

        issue = jira_data_source._parse_issues([raw_issue])[0]

        assert issue.key == "TEST-123"
        assert issue.summary == "Test Summary"
        assert issue.issue_type == "Story"
        assert issue.status == "In Progress"
        assert issue.assignee == "John Doe"
        assert issue.reporter == "Jane Smith"
        assert issue.labels == ["backend", "api"]

    def test_parse_date_formats(self, jira_data_source):
        """Test various date format parsing"""
        # ISO format with Z
        date1 = jira_data_source._parse_date("2024-01-01T10:00:00.000Z")
        assert date1 is not None
        assert date1.year == 2024

        # ISO format with offset
        date2 = jira_data_source._parse_date("2024-01-01T10:00:00.000+0000")
        assert date2 is not None

        # None
        date3 = jira_data_source._parse_date(None)
        assert date3 is None

        # Invalid format
        date4 = jira_data_source._parse_date("invalid-date")
        assert date4 is None

    def test_test_connection_success(self, jira_data_source):
        """Test successful connection test"""
        jira_data_source.jira = Mock()
        jira_data_source.jira.get_server_info.return_value = {
            "serverTitle": "Test JIRA",
            "version": "8.0.0",
        }

        result = jira_data_source.test_connection()
        assert result is True
        jira_data_source.jira.get_server_info.assert_called_once()

    def test_test_connection_failure(self, jira_data_source):
        """Test failed connection test"""
        jira_data_source.jira = Mock()
        jira_data_source.jira.get_server_info.side_effect = Exception("Authentication failed")

        result = jira_data_source.test_connection()
        assert result is False

    def test_get_projects(self, jira_data_source, mock_jira_client):
        """Test getting projects"""
        mock_jira_client.projects.return_value = [
            {"key": "TEST", "name": "Test Project"},
            {"key": "DEMO", "name": "Demo Project"},
        ]

        projects = jira_data_source.get_projects()
        assert len(projects) == 2
        assert projects[0]["key"] == "TEST"
        assert projects[1]["name"] == "Demo Project"

    def test_parse_with_processing_error(self, jira_data_source):
        """Test parse method with processing error"""
        # Make fetch_all_issues raise an exception
        with patch.object(jira_data_source, "_fetch_all_issues", side_effect=Exception("API Error")):
            with pytest.raises(ProcessingError) as exc_info:
                jira_data_source.parse()

            assert "Failed to fetch data from Jira" in str(exc_info.value)

    def test_extract_sprints_with_embedded_dates(self, jira_data_source):
        """Test extracting sprints with embedded date data from issues"""
        from datetime import datetime

        from src.domain.entities import Issue

        # Create test issues with sprint data including dates
        issues = [
            Issue(
                key="TEST-1",
                summary="Issue 1",
                issue_type="Story",
                status="Done",
                created=datetime(2024, 1, 1),
                resolved=datetime(2024, 1, 10),
                story_points=5.0,
                custom_fields={
                    "sprint": "Sprint 1",
                    "sprint_data": {
                        "startDate": "2024-01-01T00:00:00.000Z",
                        "endDate": "2024-01-14T00:00:00.000Z",
                    },
                },
            ),
            Issue(
                key="TEST-2",
                summary="Issue 2",
                issue_type="Story",
                status="Done",
                created=datetime(2024, 1, 5),
                resolved=datetime(2024, 1, 12),
                story_points=3.0,
                custom_fields={
                    "sprint": "Sprint 1",
                    "sprint_data": {
                        "startDate": "2024-01-01T00:00:00.000Z",
                        "endDate": "2024-01-14T00:00:00.000Z",
                    },
                },
            ),
        ]

        # Test sprint extraction
        sprints = jira_data_source._extract_sprints(issues)

        assert len(sprints) == 1
        sprint = sprints[0]
        assert sprint.name == "Sprint 1"
        # Compare dates without timezone info
        assert sprint.start_date.replace(tzinfo=None) == datetime(2024, 1, 1, 0, 0, 0)
        assert sprint.end_date.replace(tzinfo=None) == datetime(2024, 1, 14, 0, 0, 0)
        assert sprint.completed_points == 8.0
        assert len(sprint.completed_issues) == 2

        # Verify sprint duration is 14 days
        duration = (sprint.end_date - sprint.start_date).days
        assert duration == 13  # 14 days inclusive
