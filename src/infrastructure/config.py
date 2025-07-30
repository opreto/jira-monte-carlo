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
    jql_filter: Optional[str] = None

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

        return cls(
            url=url,
            username=username,
            api_token=api_token,
            project_key=os.getenv("JIRA_PROJECT_KEY"),
            jql_filter=os.getenv("JIRA_JQL_FILTER"),
        )

    def validate(self) -> None:
        """Validate the configuration"""
        if not self.url.startswith(("http://", "https://")):
            raise ValueError("JIRA_URL must start with http:// or https://")

        if "@" not in self.username and "atlassian.net" in self.url:
            raise ValueError(
                "JIRA_USERNAME should be an email address for Atlassian Cloud"
            )
