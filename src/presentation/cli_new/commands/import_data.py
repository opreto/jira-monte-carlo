"""Import data command for CLI"""

from pathlib import Path
from typing import Optional
from rich.console import Console

from .base import Command, CommandContext, CommandResult
from ...domain.value_objects import FieldMapping
from ...domain.data_sources import DataSourceType


class ImportDataCommand(Command):
    """Command to import data from various sources"""

    def __init__(self, console: Optional[Console] = None):
        super().__init__(
            name="import_data",
            description="Import project data from CSV or API sources",
        )
        self.console = console or Console()

    def validate(self, context: CommandContext) -> Optional[str]:
        """Validate import arguments"""
        args = context.args

        # Check if CSV paths are provided
        if not args.csv_paths:
            return "No CSV files specified"

        # Validate CSV paths exist
        for csv_path in args.csv_paths:
            if not Path(csv_path).exists():
                return f"CSV file not found: {csv_path}"

        # Validate source type if specified
        if args.source and args.source not in ["jira", "linear", "auto"]:
            return f"Invalid source type: {args.source}"

        return None

    def execute(self, context: CommandContext) -> CommandResult:
        """Execute data import"""
        args = context.args

        # Get dependencies
        import_use_case = context.get_dependency("import_use_case")
        analyze_use_case = context.get_dependency("analyze_use_case")
        data_source_factory = context.get_dependency("data_source_factory")

        # Process multiple files if provided
        if len(args.csv_paths) > 1:
            return self._handle_multi_project_import(context)

        # Single file processing
        csv_path = args.csv_paths[0]
        source_type = self._determine_source_type(args, csv_path, data_source_factory)

        # Create field mapping from arguments
        field_mapping = self._create_field_mapping(args)

        try:
            self.console.print("\n[yellow]Importing data...[/yellow]")

            # Execute import
            issues, sprints = import_use_case.execute(
                file_path=csv_path, source_type=source_type, field_mapping=field_mapping
            )

            self.console.print(
                f"[green]✓ Loaded {len(issues)} issues and {len(sprints)} sprints[/green]"
            )

            # Run analysis if requested
            if args.analyze_only:
                analysis_result = analyze_use_case.execute(csv_path, source_type)
                return CommandResult(
                    success=True,
                    message="Data analysis completed",
                    data={
                        "analysis_result": analysis_result,
                        "issues": issues,
                        "sprints": sprints,
                    },
                )

            return CommandResult(
                success=True,
                message="Data imported successfully",
                data={
                    "issues": issues,
                    "sprints": sprints,
                    "source_type": source_type,
                    "field_mapping": field_mapping,
                },
            )

        except ValueError as e:
            return CommandResult(
                success=False, message=f"Import failed: {str(e)}", error=e
            )

    def _handle_multi_project_import(self, context: CommandContext) -> CommandResult:
        """Handle multiple project imports"""
        # Delegate to multi-project orchestrator
        # This will be implemented in the orchestrator module
        return CommandResult(
            success=False,
            message="Multi-project import not yet implemented in refactored version",
        )

    def _determine_source_type(
        self, args, csv_path: Path, data_source_factory
    ) -> DataSourceType:
        """Determine the source type for the CSV file"""
        if args.source == "auto" or not args.source:
            # Auto-detect source type
            try:
                # Quick analysis to determine type
                import polars as pl

                df = pl.scan_csv(str(csv_path)).head(5).collect()
                columns = df.columns

                # Simple heuristic for detection
                if any("issue" in col.lower() for col in columns):
                    if any("sprint" in col.lower() for col in columns):
                        return DataSourceType.JIRA_CSV
                    else:
                        return DataSourceType.LINEAR_CSV
                else:
                    # Default to Jira
                    return DataSourceType.JIRA_CSV

            except Exception:
                # Default to Jira if detection fails
                return DataSourceType.JIRA_CSV

        # Map string to enum
        source_map = {
            "jira": DataSourceType.JIRA_CSV,
            "linear": DataSourceType.LINEAR_CSV,
            "jira-api": DataSourceType.JIRA_API,
        }

        return source_map.get(args.source, DataSourceType.JIRA_CSV)

    def _create_field_mapping(self, args) -> FieldMapping:
        """Create field mapping from command line arguments"""
        return FieldMapping(
            id_field=args.key_field,
            title_field=args.summary_field,
            estimation_field=args.points_field,
            velocity_field=args.velocity_field,
            sprint_field=args.sprint_field,
            status_field=args.status_field,
            created_date_field=args.created_field,
            resolved_date_field=args.resolved_field,
            labels_field=args.labels_field,
            issue_type_field=args.type_field,
            assignee_field=args.assignee_field,
            project_field=args.project_field,
            blocked_field=args.blocked_field,
        )
