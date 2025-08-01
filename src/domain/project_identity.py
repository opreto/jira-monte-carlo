"""Project identity management for ML model isolation."""

import hashlib
from typing import Optional
from urllib.parse import urlparse


def generate_project_id(jira_url: str, project_key: str) -> str:
    """Generate a stable project ID from Jira URL and project key.

    This creates a short, filesystem-safe identifier that uniquely identifies
    a project based on its Jira instance and project key. This allows ML models
    to be automatically associated with the right project without manual configuration.

    Args:
        jira_url: The Jira instance URL (e.g., https://mycompany.atlassian.net)
        project_key: The Jira project key (e.g., PROJ)

    Returns:
        A short, stable project ID (e.g., "mycompany-PROJ-a1b2c3")
    """
    # Normalize the URL - extract just the hostname
    parsed = urlparse(jira_url.lower())
    hostname = parsed.hostname or parsed.netloc

    # Remove common suffixes for cleaner IDs
    if hostname:
        hostname = hostname.replace(".atlassian.net", "")
        hostname = hostname.replace(".jira.com", "")
        hostname = hostname.replace(".com", "")
        hostname = hostname.replace(".org", "")
        hostname = hostname.replace(".net", "")

    # Create a unique string from URL + project key
    unique_string = f"{hostname}:{project_key.upper()}"

    # Generate a short hash for uniqueness (in case of conflicts)
    hash_digest = hashlib.sha256(unique_string.encode()).hexdigest()[:6]

    # Combine readable parts with hash
    # Format: "hostname-PROJECT-hash"
    project_id = f"{hostname}-{project_key.upper()}-{hash_digest}"

    # Ensure filesystem safety
    project_id = project_id.replace("/", "-").replace("\\", "-").replace(":", "-")

    return project_id


def extract_project_key_from_csv(filename: str) -> Optional[str]:
    """Extract project key from a CSV filename.

    Assumes filenames follow patterns like:
    - PROJ-issues.csv
    - project-PROJ-export.csv
    - PROJ_2024_data.csv

    Args:
        filename: The CSV filename

    Returns:
        The extracted project key or None if not found
    """
    import re
    import os

    # Get just the filename without path
    basename = os.path.basename(filename)

    # Common patterns for project keys in filenames
    patterns = [
        r"^([A-Z]+)-",  # PROJ-issues.csv
        r"-([A-Z]+)-",  # project-PROJ-export.csv
        r"^([A-Z]+)_",  # PROJ_2024_data.csv
        r"_([A-Z]+)_",  # data_PROJ_export.csv
    ]

    for pattern in patterns:
        match = re.search(pattern, basename)
        if match:
            potential_key = match.group(1)
            # Validate it looks like a project key (2-10 uppercase letters)
            if 2 <= len(potential_key) <= 10 and potential_key.isalpha():
                return potential_key

    return None


def generate_csv_project_id(
    filename: str, project_key: Optional[str] = None
) -> Optional[str]:
    """Generate a project ID for CSV files.

    Args:
        filename: The CSV filename
        project_key: Optional explicit project key, otherwise extracted from filename

    Returns:
        A project ID or None if project key cannot be determined
    """
    if not project_key:
        project_key = extract_project_key_from_csv(filename)

    if not project_key:
        return None

    # For CSV files, use "local" as the hostname equivalent
    # This keeps CSV-based models separate from Jira-based ones
    return generate_project_id("local://csv", project_key)
