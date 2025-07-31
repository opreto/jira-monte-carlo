"""Import controller for presentation layer"""

from typing import Dict, Any

from .base import Controller
from ..models.requests import ImportDataRequest
from ..models.responses import ImportDataResponse
from ...domain.value_objects import FieldMapping
from ...domain.data_sources import DataSourceType


class ImportController(Controller[ImportDataRequest, ImportDataResponse]):
    """Controller for handling data import operations"""

    def __init__(self, import_use_case, analyze_use_case, data_source_factory):
        """Initialize import controller

        Args:
            import_use_case: Use case for importing data
            analyze_use_case: Use case for analyzing data sources
            data_source_factory: Factory for creating data sources
        """
        super().__init__("ImportData")
        self.import_use_case = import_use_case
        self.analyze_use_case = analyze_use_case
        self.data_source_factory = data_source_factory

    def handle(self, request: ImportDataRequest) -> ImportDataResponse:
        """Handle import request

        Args:
            request: Import request model

        Returns:
            Import response model
        """
        try:
            # Determine source type
            source_type = self._determine_source_type(request)

            # Create field mapping
            field_mapping = self._create_field_mapping(request)

            # Handle analysis-only request
            if request.analyze_only:
                return self._handle_analysis(request, source_type)

            # Execute import
            issues, sprints = self.import_use_case.execute(
                file_path=request.file_paths[0],  # Single file for now
                source_type=source_type,
                field_mapping=field_mapping,
            )

            # Calculate data quality
            data_quality = self._calculate_data_quality(issues, sprints)

            return ImportDataResponse(
                success=True,
                issues_count=len(issues),
                sprints_count=len(sprints),
                source_type=source_type.value,
                field_mapping_used=request.field_mapping or {},
                data_quality_score=data_quality["score"],
                missing_fields=data_quality["missing_fields"],
            )

        except Exception as e:
            self._logger.error(f"Import failed: {str(e)}")
            return ImportDataResponse(
                success=False,
                issues_count=0,
                sprints_count=0,
                source_type="unknown",
                field_mapping_used={},
                errors=[str(e)],
            )

    def _determine_source_type(self, request: ImportDataRequest) -> DataSourceType:
        """Determine the source type from request

        Args:
            request: Import request

        Returns:
            Data source type enum
        """
        if request.source_type == "auto":
            # Auto-detect logic would go here
            # For now, default to Jira
            return DataSourceType.JIRA_CSV

        source_map = {
            "jira": DataSourceType.JIRA_CSV,
            "linear": DataSourceType.LINEAR_CSV,
            "jira-api": DataSourceType.JIRA_API,
        }

        return source_map.get(request.source_type, DataSourceType.JIRA_CSV)

    def _create_field_mapping(self, request: ImportDataRequest) -> FieldMapping:
        """Create field mapping from request

        Args:
            request: Import request

        Returns:
            Field mapping value object
        """
        return FieldMapping(
            id_field=request.key_field,
            title_field=request.summary_field,
            estimation_field=request.points_field,
            velocity_field=request.velocity_field,
            sprint_field=request.sprint_field,
            status_field=request.status_field,
            created_date_field=request.created_field,
            resolved_date_field=request.resolved_field,
            labels_field=request.labels_field,
            issue_type_field=request.type_field,
            assignee_field=request.assignee_field,
            project_field=request.project_field,
            blocked_field=request.blocked_field,
        )

    def _handle_analysis(
        self, request: ImportDataRequest, source_type: DataSourceType
    ) -> ImportDataResponse:
        """Handle analysis-only request

        Args:
            request: Import request
            source_type: Detected source type

        Returns:
            Import response with analysis results
        """
        analysis_result = self.analyze_use_case.execute(
            request.file_paths[0], source_type
        )

        return ImportDataResponse(
            success=True,
            issues_count=0,
            sprints_count=0,
            source_type=source_type.value,
            field_mapping_used={},
            analysis_results={
                "structure": analysis_result.structure_analysis,
                "field_detection": analysis_result.field_detection,
                "data_quality": analysis_result.data_quality_assessment,
            },
        )

    def _calculate_data_quality(self, issues: list, sprints: list) -> Dict[str, Any]:
        """Calculate data quality metrics

        Args:
            issues: List of issues
            sprints: List of sprints

        Returns:
            Data quality metrics
        """
        # Simplified data quality calculation
        total_fields = 0
        missing_fields = {}

        for issue in issues:
            for field, value in issue.__dict__.items():
                total_fields += 1
                if value is None or value == "":
                    missing_fields[field] = missing_fields.get(field, 0) + 1

        # Calculate score (0-1)
        if total_fields > 0:
            missing_ratio = sum(missing_fields.values()) / total_fields
            score = 1.0 - missing_ratio
        else:
            score = 0.0

        return {"score": score, "missing_fields": missing_fields}
