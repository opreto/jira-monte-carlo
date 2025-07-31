"""Data source factory implementation"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from ..domain.data_sources import (
    DataSource,
    DataSourceFactory,
    DataSourceInfo,
    DataSourceType,
)
from ..domain.value_objects import FieldMapping
from .jira_api_adapter import JiraApiDataSourceAdapter
from .jira_data_source import JiraCSVDataSource
from .jira_xml_adapter import JiraXmlDataSourceAdapter
from .linear_data_source import LinearCSVDataSource

logger = logging.getLogger(__name__)


class DefaultDataSourceFactory(DataSourceFactory):
    """Default implementation of data source factory"""

    def __init__(self):
        # Registry of available data sources
        self._sources: Dict[DataSourceType, Type[DataSource]] = {
            DataSourceType.JIRA_CSV: JiraCSVDataSource,
            DataSourceType.LINEAR_CSV: LinearCSVDataSource,
            DataSourceType.JIRA_XML: JiraXmlDataSourceAdapter,
            DataSourceType.JIRA_API: JiraApiDataSourceAdapter,
        }

    def create(self, source_type: DataSourceType, field_mapping: Optional[FieldMapping] = None) -> DataSource:
        """Create a data source instance"""
        if source_type not in self._sources:
            raise ValueError(f"Unknown data source type: {source_type}")

        source_class = self._sources[source_type]
        return source_class(field_mapping)

    def detect_source_type(self, file_path: Path) -> Optional[DataSourceType]:
        """Auto-detect the source type from file"""
        logger.info(f"Auto-detecting source type for: {file_path}")

        # Try each source type's detection
        for source_type, source_class in self._sources.items():
            try:
                # Create a temporary instance for detection
                temp_source = source_class()
                if temp_source.detect_format(file_path):
                    logger.info(f"Detected source type: {source_type.value}")
                    return source_type
            except Exception as e:
                logger.debug(f"Detection failed for {source_type}: {e}")
                continue

        logger.warning(f"Could not detect source type for: {file_path}")
        return None

    def get_available_sources(self) -> List[DataSourceInfo]:
        """Get list of available data sources"""
        sources = []
        for source_type, source_class in self._sources.items():
            temp_source = source_class()
            sources.append(temp_source.get_info())
        return sources
