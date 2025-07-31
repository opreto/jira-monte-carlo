"""Base component for presentation layer components"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from jinja2 import Environment


class Component(ABC):
    """Base class for all presentation components"""

    def __init__(self, template: Optional[str] = None):
        """Initialize component with optional template

        Args:
            template: Optional template string. If not provided, will use get_template()
        """
        self._template = template
        self._environment = Environment(
            autoescape=True, trim_blocks=True, lstrip_blocks=True
        )

    @abstractmethod
    def get_template(self) -> str:
        """Get the component's template string

        Returns:
            Template string
        """
        pass

    @abstractmethod
    def get_context(self, **kwargs) -> Dict[str, Any]:
        """Get the context data for rendering

        Args:
            **kwargs: Component-specific parameters

        Returns:
            Context dictionary for template rendering
        """
        pass

    def render(self, **kwargs) -> str:
        """Render the component to HTML

        Args:
            **kwargs: Parameters passed to get_context

        Returns:
            Rendered HTML string
        """
        # Get template
        template_str = self._template or self.get_template()
        template = self._environment.from_string(template_str)

        # Get context
        context = self.get_context(**kwargs)

        # Render
        return template.render(**context)

    def get_styles(self) -> Optional[str]:
        """Get component-specific styles

        Returns:
            CSS string or None if no component-specific styles
        """
        return None

    def get_scripts(self) -> Optional[str]:
        """Get component-specific scripts

        Returns:
            JavaScript string or None if no component-specific scripts
        """
        return None


class CompositeComponent(Component):
    """Base class for components that contain other components"""

    def __init__(self, template: Optional[str] = None):
        """Initialize composite component"""
        super().__init__(template)
        self._children: List[Component] = []

    def add_child(self, component: Component) -> "CompositeComponent":
        """Add a child component

        Args:
            component: Child component to add

        Returns:
            Self for chaining
        """
        self._children.append(component)
        return self

    def render_children(self) -> Dict[str, str]:
        """Render all child components

        Returns:
            Dictionary mapping component class name to rendered HTML
        """
        rendered = {}
        for child in self._children:
            key = child.__class__.__name__.lower()
            rendered[key] = child.render()
        return rendered

    def get_context(self, **kwargs) -> Dict[str, Any]:
        """Get context including rendered children

        Args:
            **kwargs: Component-specific parameters

        Returns:
            Context dictionary with rendered children
        """
        context = kwargs.copy()
        context.update(self.render_children())
        return context
