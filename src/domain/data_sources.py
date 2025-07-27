"""Domain interfaces for data sources"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass

from .entities import Issue, Sprint
from .value_objects import FieldMapping


class DataSourceType(Enum):
    """Supported data source types"""
    JIRA_CSV = "jira_csv"
    LINEAR_CSV = "linear_csv"
    JIRA_XML = "jira_xml"
    # Future: JIRA_API = "jira_api"
    # Future: LINEAR_API = "linear_api"


@dataclass
class DataSourceInfo:
    """Information about a data source"""
    source_type: DataSourceType
    name: str
    description: str
    file_extensions: List[str]
    default_field_mapping: FieldMapping


class DataSource(ABC):
    """Abstract interface for data sources"""
    
    @abstractmethod
    def parse_file(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        """
        Parse a file and extract issues and sprints
        
        Returns:
            Tuple of (issues, sprints)
        """
        pass
    
    @abstractmethod
    def detect_format(self, file_path: Path) -> bool:
        """
        Detect if this parser can handle the given file
        
        Returns:
            True if this parser can handle the file format
        """
        pass
    
    @abstractmethod
    def get_info(self) -> DataSourceInfo:
        """Get information about this data source"""
        pass
    
    @abstractmethod
    def analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze the structure of the data source
        
        Returns:
            Dictionary with analysis results (columns, sample data, etc.)
        """
        pass


class DataSourceFactory(ABC):
    """Factory for creating data source instances"""
    
    @abstractmethod
    def create(self, source_type: DataSourceType, field_mapping: Optional[FieldMapping] = None) -> DataSource:
        """Create a data source instance"""
        pass
    
    @abstractmethod
    def detect_source_type(self, file_path: Path) -> Optional[DataSourceType]:
        """Auto-detect the source type from file"""
        pass
    
    @abstractmethod
    def get_available_sources(self) -> List[DataSourceInfo]:
        """Get list of available data sources"""
        pass