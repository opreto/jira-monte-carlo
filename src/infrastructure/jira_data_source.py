"""Jira CSV data source implementation"""
import polars as pl
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path
import logging
import csv

from ..domain.data_sources import DataSource, DataSourceInfo, DataSourceType
from ..domain.entities import Issue, Sprint
from ..domain.value_objects import FieldMapping
from ..domain.analysis import CSVAnalysisResult
from ..application.csv_analysis import AnalyzeCSVStructureUseCase
from .csv_parser import JiraCSVParser
from .csv_analyzer import SmartCSVParser, EnhancedSprintExtractor

logger = logging.getLogger(__name__)


class JiraCSVDataSource(DataSource):
    """Data source for Jira CSV exports"""
    
    def __init__(self, field_mapping: Optional[FieldMapping] = None):
        self.field_mapping = field_mapping or self._get_default_field_mapping()
    
    def parse_file(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        """Parse Jira CSV file and extract issues and sprints"""
        logger.info(f"Parsing Jira CSV file: {file_path}")
        
        # First analyze the CSV structure
        analysis_result = self._analyze_csv_structure(file_path)
        
        # Parse with smart column aggregation
        smart_parser = SmartCSVParser(self.field_mapping, analysis_result.column_groups)
        df = smart_parser.parse_file(file_path)
        
        # Extract issues
        parser = JiraCSVParser(self.field_mapping)
        issues = parser.parse_dataframe(df)
        
        # Extract sprints
        status_mapping = {"done": ["Done", "Released", "Closed", "Resolved"]}
        sprint_data = EnhancedSprintExtractor.extract_from_dataframe(
            df,
            self.field_mapping.sprint_field,
            self.field_mapping.status_field,
            status_mapping.get("done", []),
            self.field_mapping.story_points_field
        )
        
        # Convert sprint data to Sprint entities
        sprints = []
        for sprint_name, data in sprint_data.items():
            from datetime import datetime
            sprint = Sprint(
                name=sprint_name,
                start_date=datetime.now(),  # Will be enhanced with actual dates
                end_date=datetime.now(),
                completed_points=data["completed_points"] if isinstance(data, dict) else data
            )
            sprints.append(sprint)
        
        return issues, sprints
    
    def detect_format(self, file_path: Path) -> bool:
        """Detect if this is a Jira CSV file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader)
                
                # Look for typical Jira fields
                jira_indicators = [
                    'Issue key', 'Issue id', 'Issue Type', 'Status',
                    'Project key', 'Project name', 'Created', 'Updated',
                    'Resolved', 'Priority', 'Reporter', 'Assignee',
                    'Sprint', 'Story Points', 'Epic Link'
                ]
                
                # Count how many Jira-specific fields we find
                matches = sum(1 for field in jira_indicators 
                            if any(field.lower() in h.lower() for h in headers))
                
                # If we find at least 5 Jira fields, it's likely a Jira export
                return matches >= 5
                
        except Exception as e:
            logger.debug(f"Error detecting Jira format: {e}")
            return False
    
    def get_info(self) -> DataSourceInfo:
        """Get information about this data source"""
        return DataSourceInfo(
            source_type=DataSourceType.JIRA_CSV,
            name="Jira CSV Export",
            description="CSV export from Jira with issue and sprint data",
            file_extensions=[".csv"],
            default_field_mapping=self._get_default_field_mapping()
        )
    
    def analyze_structure(self, file_path: Path) -> Dict[str, Any]:
        """Analyze Jira CSV structure"""
        analysis_result = self._analyze_csv_structure(file_path)
        
        return {
            "total_rows": analysis_result.total_rows,
            "total_columns": analysis_result.total_columns,
            "column_groups": {k: len(v.columns) for k, v in analysis_result.column_groups.items()},
            "status_values": analysis_result.status_values,
            "sprint_values": analysis_result.sprint_values[:10],  # First 10 sprints
            "field_mapping_suggestions": analysis_result.field_mapping_suggestions,
            "numeric_field_candidates": analysis_result.numeric_field_candidates
        }
    
    def _analyze_csv_structure(self, file_path: Path) -> CSVAnalysisResult:
        """Analyze CSV structure using existing analyzer"""
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            rows = list(reader)
        
        analyzer = AnalyzeCSVStructureUseCase()
        return analyzer.execute(headers, rows)
    
    def _get_default_field_mapping(self) -> FieldMapping:
        """Get default field mapping for Jira"""
        return FieldMapping(
            key_field="Issue key",
            summary_field="Summary",
            status_field="Status",
            created_field="Created",
            resolved_field="Resolved",
            story_points_field="Custom field (Story point estimate)",
            sprint_field="Sprint",
            assignee_field="Assignee",
            reporter_field="Reporter",
            issue_type_field="Issue Type",
            labels_field="Labels",
            time_estimate_field="Original Estimate",
            time_spent_field="Time Spent"
        )