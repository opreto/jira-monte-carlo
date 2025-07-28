"""Use case for importing data from various sources"""
import logging
from pathlib import Path
from typing import List, Optional, Tuple

from ..domain.data_sources import DataSourceFactory, DataSourceType
from ..domain.entities import Issue, Sprint
from ..domain.repositories import ConfigRepository, IssueRepository, SprintRepository
from ..domain.value_objects import FieldMapping

logger = logging.getLogger(__name__)


class ImportDataUseCase:
    """Import data from various sources (CSV, API, etc.)"""

    def __init__(
        self,
        data_source_factory: DataSourceFactory,
        issue_repo: IssueRepository,
        sprint_repo: SprintRepository,
        config_repo: ConfigRepository,
    ):
        self.data_source_factory = data_source_factory
        self.issue_repo = issue_repo
        self.sprint_repo = sprint_repo
        self.config_repo = config_repo

    def execute(
        self,
        file_path: Path,
        source_type: Optional[DataSourceType] = None,
        field_mapping: Optional[FieldMapping] = None,
    ) -> Tuple[List[Issue], List[Sprint]]:
        """
        Import data from a file

        Args:
            file_path: Path to the data file
            source_type: Type of data source (if None, will auto-detect)
            field_mapping: Custom field mapping (if None, uses default or saved)

        Returns:
            Tuple of (issues, sprints)
        """
        logger.info(f"Importing data from: {file_path}")

        # Auto-detect source type if not provided
        if source_type is None:
            source_type = self.data_source_factory.detect_source_type(file_path)
            if source_type is None:
                raise ValueError(f"Could not detect data source type for: {file_path}")
            logger.info(f"Auto-detected source type: {source_type.value}")

        # Use saved field mapping if not provided
        if field_mapping is None:
            field_mapping = self.config_repo.load_field_mapping()

        # Create data source
        data_source = self.data_source_factory.create(source_type, field_mapping)

        # Parse file
        issues, sprints = data_source.parse_file(file_path)

        # Save to repositories
        if issues:
            self.issue_repo.save_all(issues)
            logger.info(f"Imported {len(issues)} issues")

        if sprints:
            self.sprint_repo.add_sprints(sprints)
            logger.info(f"Imported {len(sprints)} sprints")

        return issues, sprints


class AnalyzeDataSourceUseCase:
    """Analyze structure of a data source"""

    def __init__(self, data_source_factory: DataSourceFactory):
        self.data_source_factory = data_source_factory

    def execute(self, file_path: Path, source_type: Optional[DataSourceType] = None):
        """Analyze the structure of a data source file"""
        # Auto-detect if needed
        if source_type is None:
            source_type = self.data_source_factory.detect_source_type(file_path)
            if source_type is None:
                raise ValueError(f"Could not detect data source type for: {file_path}")

        # Create data source and analyze
        data_source = self.data_source_factory.create(source_type)
        return data_source.analyze_structure(file_path)
