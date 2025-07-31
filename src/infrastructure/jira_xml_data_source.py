"""High-performance streaming XML parser for Jira exports"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Iterator, List, Optional, Tuple

from lxml import etree

from ..domain.data_sources import IssueData
from ..domain.entities import Issue, Sprint
from ..domain.exceptions import ProcessingError

logger = logging.getLogger(__name__)


class JiraXmlDataSource:
    """
    High-performance streaming XML parser for Jira exports.

    Uses lxml's iterparse for memory-efficient processing of large XML files.
    Designed to handle multi-gigabyte XML exports efficiently.
    """

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"XML file not found: {file_path}")

        # Field mappings for custom fields
        self.custom_field_mappings = {
            "story_points": None,
            "sprint": None,
            "epic_link": None,
        }

    def parse(self) -> Tuple[List[Issue], List[Sprint]]:
        """
        Parse the XML file and return issues and sprints.

        Uses streaming parsing to handle large files efficiently.
        """
        try:
            issues = []
            sprints_dict = {}

            # Parse issues using streaming
            for issue_data in self._parse_issues_streaming():
                issue = self._create_issue(issue_data)
                if issue:
                    issues.append(issue)

                    # Extract sprint information from custom fields
                    sprint_name = issue.custom_fields.get("sprint")
                    if sprint_name:
                        if sprint_name not in sprints_dict:
                            sprints_dict[sprint_name] = {
                                "name": sprint_name,
                                "issues": [],
                                "start_date": None,
                                "end_date": None,
                            }
                        sprints_dict[sprint_name]["issues"].append(issue)

            # Create Sprint objects
            sprints = self._create_sprints(sprints_dict)

            logger.info(f"Parsed {len(issues)} issues and {len(sprints)} sprints from XML")
            return issues, sprints

        except Exception as e:
            logger.error(f"Error parsing XML file: {e}")
            raise ProcessingError(f"Failed to parse XML file: {e}")

    def _parse_issues_streaming(self) -> Iterator[IssueData]:
        """
        Stream parse issues from the XML file.

        Uses lxml's iterparse for memory efficiency.
        """
        # Events to listen for
        events = ("start", "end")

        # Create parser context - don't filter by tag initially
        context = etree.iterparse(
            str(self.file_path),
            events=events,
            encoding="utf-8",
            huge_tree=True,  # Enable parsing of very large documents
        )

        # Make it an iterator
        context = iter(context)

        # Track current issue data
        current_issue = None
        current_customfield = None

        for event, elem in context:
            if event == "start" and elem.tag == "item":
                # Start of a new issue
                current_issue = IssueData()

            elif event == "end" and elem.tag == "item" and current_issue:
                # End of issue - yield it
                yield current_issue
                current_issue = None

                # Clear the element to free memory
                elem.clear()
                # Also eliminate now-empty references from the root node
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

            elif current_issue and event == "end":
                # Process issue fields
                if elem.tag == "key":
                    current_issue.key = elem.text
                    logger.debug(f"Found key: {elem.text}")
                elif elem.tag == "summary":
                    current_issue.summary = elem.text
                elif elem.tag == "type":
                    current_issue.issue_type = elem.text
                elif elem.tag == "status":
                    current_issue.status = elem.text
                elif elem.tag == "priority":
                    current_issue.priority = elem.text
                elif elem.tag == "assignee":
                    current_issue.assignee = elem.text
                elif elem.tag == "reporter":
                    current_issue.reporter = elem.text
                elif elem.tag == "created":
                    current_issue.created = self._parse_date(elem.text)
                elif elem.tag == "updated":
                    current_issue.updated = self._parse_date(elem.text)
                elif elem.tag == "resolved":
                    current_issue.resolved = self._parse_date(elem.text)
                elif elem.tag == "description":
                    current_issue.description = elem.text
                elif elem.tag == "label" and elem.getparent().tag == "labels":
                    if current_issue.labels is None:
                        current_issue.labels = []
                    current_issue.labels.append(elem.text)
                elif elem.tag == "customfieldname":
                    # Track custom field name
                    if elem.text == "Story Points":
                        current_customfield = "story_points"
                    elif elem.text == "Sprint":
                        current_customfield = "sprint"
                    elif elem.text == "Epic Link":
                        current_customfield = "epic_link"
                elif elem.tag == "customfieldvalue" and current_customfield:
                    # Process custom field value
                    if current_customfield == "story_points":
                        try:
                            current_issue.story_points = float(elem.text)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid story points value: {elem.text}")
                    elif current_customfield == "sprint":
                        current_issue.sprint = elem.text
                    elif current_customfield == "epic_link":
                        current_issue.epic_link = elem.text
                elif elem.tag == "customfield":
                    # Reset custom field tracking
                    current_customfield = None

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse various date formats from Jira XML."""
        if not date_str:
            return None

        # Common Jira XML date formats
        date_formats = [
            "%a, %d %b %Y %H:%M:%S %z",  # Mon, 1 Jan 2024 10:00:00 +0000
            "%Y-%m-%d %H:%M:%S.%f",  # 2024-01-01 10:00:00.000
            "%Y-%m-%dT%H:%M:%S.%f%z",  # 2024-01-01T10:00:00.000+0000
            "%Y-%m-%d",  # 2024-01-01
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Unable to parse date: {date_str}")
        return None

    def _create_issue(self, issue_data: IssueData) -> Optional[Issue]:
        """Create an Issue entity from parsed data."""
        if not issue_data.key:
            logger.warning("Skipping issue without key")
            return None

        issue = Issue(
            key=issue_data.key,
            summary=issue_data.summary or "",
            issue_type=issue_data.issue_type or "Unknown",
            status=issue_data.status or "Unknown",
            created=issue_data.created,
            updated=issue_data.updated,
            resolved=issue_data.resolved,
            story_points=issue_data.story_points,
            assignee=issue_data.assignee,
            labels=issue_data.labels or [],
        )

        # Add additional fields to custom_fields
        if issue_data.sprint:
            issue.custom_fields["sprint"] = issue_data.sprint
        if issue_data.priority:
            issue.custom_fields["priority"] = issue_data.priority
        if issue_data.description:
            issue.custom_fields["description"] = issue_data.description
        if issue_data.epic_link:
            issue.custom_fields["epic_link"] = issue_data.epic_link

        return issue

    def _create_sprints(self, sprints_dict: dict) -> List[Sprint]:
        """Create Sprint objects from collected sprint data."""
        sprints = []

        for sprint_name, sprint_data in sprints_dict.items():
            if not sprint_data["issues"]:
                continue

            # Calculate sprint dates from issue dates
            created_dates = [i.created for i in sprint_data["issues"] if i.created]
            resolved_dates = [i.resolved for i in sprint_data["issues"] if i.resolved]

            start_date = min(created_dates) if created_dates else None
            end_date = max(resolved_dates) if resolved_dates else None

            # Get completed issues
            completed_issues_list = [i for i in sprint_data["issues"] if i.resolved]

            # Calculate completed points
            completed_points = sum(i.story_points or 0 for i in completed_issues_list if i.story_points)

            sprint = Sprint(
                name=sprint_name,
                start_date=start_date,
                end_date=end_date,
                completed_points=completed_points,
                completed_issues=completed_issues_list,
            )
            sprints.append(sprint)

        return sorted(sprints, key=lambda s: s.start_date or datetime.min)

    def detect_custom_fields(self) -> dict:
        """
        Auto-detect custom field IDs for known field types.

        Returns a mapping of field types to their custom field IDs.
        """
        field_mapping = {}

        # Quick scan for custom field definitions
        context = etree.iterparse(
            str(self.file_path),
            events=("start", "end"),
            tag="customfield",
            encoding="utf-8",
        )

        for event, elem in context:
            if event == "end":
                field_id = elem.get("id")

                # Look for field name
                name_elem = elem.find(".//customfieldname")
                if name_elem is not None and name_elem.text:
                    field_name = name_elem.text.lower()

                    # Map known field types
                    if "story point" in field_name:
                        field_mapping["story_points"] = field_id
                    elif "sprint" in field_name:
                        field_mapping["sprint"] = field_id
                    elif "epic link" in field_name:
                        field_mapping["epic_link"] = field_id

                # Clear memory
                elem.clear()

        logger.info(f"Detected custom fields: {field_mapping}")
        return field_mapping
