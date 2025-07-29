# Adding New Data Sources

This guide shows how to add support for new data sources to the Monte Carlo forecasting tool.

## Quick Start

To add a new data source, you need to:

1. Create a new file in `src/infrastructure/`
2. Implement the `DataSource` interface
3. Register it in the factory
4. (Optional) Add auto-detection

## Complete Example: Adding GitHub Issues

### 1. Create the Implementation

```python
# src/infrastructure/github_data_source.py
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

from ..domain.data_sources import DataSource, DataSourceInfo, DataSourceType
from ..domain.entities import Issue, Sprint
from ..domain.value_objects import FieldMapping


class GitHubDataSource(DataSource):
    """Data source for GitHub Issues via REST API"""
    
    def __init__(self, token: str = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
    
    def get_info(self) -> DataSourceInfo:
        return DataSourceInfo(
            type=DataSourceType.GITHUB,
            name="GitHub Issues",
            description="GitHub Issues and Projects",
            supported_features=["milestones", "projects", "labels"],
            file_extensions=[]  # API-based, no files
        )
    
    def detect_format(self, file_path: Path) -> bool:
        # Detects GitHub repo URLs or owner/repo format
        path_str = str(file_path)
        return (
            'github.com' in path_str or 
            bool(re.match(r'^[\w-]+/[\w-]+$', path_str))
        )
    
    def parse(self, file_path: Path) -> Tuple[List[Issue], List[Sprint]]:
        # Parse owner/repo from path
        owner, repo = self._parse_repo_info(file_path)
        
        # Fetch issues
        raw_issues = self._fetch_issues(owner, repo)
        issues = [self._convert_issue(i) for i in raw_issues]
        
        # Fetch milestones as sprints
        raw_milestones = self._fetch_milestones(owner, repo)
        sprints = [self._convert_milestone(m) for m in raw_milestones]
        
        return issues, sprints
    
    def get_default_field_mapping(self) -> FieldMapping:
        return FieldMapping(
            key_field="number",
            summary_field="title",
            status_field="state",
            created_field="created_at",
            updated_field="updated_at",
            resolved_field="closed_at",
            assignee_field="assignee.login",
            labels_field="labels",
            sprint_field="milestone.title"
        )
    
    def _convert_issue(self, github_issue: dict) -> Issue:
        # Convert GitHub issue to domain Issue
        return Issue(
            key=f"#{github_issue['number']}",
            summary=github_issue['title'],
            status='Done' if github_issue['state'] == 'closed' else 'Open',
            created=datetime.fromisoformat(github_issue['created_at']),
            # ... map other fields
        )
```

### 2. Add the Type Enum

```python
# src/domain/data_sources.py
class DataSourceType(Enum):
    JIRA_CSV = "jira_csv"
    LINEAR_CSV = "linear_csv"
    GITHUB = "github"  # Add this
```

### 3. Register in Factory

```python
# src/infrastructure/data_source_factory.py
from .github_data_source import GitHubDataSource

class DefaultDataSourceFactory(DataSourceFactory):
    def __init__(self):
        super().__init__()
        self.sources = {
            DataSourceType.JIRA_CSV: JiraDataSource,
            DataSourceType.LINEAR_CSV: LinearDataSource,
            DataSourceType.GITHUB: GitHubDataSource,  # Add this
        }
```

### 4. Use It

```bash
# CLI automatically detects GitHub format
montecarlo --csv-file opreto/montecarlo --format github

# Or with multiple sources
montecarlo --csv-file jira-export.csv \
           --csv-file opreto/montecarlo \
           --output combined-report.html
```

## Common Data Source Types

### File-Based Sources
- CSV exports (Jira, Linear, Azure DevOps)
- XML exports (Jira, TestRail)
- JSON exports (Monday.com, Trello)

### API-Based Sources
- REST APIs (Jira, GitHub, GitLab)
- GraphQL APIs (Linear, Monday.com)
- Webhooks (real-time updates)

### Database Sources
- Atlassian Data Lake (SQL)
- Direct database connections
- Data warehouses

## Testing Your Data Source

```python
# tests/unit/test_github_data_source.py
def test_github_parse():
    source = GitHubDataSource(token="fake-token")
    
    # Mock the API calls
    with patch.object(source, '_fetch_issues') as mock_fetch:
        mock_fetch.return_value = [
            {'number': 1, 'title': 'Test Issue', 'state': 'open'}
        ]
        
        issues, sprints = source.parse(Path('owner/repo'))
        
        assert len(issues) == 1
        assert issues[0].key == '#1'
```

## Best Practices

1. **Handle Authentication**: Use environment variables or config files
2. **Implement Pagination**: For API sources, handle large datasets
3. **Cache Responses**: Avoid hitting rate limits
4. **Validate Data**: Check required fields exist
5. **Map Statuses**: Convert to standard todo/in_progress/done
6. **Handle Errors**: Graceful degradation for missing fields

## Field Mapping

Each data source should provide sensible defaults:

```python
def get_default_field_mapping(self) -> FieldMapping:
    return FieldMapping(
        key_field="id",          # Unique identifier
        summary_field="title",    # Issue title
        status_field="status",    # Current status
        # ... map all fields
    )
```

Users can override mappings via CLI:

```bash
montecarlo --csv-file github:owner/repo \
           --key-field number \
           --status-field state \
           --story-points-field size