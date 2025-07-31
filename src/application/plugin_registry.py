"""Plugin registry for extensible report and metric capabilities"""

import logging
from typing import Dict, List, Type

from ..domain.reporting_capabilities import ReportType
from .capability_analyzer import ReportCapabilityChecker

logger = logging.getLogger(__name__)


class ReportPluginRegistry:
    """Registry for report capability checker plugins"""

    def __init__(self):
        self._checkers: Dict[ReportType, Type[ReportCapabilityChecker]] = {}
        self._registered_plugins: List[str] = []

    def register(self, report_type: ReportType, checker_class: Type[ReportCapabilityChecker]) -> None:
        """Register a custom capability checker for a report type"""
        if report_type in self._checkers:
            logger.warning(f"Overriding existing checker for {report_type} with {checker_class.__name__}")

        self._checkers[report_type] = checker_class
        plugin_name = f"{checker_class.__module__}.{checker_class.__name__}"
        self._registered_plugins.append(plugin_name)

        logger.info(f"Registered capability checker {plugin_name} for {report_type}")

    def get_checker(self, report_type: ReportType) -> Type[ReportCapabilityChecker]:
        """Get the registered checker for a report type"""
        return self._checkers.get(report_type)

    def get_all_checkers(self) -> Dict[ReportType, Type[ReportCapabilityChecker]]:
        """Get all registered checkers"""
        return self._checkers.copy()

    def list_plugins(self) -> List[str]:
        """List all registered plugin names"""
        return self._registered_plugins.copy()


# Global registry instance
report_plugin_registry = ReportPluginRegistry()
