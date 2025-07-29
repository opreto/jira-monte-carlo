"""Use case for analyzing data capabilities and determining available reports"""
import logging
from typing import List, Set

from ..domain.entities import Issue, Sprint
from ..domain.reporting_capabilities import (
    DataRequirement,
    REPORT_REQUIREMENTS,
    ReportCapability,
    ReportingCapabilities,
    ReportType,
)
from ..domain.repositories import IssueRepository, SprintRepository
from ..domain.value_objects import FieldMapping


logger = logging.getLogger(__name__)


class AnalyzeCapabilitiesUseCase:
    """Analyze available data to determine which reports can be generated"""

    def __init__(
        self,
        issue_repository: IssueRepository,
        sprint_repository: SprintRepository,
        field_mapping: FieldMapping,
    ):
        self.issue_repository = issue_repository
        self.sprint_repository = sprint_repository
        self.field_mapping = field_mapping

    def execute(self) -> ReportingCapabilities:
        """Analyze data and return available reporting capabilities"""
        # Get sample data to analyze
        issues = self.issue_repository.get_all()
        sprints = self.sprint_repository.get_all()

        # Analyze available fields
        available_fields = self._analyze_available_fields(issues, sprints)

        # Check each report's requirements
        all_reports = []
        available_reports = []

        for report_type, base_capability in REPORT_REQUIREMENTS.items():
            capability = self._check_report_capability(base_capability, available_fields)
            all_reports.append(capability)

            if capability.is_available:
                available_reports.append(capability)
                logger.info(
                    f"Report {capability.display_name} is available"
                    + (" (degraded mode)" if capability.degraded_mode else "")
                )
            else:
                logger.info(
                    f"Report {capability.display_name} is NOT available. "
                    f"Missing fields: {capability.missing_fields}"
                )

        # Calculate data quality score
        total_fields = len(DataRequirement)
        available_field_count = len(available_fields)
        data_quality_score = available_field_count / total_fields if total_fields > 0 else 0

        # Generate warnings
        warnings = self._generate_warnings(issues, sprints, available_fields)

        return ReportingCapabilities(
            available_reports=available_reports,
            all_reports=all_reports,
            data_quality_score=data_quality_score,
            warnings=warnings,
        )

    def _analyze_available_fields(self, issues: List[Issue], sprints: List[Sprint]) -> Set[DataRequirement]:
        """Analyze which data fields are available"""
        available = set()

        if not issues:
            return available

        # Check basic fields
        if all(issue.key for issue in issues[:10]):  # Sample first 10
            available.add(DataRequirement.KEY)

        if all(issue.status for issue in issues[:10]):
            available.add(DataRequirement.STATUS)

        # Check if created dates are real (not all the same fake date)
        sample_created_dates = [issue.created for issue in issues[:10] if issue.created]
        if sample_created_dates:
            # Check if dates vary by more than 1 minute (to detect fake dates with microsecond differences)
            min_date = min(sample_created_dates)
            max_date = max(sample_created_dates)
            date_range_seconds = (max_date - min_date).total_seconds()

            if date_range_seconds > 60:  # More than 1 minute variation
                available.add(DataRequirement.CREATED_DATE)
            else:
                logger.warning("Created dates appear to be missing or fake - aging analysis will be disabled")

        # Check optional fields with threshold (50% populated)
        sample_size = min(100, len(issues))
        sample_issues = issues[:sample_size]

        if sum(1 for i in sample_issues if i.resolved) > sample_size * 0.5:
            available.add(DataRequirement.RESOLVED_DATE)

        if sum(1 for i in sample_issues if i.updated) > sample_size * 0.5:
            available.add(DataRequirement.UPDATED_DATE)

        if sum(1 for i in sample_issues if i.story_points is not None) > sample_size * 0.5:
            available.add(DataRequirement.STORY_POINTS)

        if sum(1 for i in sample_issues if i.time_estimate is not None) > sample_size * 0.3:
            available.add(DataRequirement.TIME_ESTIMATE)

        if sum(1 for i in sample_issues if i.time_spent is not None) > sample_size * 0.3:
            available.add(DataRequirement.TIME_SPENT)

        if sum(1 for i in sample_issues if i.assignee) > sample_size * 0.5:
            available.add(DataRequirement.ASSIGNEE)

        if sum(1 for i in sample_issues if i.labels) > sample_size * 0.3:
            available.add(DataRequirement.LABELS)

        if sum(1 for i in sample_issues if i.issue_type) > sample_size * 0.8:
            available.add(DataRequirement.ISSUE_TYPE)

        # Check sprint data
        if sprints:
            available.add(DataRequirement.SPRINT)
            if all(s.start_date and s.end_date for s in sprints[:5]):
                available.add(DataRequirement.SPRINT_DATES)

        # Check for blocked status (in status or labels)
        blocked_keywords = ["blocked", "impediment", "waiting"]
        has_blocked_status = any(
            any(keyword in issue.status.lower() for keyword in blocked_keywords) for issue in sample_issues
        )
        has_blocked_labels = any(
            any(keyword in label.lower() for label in issue.labels for keyword in blocked_keywords)
            for issue in sample_issues
        )

        if has_blocked_status or has_blocked_labels:
            available.add(DataRequirement.BLOCKED_STATUS)

        return available

    def _check_report_capability(
        self, base_capability: ReportCapability, available_fields: Set[DataRequirement]
    ) -> ReportCapability:
        """Check if a report's requirements are met"""
        missing_required = base_capability.required_fields - available_fields

        # Check if report can run in degraded mode
        degraded_mode = False
        is_available = len(missing_required) == 0

        # Special cases for degraded mode
        if base_capability.report_type == ReportType.CYCLE_TIME_DISTRIBUTION:
            # Can estimate cycle time from status changes if updated date is available
            if DataRequirement.RESOLVED_DATE in missing_required and DataRequirement.UPDATED_DATE in available_fields:
                is_available = True
                degraded_mode = True
                missing_required.discard(DataRequirement.RESOLVED_DATE)

        return ReportCapability(
            report_type=base_capability.report_type,
            display_name=base_capability.display_name,
            description=base_capability.description,
            required_fields=base_capability.required_fields,
            optional_fields=base_capability.optional_fields,
            is_available=is_available,
            missing_fields=missing_required,
            degraded_mode=degraded_mode,
        )

    def _generate_warnings(
        self, issues: List[Issue], sprints: List[Sprint], available_fields: Set[DataRequirement]
    ) -> List[str]:
        """Generate warnings about data quality issues"""
        warnings = []

        if not issues:
            warnings.append("No issues found in the data")
            return warnings

        # Check for low story points coverage
        if DataRequirement.STORY_POINTS in available_fields:
            story_point_coverage = sum(1 for i in issues if i.story_points is not None) / len(issues)
            if story_point_coverage < 0.7:
                warnings.append(
                    f"Only {story_point_coverage:.0%} of issues have story points. "
                    "This may affect forecast accuracy."
                )

        # Check for missing resolved dates
        if DataRequirement.RESOLVED_DATE not in available_fields:
            warnings.append("No resolved dates found. Cycle time and throughput metrics will be unavailable.")

        # Check for sprint data
        if not sprints and DataRequirement.SPRINT not in available_fields:
            warnings.append("No sprint data found. Sprint-based analytics will be unavailable.")

        # Check for old data
        if issues:
            latest_date = max(i.created for i in issues if i.created)
            from datetime import datetime

            now = datetime.now(latest_date.tzinfo) if latest_date.tzinfo else datetime.now()
            days_old = (now - latest_date).days
            if days_old > 30:
                warnings.append(f"Latest data is {days_old} days old. Consider updating the export.")

        return warnings
