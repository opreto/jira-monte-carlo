"""Tests for plugin registry"""

from src.application.plugin_registry import ReportPluginRegistry
from src.application.capability_analyzer import ReportCapabilityChecker
from src.domain.reporting_capabilities import ReportType


class MockCapabilityChecker(ReportCapabilityChecker):
    """Mock capability checker for testing"""
    
    def check_availability(self, issues, sprints, available_fields):
        return None


class TestReportPluginRegistry:
    """Test plugin registry functionality"""
    
    def test_register_checker(self):
        """Test registering a capability checker"""
        registry = ReportPluginRegistry()
        
        # Register a checker
        registry.register(ReportType.MONTE_CARLO_FORECAST, MockCapabilityChecker)
        
        # Verify it's registered
        assert registry.get_checker(ReportType.MONTE_CARLO_FORECAST) == MockCapabilityChecker
        assert len(registry.list_plugins()) == 1
    
    def test_register_override(self):
        """Test overriding an existing checker"""
        registry = ReportPluginRegistry()
        
        # Register first checker
        registry.register(ReportType.MONTE_CARLO_FORECAST, MockCapabilityChecker)
        
        # Create another mock checker
        class AnotherMockChecker(ReportCapabilityChecker):
            def check_availability(self, issues, sprints, available_fields):
                return None
        
        # Override with new checker
        registry.register(ReportType.MONTE_CARLO_FORECAST, AnotherMockChecker)
        
        # Verify it's overridden
        assert registry.get_checker(ReportType.MONTE_CARLO_FORECAST) == AnotherMockChecker
        assert len(registry.list_plugins()) == 2  # Both registrations are tracked
    
    def test_get_all_checkers(self):
        """Test getting all registered checkers"""
        registry = ReportPluginRegistry()
        
        # Register multiple checkers
        registry.register(ReportType.MONTE_CARLO_FORECAST, MockCapabilityChecker)
        registry.register(ReportType.AGING_WORK_ITEMS, MockCapabilityChecker)
        
        all_checkers = registry.get_all_checkers()
        assert len(all_checkers) == 2
        assert ReportType.MONTE_CARLO_FORECAST in all_checkers
        assert ReportType.AGING_WORK_ITEMS in all_checkers
    
    def test_get_unregistered_checker(self):
        """Test getting a checker that isn't registered"""
        registry = ReportPluginRegistry()
        
        # Should return None for unregistered types
        assert registry.get_checker(ReportType.SPRINT_HEALTH) is None