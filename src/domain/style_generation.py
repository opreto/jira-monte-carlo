"""Domain interfaces for style and theme generation"""
from abc import ABC, abstractmethod
from typing import Any, Dict

from .styles import Theme


class StyleGenerator(ABC):
    """Interface for generating styles from themes"""

    @abstractmethod
    def generate_css(self, theme: Theme) -> str:
        """Generate CSS styles from theme"""
        pass

    @abstractmethod
    def generate_chart_config(self, theme: Theme) -> Dict[str, Any]:
        """Generate chart configuration from theme"""
        pass

    @abstractmethod
    def generate_colors(self, theme: Theme) -> Dict[str, str]:
        """Generate color palette from theme"""
        pass
