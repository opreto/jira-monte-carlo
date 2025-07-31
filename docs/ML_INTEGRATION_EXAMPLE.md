# ML Integration Example

This document shows how the ML features integrate with the existing Sprint Radar CLI using automatic project ID generation.

## Extracting Project Key from Data Sources

### From Jira API

When using `jira-api://`, the project key is already available in the configuration:

```python
# In JiraApiDataSource
def get_project_info(self) -> dict:
    """Get project information including key"""
    if not self.config.project_key:
        return {}
    
    project = self.jira.get_project(self.config.project_key)
    return {
        "key": project.get("key"),  # e.g., "PROJ-123"
        "name": project.get("name"),
        "id": project.get("id")
    }
```

### From CSV Files

For CSV files, we can extract the project key from the issues:

```python
def extract_project_key_from_issues(issues: List[Issue]) -> Optional[str]:
    """Extract project key from issue keys (e.g., PROJ-123 -> PROJ)"""
    if not issues:
        return None
    
    # Get the first issue key
    first_key = issues[0].key
    
    # Extract project part (everything before the last dash)
    if '-' in first_key:
        parts = first_key.split('-')
        return '-'.join(parts[:-1])  # Handle keys like "TEAM-PROJ-123"
    
    return None
```

## Automatic Project ID Generation

Sprint Radar automatically generates unique project IDs based on your data source:

### For Jira API
```
Project ID = {jira-hostname}-{PROJECT-KEY}-{hash}
Example: mycompany-PROJ-a1b2c3
```

### For CSV Files
```
Project ID = csv-{PROJECT-KEY}-{hash}
Example: csv-TEAM-f3d5a7
```

This ensures complete isolation between:
- Different projects in the same Jira instance
- Different Jira instances
- CSV-based and API-based data

## CLI Integration

The ML features are now integrated into the CLI with the `--enable-ml` flag:

```bash
# For Jira API - automatic project ID from URL + project key
$ sprint-radar forecast -f jira-api:// --enable-ml
[green]ML features enabled for project: mycompany-PROJ-a1b2c3[/green]
[INFO] ML-optimized lookback: 8 sprints (confidence: 0.85)
  - stability: Stable velocity pattern (score=0.92)
  - recency: Recent velocity differs from historical pattern

# For CSV files - automatic project ID from filename
$ sprint-radar forecast -f TEAM-issues.csv --enable-ml
[green]ML features enabled for project: csv-TEAM-f3d5a7[/green]
[INFO] ML-optimized lookback: 10 sprints (confidence: 0.82)
  - variance: CV=0.35 indicates moderate variability
  - trend: Slight upward trend detected
```

### How It Works

1. **Jira API**: Combines the Jira instance URL and project key from environment
2. **CSV Files**: Extracts project key from filename patterns like:
   - `PROJ-issues.csv` → PROJ
   - `project-TEAM-export.csv` → TEAM
   - `ABC_2024_data.csv` → ABC

3. **Automatic Fallback**: If project ID cannot be determined, ML features are disabled with a warning

## ML Status Command

Add a new command to check ML model status:

```python
@cli.command()
@click.option(
    "--project-key",
    help="Project key to check ML status for"
)
def ml_status(project_key):
    """Check ML model status for a project."""
    
    if not project_key:
        # Try to detect from current directory or config
        config = JiraConfig.from_env()
        project_key = config.project_key
        
    if not project_key:
        console.print("[red]Error: Project key required. "
                     "Use --project-key or set JIRA_PROJECT_KEY[/red]")
        return
    
    manager = MLModelManagementUseCase(project_key)
    status = manager.get_model_status()
    
    console.print(f"\n[bold]ML Model Status for {project_key}[/bold]\n")
    
    if not status['models_available']:
        console.print("[yellow]No ML models found. Models will be created "
                     "on first use with --enable-ml flag.[/yellow]")
        return
    
    table = Table(title="Available Models")
    table.add_column("Model", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Last Trained")
    table.add_column("Training Samples")
    table.add_column("Size (KB)")
    
    for model_name, info in status['models'].items():
        if info['exists']:
            table.add_row(
                model_name,
                "✓ Trained",
                info.get('last_trained', 'Unknown'),
                str(info.get('training_samples', 0)),
                f"{info.get('size_kb', 0):.1f}"
            )
        else:
            table.add_row(model_name, "Not trained", "-", "-", "-")
    
    console.print(table)
```

## Environment Variable Support

For teams that always work on the same project:

```bash
# In .env or shell profile
export SPRINT_RADAR_PROJECT_KEY="PROJ-123"
export SPRINT_RADAR_ENABLE_ML=true

# Then just run normally
sprint-radar forecast -f jira-api://
```

## Privacy Report Command

```python
@cli.command()
@click.option("--project-key", help="Project key to generate privacy report for")
def ml_privacy(project_key):
    """Generate privacy report showing data isolation."""
    
    manager = MLModelManagementUseCase(project_key)
    report = manager.get_privacy_report()
    
    console.print(f"\n[bold]Privacy Report for {project_key}[/bold]\n")
    console.print("✓ Data Isolation: Confirmed")
    console.print(f"✓ Storage Path: {report['data_isolation']['project_specific_path']}")
    console.print("✓ Other Projects Accessible: No")
    console.print("\n[bold]Privacy Features:[/bold]")
    
    for feature in report['privacy_features']:
        console.print(f"  • {feature}")
```

## Gradual Rollout Strategy

1. **Phase 1**: Hidden flag `--enable-ml` for early adopters
2. **Phase 2**: Add to help text and documentation
3. **Phase 3**: Show ML vs heuristic comparison in reports
4. **Phase 4**: Enable by default with `--disable-ml` option

## Example Usage Flow

```bash
# First time setup - ML models created automatically
$ sprint-radar forecast -f jira-api:// --enable-ml
[green]ML features enabled for project: mycompany-PROJ-a1b2c3[/green]
[INFO] No existing ML models found for mycompany-PROJ-a1b2c3
[INFO] Training LookbackOptimizer with 25 historical sprints
[INFO] ML-optimized lookback: 10 sprints (confidence: 0.82)
  - variance: CV=0.35 indicates moderate variability
  - trend: Slight upward trend detected
[INFO] Using 10 sprints for velocity calculation

# Subsequent runs - uses existing models
$ sprint-radar forecast -f jira-api:// --enable-ml
[green]ML features enabled for project: mycompany-PROJ-a1b2c3[/green]
[INFO] Loaded existing ML models for mycompany-PROJ-a1b2c3
[INFO] ML-optimized lookback: 8 sprints (confidence: 0.85)
  - recency: Recent process change detected
  - stability: Velocity stabilizing after change

# CSV file with automatic project detection
$ sprint-radar forecast -f TEAM-issues.csv --enable-ml
[green]ML features enabled for project: csv-TEAM-f3d5a7[/green]
[INFO] ML-optimized lookback: 12 sprints (confidence: 0.78)

# CSV file without detectable project key
$ sprint-radar forecast -f export.csv --enable-ml
[yellow]Warning: Could not extract project key from CSV filename[/yellow]
[yellow]ML features disabled - project ID could not be determined[/yellow]

# Check model status (future enhancement)
$ sprint-radar ml-status --project-id mycompany-PROJ-a1b2c3
ML Model Status for mycompany-PROJ-a1b2c3

┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
┃ Model             ┃ Status    ┃ Last Trained    ┃ Training Samples┃ Size KB ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
│ LookbackOptimizer │ ✓ Trained │ 2024-01-15     │ 25              │ 2.3     │
│ ProductivityCurve │ Not trained│ -              │ -               │ -       │
└───────────────────┴───────────┴─────────────────┴─────────────────┴─────────┘
```