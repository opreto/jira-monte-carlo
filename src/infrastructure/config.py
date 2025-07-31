"""Configuration management for external services"""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class JiraConfig:
    """Configuration for Jira API connection"""

    url: str
    username: str
    api_token: str
    project_key: Optional[str] = None
    jql_filter: Optional[str] = (
        None  # Legacy, now used as forecast_jql if forecast_jql not set
    )
    history_jql: Optional[str] = None
    forecast_jql: Optional[str] = None

    @classmethod
    def from_env(cls) -> "JiraConfig":
        """Create configuration from environment variables"""
        url = os.getenv("JIRA_URL")
        username = os.getenv("JIRA_USERNAME")
        api_token = os.getenv("ATLASSIAN_API_TOKEN")

        if not all([url, username, api_token]):
            missing = []
            if not url:
                missing.append("JIRA_URL")
            if not username:
                missing.append("JIRA_USERNAME")
            if not api_token:
                missing.append("ATLASSIAN_API_TOKEN")
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )

        # Support both old and new environment variable names
        jql_filter = os.getenv("JIRA_JQL_FILTER")
        forecast_jql = os.getenv("FORECAST_JQL", jql_filter)
        history_jql = os.getenv("HISTORY_JQL")

        return cls(
            url=url,
            username=username,
            api_token=api_token,
            project_key=os.getenv("JIRA_PROJECT_KEY"),
            jql_filter=jql_filter,
            history_jql=history_jql,
            forecast_jql=forecast_jql,
        )

    def validate(self) -> None:
        """Validate the configuration"""
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("JIRA_URL must start with http:// or https://")

        if "@" not in self.username and "atlassian.net" in self.url:
            raise ValueError(
                "JIRA_USERNAME should be an email address for Atlassian Cloud"
            )
