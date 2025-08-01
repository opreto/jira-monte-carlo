"""HTML templates for reports - Refactored to use file-based templates"""

import os
from jinja2 import Template
from .services.template_service import TemplateService


class ReportTemplates:
    """HTML templates for report generation using file-based templates"""

    _template_service = None

    @classmethod
    def _get_template_service(cls) -> TemplateService:
        """Get or create the template service singleton"""
        if cls._template_service is None:
            cls._template_service = TemplateService()
        return cls._template_service

    @staticmethod
    def get_base_template() -> Template:
        """Get base HTML template"""
        service = ReportTemplates._get_template_service()
        # For backward compatibility, we need to return a Template object
        # that can be used with the existing render() calls
        template = service.get_template("base/layout.html")

        # Create a wrapper that handles the old interface
        class TemplateWrapper:
            def __init__(self, template, service):
                self._template = template
                self._service = service

            def render(self, **kwargs):
                # Transform old context to new context
                # Old templates expected 'styles' but new expects 'theme_css'
                if "styles" in kwargs:
                    kwargs["theme_css"] = kwargs.pop("styles")

                # Ensure content is properly handled
                if "content" not in kwargs:
                    kwargs["content"] = ""

                return self._template.render(**kwargs)

        return TemplateWrapper(template, service)

    @staticmethod
    def get_single_report_template() -> Template:
        """Get single project report template"""
        service = ReportTemplates._get_template_service()
        # Use the content-only version for backward compatibility
        template = service.get_template("reports/single_project_content.html")

        # Create a wrapper that provides backward compatibility
        class SingleReportTemplateWrapper:
            def __init__(self, template, service):
                self._template = template
                self._service = service

            def render(self, **kwargs):
                # The old code expects to combine base template with content
                # The content template already has everything needed
                return self._template.render(**kwargs)

        return SingleReportTemplateWrapper(template, service)

    @staticmethod
    def get_dashboard_template() -> Template:
        """Get multi-project dashboard template"""
        service = ReportTemplates._get_template_service()
        # Use the content-only version for backward compatibility
        template = service.get_template("reports/multi_project_content.html")

        # Create a wrapper for backward compatibility
        class DashboardTemplateWrapper:
            def __init__(self, template, service):
                self._template = template
                self._service = service

            def render(self, **kwargs):
                # The content template already has everything needed
                return self._template.render(**kwargs)

        return DashboardTemplateWrapper(template, service)


# For gradual migration - Feature flag to switch between implementations
USE_FILE_BASED_TEMPLATES = (
    os.environ.get("USE_FILE_BASED_TEMPLATES", "false").lower() == "true"
)

if not USE_FILE_BASED_TEMPLATES:
    # Import the original implementation
    from .templates import ReportTemplates as OriginalReportTemplates

    ReportTemplates = OriginalReportTemplates
