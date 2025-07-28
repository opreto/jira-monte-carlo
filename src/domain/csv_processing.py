"""Domain interfaces for CSV processing and analysis"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import pandas as pd

from .analysis import CSVAnalysisResult, VelocityAnalysisConfig
from .entities import Issue, Sprint
from .value_objects import FieldMapping, VelocityMetrics


class CSVParser(ABC):
    """Interface for parsing CSV files into domain entities"""

    @abstractmethod
    def parse(self, df: pd.DataFrame, field_mapping: FieldMapping) -> List[Issue]:
        """Parse DataFrame into list of Issues"""
        pass


class CSVAnalyzer(ABC):
    """Interface for analyzing CSV structure and data patterns"""

    @abstractmethod
    def analyze_structure(self, file_path: Path) -> CSVAnalysisResult:
        """Analyze CSV file structure and detect patterns"""
        pass

    @abstractmethod
    def extract_sprints(self, df: pd.DataFrame, field_mapping: FieldMapping) -> List[Sprint]:
        """Extract sprint information from CSV data"""
        pass

    @abstractmethod
    def extract_velocity(
        self, df: pd.DataFrame, field_mapping: FieldMapping, config: VelocityAnalysisConfig
    ) -> VelocityMetrics:
        """Extract velocity metrics from CSV data"""
        pass


class SprintExtractor(ABC):
    """Interface for extracting sprint data from various sources"""

    @abstractmethod
    def extract_from_issues(self, issues: List[Issue]) -> List[Sprint]:
        """Extract sprint information from issues"""
        pass

    @abstractmethod
    def extract_from_dataframe(
        self, df: pd.DataFrame, sprint_field: str, velocity_field: str = "Story Points"
    ) -> List[Sprint]:
        """Extract sprint information directly from DataFrame"""
        pass
