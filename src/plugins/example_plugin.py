"""Example plugin showing how to extend report capabilities"""

from typing import List, Optional, Set

from ..application.capability_analyzer import ReportCapabilityChecker
from ..application.plugin_registry import report_plugin_registry
from ..domain.entities import Issue, Sprint
from ..domain.reporting_capabilities import (
    DataRequirement,
    ReportCapability,
    ReportType,
)


class CustomSprintHealthChecker(ReportCapabilityChecker):
    """Custom sprint health capability checker with enhanced logic"""

    def __init__(self, report_type: ReportType, base_capability: ReportCapability):
        self.report_type = report_type
        self.base_capability = base_capability

    def check_availability(
        self,
        issues: List[Issue],
        sprints: List[Sprint],
        available_fields: Set[DataRequirement],
    ) -> Optional[ReportCapability]:
        """Enhanced sprint health availability check"""
        # Custom logic: Check if we have enough historical sprints
        if len(sprints) < 3:
            return ReportCapability(
                report_type=self.base_capability.report_type,
                display_name=self.base_capability.display_name,
                description=self.base_capability.description + " (Limited data)",
                required_fields=self.base_capability.required_fields,
                optional_fields=self.base_capability.optional_fields,
                is_available=False,
                missing_fields=set(),
                degraded_mode=False,
            )

        # Check standard requirements
        missing_required = self.base_capability.required_fields - available_fields

        # Can run in degraded mode without sprint dates
        degraded_mode = False
        if DataRequirement.SPRINT_DATES in missing_required:
            # We can still analyze sprint health without exact dates
            missing_required.discard(DataRequirement.SPRINT_DATES)
            degraded_mode = True

        is_available = len(missing_required) == 0

        return ReportCapability(
            report_type=self.base_capability.report_type,
            display_name=self.base_capability.display_name,
            description=self.base_capability.description,
            required_fields=self.base_capability.required_fields,
            optional_fields=self.base_capability.optional_fields,
            is_available=is_available,
            missing_fields=missing_required,
            degraded_mode=degraded_mode,
        )


def register_plugin():
    """Register this plugin's capability checkers"""
    # Register custom sprint health checker
    report_plugin_registry.register(ReportType.SPRINT_HEALTH, CustomSprintHealthChecker)


# Auto-register when imported
# In a real plugin system, this would be called by a plugin loader
# register_plugin()
