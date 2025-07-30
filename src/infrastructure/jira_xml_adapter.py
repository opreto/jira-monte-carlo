"""Adapter to make JiraXmlDataSource comply with DataSource interface"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..domain.data_sources import DataSource, DataSourceInfo, DataSourceType
from ..domain.entities import Issue, Sprint
from ..domain.value_objects import FieldMapping
from .jira_xml_data_source import JiraXmlDataSource

logger = logging.getLogger(__name__)


class JiraXmlDataSourceAdapter(DataSource):
    """Adapter for JiraXmlDataSource to implement DataSource interface"""

    def __init__(self, field_mapping: Optional[FieldMapping] = None):
        self.field_mapping = field_mapping or self._get_default_field_mapping()

    def parse_file(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        """Parse XML file and extract issues and sprints"""
        parser = JiraXmlDataSource(str(file_path))
        return parser.parse()

    def detect_format(self, file_path: Path) -> bool:
        """Detect if this is a Jira XML file"""
        # Check file extension
        if file_path.suffix.lower() != ".xml":
            return False

        # Try to parse the first few elements to verify it's Jira XML
        try:
            from lxml import etree

            # Parse just the beginning of the file
            with open(file_path, "rb") as f:
                # Read first 10KB to check format
                sample = f.read(10240)

            # Try to parse the sample
            root = etree.fromstring(sample, etree.XMLParser(recover=True))

            # Check for Jira XML indicators
            # Look for RSS structure with channel and items
            if root.tag == "rss":
                channel = root.find("channel")
                if channel is not None:
                    # Check for Jira-specific elements
                    channel.find("build-info")  # Check existence without using result
                    item = channel.find("item")

                    if item is not None:
                        # Check for Jira issue fields
                        key = item.find("key")
                        status = item.find("status")
                        project = item.find("project")

                        # If we find these Jira-specific fields, it's likely a Jira XML
                        if any(
                            [key is not None, status is not None, project is not None]
                        ):
                            logger.info(f"Detected Jira XML format for: {file_path}")
                            return True

        except Exception as e:
            logger.debug(f"Not a Jira XML file: {file_path} - {e}")

        return False

    def get_info(self) -> DataSourceInfo:
        """Get information about this data source"""
        return DataSourceInfo(
            source_type=DataSourceType.JIRA_XML,
            name="Jira XML Export",
            description="High-performance streaming parser for Jira XML exports (RSS format)",
            file_extensions=[".xml"],
            default_field_mapping=self._get_default_field_mapping(),
        )

    def analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze the structure of the XML file"""
        try:
            parser = JiraXmlDataSource(str(file_path))

            # Detect custom fields
            custom_fields = parser.detect_custom_fields()

            # Quick scan for statistics
            issue_count = 0
            statuses = set()
            issue_types = set()

            from lxml import etree

            # Count items and collect metadata
            context = etree.iterparse(
                str(file_path), events=("end",), tag="item", encoding="utf-8"
            )

            for event, elem in context:
                issue_count += 1

                # Sample first few issues for metadata
                if issue_count <= 10:
                    status = elem.find("status")
                    if status is not None and status.text:
                        statuses.add(status.text)

                    issue_type = elem.find("type")
                    if issue_type is not None and issue_type.text:
                        issue_types.add(issue_type.text)

                # Clear memory
                elem.clear()
                while elem.getprevious() is not None:
                    del elem.getparent()[0]

                # Limit scan for performance
                if issue_count > 100:
                    # Estimate total from partial scan
                    file_size = file_path.stat().st_size
                    scanned_pos = file_path.open("rb").tell()
                    if scanned_pos > 0:
                        issue_count = int(issue_count * file_size / scanned_pos)
                    break

            return {
                "format": "Jira XML (RSS)",
                "issue_count": issue_count,
                "file_size_mb": round(file_path.stat().st_size / 1024 / 1024, 2),
                "detected_fields": {
                    "custom_fields": custom_fields,
                    "has_story_points": "story_points" in custom_fields,
                    "has_sprints": "sprint" in custom_fields,
                },
                "sample_data": {
                    "statuses": list(statuses)[:10],
                    "issue_types": list(issue_types)[:10],
                },
            }

        except Exception as e:
            logger.error(f"Error analyzing XML structure: {e}")
            return {
                "format": "Jira XML",
                "error": str(e),
            }

    def _get_default_field_mapping(self) -> FieldMapping:
        """Get default field mapping for Jira XML"""
        return FieldMapping(
            key_field="key",
            summary_field="summary",
            issue_type_field="type",
            status_field="status",
            created_field="created",
            updated_field="updated",
            resolved_field="resolved",
            story_points_field="Story Points",  # Custom field name
            sprint_field="Sprint",  # Custom field name
            assignee_field="assignee",
            reporter_field="reporter",
            labels_field="labels",
        )
