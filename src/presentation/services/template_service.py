"""Template service for managing Jinja2 templates from files"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound
import logging

logger = logging.getLogger(__name__)


class TemplateService:
    """Service for loading and rendering templates from the filesystem"""

    def __init__(self, template_dir: Optional[Path] = None):
        """Initialize template service with template directory

        Args:
            template_dir: Path to templates directory. If None, uses default location
        """
        if template_dir is None:
            # Default to templates directory relative to this file
            current_dir = Path(__file__).parent.parent
            template_dir = current_dir / "templates"

        if not template_dir.exists():
            raise ValueError(f"Template directory does not exist: {template_dir}")

        self.template_dir = template_dir
        self._env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

        # Cache for compiled templates
        self._cache: Dict[str, Template] = {}

        # Configure static URL function
        self._env.globals["url_for"] = self._url_for_static

        logger.info(f"Initialized template service with directory: {template_dir}")

    def _url_for_static(self, endpoint: str, filename: str) -> str:
        """Generate URL for static files

        Args:
            endpoint: Should be 'static' for static files
            filename: Path to static file relative to static directory

        Returns:
            Relative path to static file
        """
        if endpoint == "static":
            # Return relative path from templates to static directory
            return f"../static/{filename}"
        return ""

    def get_template(self, template_name: str) -> Template:
        """Get a template by name, using cache if available

        Args:
            template_name: Name of template file relative to template directory

        Returns:
            Compiled Jinja2 template

        Raises:
            TemplateNotFound: If template doesn't exist
        """
        if template_name not in self._cache:
            try:
                template = self._env.get_template(template_name)
                self._cache[template_name] = template
                logger.debug(f"Loaded template: {template_name}")
            except TemplateNotFound:
                logger.error(f"Template not found: {template_name}")
                raise

        return self._cache[template_name]

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a template with the given context

        Args:
            template_name: Name of template file relative to template directory
            context: Dictionary of variables to pass to template

        Returns:
            Rendered HTML string
        """
        template = self.get_template(template_name)
        return template.render(**context)

    def render_string(self, template_string: str, context: Dict[str, Any]) -> str:
        """Render a template from a string

        Args:
            template_string: Template content as string
            context: Dictionary of variables to pass to template

        Returns:
            Rendered HTML string
        """
        template = self._env.from_string(template_string)
        return template.render(**context)

    def clear_cache(self):
        """Clear the template cache"""
        self._cache.clear()
        logger.info("Cleared template cache")

    def list_templates(self) -> list[str]:
        """List all available templates

        Returns:
            List of template paths relative to template directory
        """
        templates = []
        for root, dirs, files in os.walk(self.template_dir):
            for file in files:
                if file.endswith((".html", ".htm", ".jinja2", ".j2")):
                    rel_path = Path(root).relative_to(self.template_dir) / file
                    templates.append(str(rel_path).replace(os.sep, "/"))

        return sorted(templates)
