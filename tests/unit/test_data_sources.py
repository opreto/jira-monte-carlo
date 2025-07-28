"""Tests for data source abstraction"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.domain.data_sources import DataSourceType, DataSourceInfo
from src.domain.entities import Issue, Sprint
from src.domain.value_objects import FieldMapping
from src.domain.entities import IssueStatus
from src.infrastructure.data_source_factory import DefaultDataSourceFactory
from src.infrastructure.jira_data_source import JiraCSVDataSource
from src.infrastructure.linear_data_source import LinearCSVDataSource


class TestDataSourceFactory:
    def test_create_jira_source(self):
        factory = DefaultDataSourceFactory()
        source = factory.create(DataSourceType.JIRA_CSV)
        assert isinstance(source, JiraCSVDataSource)

    def test_create_linear_source(self):
        factory = DefaultDataSourceFactory()
        source = factory.create(DataSourceType.LINEAR_CSV)
        assert isinstance(source, LinearCSVDataSource)

    def test_create_with_field_mapping(self):
        factory = DefaultDataSourceFactory()
        field_mapping = FieldMapping(
            key_field="ID",
            summary_field="Title",
            status_field="State"
        )
        source = factory.create(DataSourceType.JIRA_CSV, field_mapping)
        assert isinstance(source, JiraCSVDataSource)
        assert source.field_mapping == field_mapping

    def test_create_unknown_source(self):
        factory = DefaultDataSourceFactory()
        # Can't create invalid enum, so test with a valid but unregistered type
        with pytest.raises(ValueError, match="Unknown data source type"):
            factory.create(DataSourceType.JIRA_XML)  # Not implemented

    def test_get_available_sources(self):
        factory = DefaultDataSourceFactory()
        sources = factory.get_available_sources()
        
        assert len(sources) >= 2
        source_types = [s.source_type for s in sources]
        assert DataSourceType.JIRA_CSV in source_types
        assert DataSourceType.LINEAR_CSV in source_types

    @patch('src.infrastructure.jira_data_source.JiraCSVDataSource.detect_format')
    @patch('src.infrastructure.linear_data_source.LinearCSVDataSource.detect_format')
    def test_detect_source_type_jira(self, mock_linear_detect, mock_jira_detect):
        mock_jira_detect.return_value = True
        mock_linear_detect.return_value = False
        
        factory = DefaultDataSourceFactory()
        source_type = factory.detect_source_type(Path("test.csv"))
        
        assert source_type == DataSourceType.JIRA_CSV

    @patch('src.infrastructure.jira_data_source.JiraCSVDataSource.detect_format')
    @patch('src.infrastructure.linear_data_source.LinearCSVDataSource.detect_format')
    def test_detect_source_type_linear(self, mock_linear_detect, mock_jira_detect):
        mock_jira_detect.return_value = False
        mock_linear_detect.return_value = True
        
        factory = DefaultDataSourceFactory()
        source_type = factory.detect_source_type(Path("test.csv"))
        
        assert source_type == DataSourceType.LINEAR_CSV

    @patch('src.infrastructure.jira_data_source.JiraCSVDataSource.detect_format')
    @patch('src.infrastructure.linear_data_source.LinearCSVDataSource.detect_format')
    def test_detect_source_type_unknown(self, mock_linear_detect, mock_jira_detect):
        mock_jira_detect.return_value = False
        mock_linear_detect.return_value = False
        
        factory = DefaultDataSourceFactory()
        source_type = factory.detect_source_type(Path("test.csv"))
        
        assert source_type is None


class TestJiraDataSource:
    def test_get_info(self):
        source = JiraCSVDataSource()
        info = source.get_info()
        
        assert info.source_type == DataSourceType.JIRA_CSV
        assert info.name == "Jira CSV Export"
        assert len(info.file_extensions) > 0
        assert info.default_field_mapping is not None

    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader')
    def test_detect_format_success(self, mock_csv_reader, mock_open):
        # Setup mock file and CSV reader
        mock_reader_instance = Mock()
        mock_reader_instance.__next__ = Mock(return_value=[
            "Issue key", "Summary", "Status", "Sprint", "Story Points",
            "Created", "Updated", "Priority", "Reporter", "Assignee"
        ])
        mock_csv_reader.return_value = mock_reader_instance
        
        source = JiraCSVDataSource()
        result = source.detect_format(Path("test.csv"))
        
        assert result is True

    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader')
    def test_detect_format_failure(self, mock_csv_reader, mock_open):
        # Setup mock file and CSV reader with non-Jira headers
        mock_reader_instance = Mock()
        mock_reader_instance.__next__ = Mock(return_value=[
            "ID", "Title", "State"
        ])
        mock_csv_reader.return_value = mock_reader_instance
        
        source = JiraCSVDataSource()
        result = source.detect_format(Path("test.csv"))
        
        assert result is False

    @patch('builtins.open')
    def test_detect_format_error(self, mock_open):
        mock_open.side_effect = Exception("Read error")
        
        source = JiraCSVDataSource()
        result = source.detect_format(Path("test.csv"))
        
        assert result is False


class TestLinearDataSource:
    def test_get_info(self):
        source = LinearCSVDataSource()
        info = source.get_info()
        
        assert info.source_type == DataSourceType.LINEAR_CSV
        assert info.name == "Linear CSV Export"
        assert len(info.file_extensions) > 0
        assert info.default_field_mapping is not None

    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader')
    def test_detect_format_success(self, mock_csv_reader, mock_open):
        # Setup mock file and CSV reader with Linear headers
        mock_reader_instance = Mock()
        mock_reader_instance.__next__ = Mock(return_value=[
            "ID", "Title", "Status", "Cycle", "Estimate", "Completed", "Project", "Team"
        ])
        mock_csv_reader.return_value = mock_reader_instance
        
        source = LinearCSVDataSource()
        result = source.detect_format(Path("test.csv"))
        
        assert result is True

    @patch('builtins.open', new_callable=MagicMock)
    @patch('csv.reader')
    def test_detect_format_failure(self, mock_csv_reader, mock_open):
        # Setup mock file and CSV reader with non-Linear headers
        mock_reader_instance = Mock()
        mock_reader_instance.__next__ = Mock(return_value=[
            "Issue key", "Summary", "State"
        ])
        mock_csv_reader.return_value = mock_reader_instance
        
        source = LinearCSVDataSource()
        result = source.detect_format(Path("test.csv"))
        
        assert result is False

    def test_status_mapping(self):
        source = LinearCSVDataSource()
        
        # Test various Linear statuses through the mapping
        assert source.LINEAR_STATUS_MAPPING["backlog"] == IssueStatus.TODO
        assert source.LINEAR_STATUS_MAPPING["todo"] == IssueStatus.TODO
        assert source.LINEAR_STATUS_MAPPING["in progress"] == IssueStatus.IN_PROGRESS
        assert source.LINEAR_STATUS_MAPPING["in review"] == IssueStatus.IN_PROGRESS
        assert source.LINEAR_STATUS_MAPPING["done"] == IssueStatus.DONE
        assert source.LINEAR_STATUS_MAPPING["canceled"] == IssueStatus.DONE
        # Test _is_done_status method which is the actual implementation
        assert source._is_done_status("done") is True
        assert source._is_done_status("todo") is False

    def test_parse_estimate_numeric(self):
        source = LinearCSVDataSource()
        
        assert source._parse_estimate("5") == 5.0
        assert source._parse_estimate("3.5") == 3.5
        assert source._parse_estimate("0") == 0.0

    def test_parse_estimate_tshirt(self):
        source = LinearCSVDataSource()
        
        assert source._parse_estimate("XS") == 1.0
        assert source._parse_estimate("S") == 2.0
        assert source._parse_estimate("M") == 3.0
        assert source._parse_estimate("L") == 5.0
        assert source._parse_estimate("XL") == 8.0
        assert source._parse_estimate("XXL") == 13.0
        assert source._parse_estimate("xs") == 1.0  # Case insensitive

    def test_parse_estimate_invalid(self):
        source = LinearCSVDataSource()
        
        assert source._parse_estimate("") is None
        assert source._parse_estimate(None) is None
        assert source._parse_estimate("invalid") is None

    @patch('src.infrastructure.linear_data_source.LinearCSVDataSource._create_monthly_sprints')
    @patch('polars.read_csv')
    def test_parse_with_synthetic_sprints(self, mock_read_csv, mock_create_sprints):
        # Mock DataFrame with no cycles
        mock_df = Mock()
        mock_df.columns = ["ID", "Title", "Status", "Cycle", "Estimate", "Completed"]
        mock_df.shape = (10, 6)
        
        # Mock row data
        mock_row = {
            "ID": "LIN-1",
            "Title": "Test Issue",
            "Status": "done",
            "Cycle": None,
            "Estimate": "5",
            "Completed": "2024-01-01"
        }
        # Linear uses iter_rows(named=True)
        mock_df.iter_rows = Mock(return_value=[mock_row])
        mock_read_csv.return_value = mock_df
        
        # Mock synthetic sprints
        mock_sprint = Sprint(
            name="Month 2024-01",
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 31),
            completed_points=20.0,
            completed_issues=[]
        )
        mock_create_sprints.return_value = [mock_sprint]
        
        source = LinearCSVDataSource()
        issues, sprints = source.parse_file(Path("test.csv"))
        
        assert len(issues) == 1
        assert len(sprints) == 1
        assert issues[0].key == "LIN-1"
        assert sprints[0].name == "Month 2024-01"
        mock_create_sprints.assert_called_once()