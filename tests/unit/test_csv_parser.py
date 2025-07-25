import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import csv

from src.domain.value_objects import FieldMapping
from src.infrastructure.csv_parser import JiraCSVParser, CSVFieldAnalyzer


class TestJiraCSVParser:
    def test_parse_simple_csv(self):
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow([
                "Issue key", "Summary", "Issue Type", "Status", 
                "Created", "Resolved", "Custom field (Story Points)"
            ])
            writer.writerow([
                "TEST-1", "Test Issue 1", "Story", "Done",
                "01/Jan/23 10:00 AM", "05/Jan/23 2:00 PM", "5"
            ])
            writer.writerow([
                "TEST-2", "Test Issue 2", "Bug", "In Progress",
                "02/Jan/23 11:00 AM", "", "3"
            ])
            temp_path = Path(f.name)
        
        try:
            # Setup
            field_mapping = FieldMapping(
                key_field="Issue key",
                summary_field="Summary",
                issue_type_field="Issue Type",
                status_field="Status",
                created_field="Created",
                resolved_field="Resolved",
                story_points_field="Custom field (Story Points)"
            )
            
            parser = JiraCSVParser(field_mapping)
            
            # Execute
            issues = parser.parse_file(temp_path)
            
            # Assert
            assert len(issues) == 2
            
            # Check first issue
            assert issues[0].key == "TEST-1"
            assert issues[0].summary == "Test Issue 1"
            assert issues[0].issue_type == "Story"
            assert issues[0].status == "Done"
            assert issues[0].story_points == 5.0
            assert issues[0].resolved is not None
            
            # Check second issue
            assert issues[1].key == "TEST-2"
            assert issues[1].status == "In Progress"
            assert issues[1].story_points == 3.0
            assert issues[1].resolved is None
            
        finally:
            temp_path.unlink()
    
    def test_parse_date_formats(self):
        parser = JiraCSVParser(FieldMapping())
        
        # Test various date formats
        date1 = parser._parse_date("13/Jun/25 6:20 AM")
        assert date1 is not None
        assert date1.year == 2025
        assert date1.month == 6
        assert date1.day == 13
        
        date2 = parser._parse_date("2023-01-15 14:30:00")
        assert date2 is not None
        assert date2.year == 2023
        
        # Test invalid date
        assert parser._parse_date("invalid") is None
        assert parser._parse_date("") is None
        assert parser._parse_date(None) is None
    
    def test_parse_float_values(self):
        parser = JiraCSVParser(FieldMapping())
        
        # Test numeric values
        assert parser._parse_float("5") == 5.0
        assert parser._parse_float("3.5") == 3.5
        
        # Test time formats
        assert parser._parse_float("2d") == 16.0  # 2 days * 8 hours
        assert parser._parse_float("4h") == 4.0
        assert parser._parse_float("1d 4h") == 12.0
        
        # Test invalid values
        assert parser._parse_float("") is None
        assert parser._parse_float(None) is None
        assert parser._parse_float("invalid") is None
    
    def test_parse_labels(self):
        parser = JiraCSVParser(FieldMapping())
        
        assert parser._parse_labels("bug, frontend, urgent") == ["bug", "frontend", "urgent"]
        assert parser._parse_labels("single") == ["single"]
        assert parser._parse_labels("") == []
        assert parser._parse_labels(None) == []


class TestCSVFieldAnalyzer:
    def test_analyze_headers(self):
        # Create a temporary CSV with various headers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow([
                "Issue key", "Issue id", "Summary", "Title",
                "Status", "State", "Created", "Updated", "Resolved",
                "Story Points", "Time Estimate", "Original Estimate",
                "Assignee", "Reporter", "Owner",
                "Sprint", "Current Sprint",
                "Custom field (Story Points)",
                "Custom field (Team)",
                "Random Field"
            ])
            temp_path = Path(f.name)
        
        try:
            # Execute
            categorized = CSVFieldAnalyzer.analyze_headers(temp_path)
            
            # Assert categorization
            assert "Issue key" in categorized["key_candidates"]
            assert "Issue id" in categorized["key_candidates"]
            
            assert "Summary" in categorized["summary_candidates"]
            assert "Title" in categorized["summary_candidates"]
            
            assert "Status" in categorized["status_candidates"]
            assert "State" in categorized["status_candidates"]
            
            assert "Created" in categorized["date_candidates"]
            assert "Updated" in categorized["date_candidates"]
            assert "Resolved" in categorized["date_candidates"]
            
            assert "Story Points" in categorized["numeric_candidates"]
            assert "Time Estimate" in categorized["numeric_candidates"]
            
            assert "Assignee" in categorized["user_candidates"]
            assert "Reporter" in categorized["user_candidates"]
            
            assert "Sprint" in categorized["sprint_candidates"]
            assert "Current Sprint" in categorized["sprint_candidates"]
            
            assert "Custom field (Story Points)" in categorized["custom_fields"]
            assert "Custom field (Team)" in categorized["custom_fields"]
            
        finally:
            temp_path.unlink()