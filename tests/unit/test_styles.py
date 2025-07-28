"""Tests for styling and theming system"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import json
from pathlib import Path

from src.domain.styles import Theme
from src.application.style_service import StyleService
from src.presentation.style_generator import StyleGenerator


class TestStyleService:
    def test_init_default_config_dir(self):
        service = StyleService()
        assert service.theme_repository is not None
        
    def test_init_custom_config_dir(self):
        custom_dir = Path("/tmp/test-config")
        service = StyleService(custom_dir)
        assert service.theme_repository is not None
    
    @patch('src.infrastructure.theme_repository.FileThemeRepository.get_theme')
    def test_get_theme_by_name(self, mock_get_theme):
        mock_theme = Mock(spec=Theme)
        mock_get_theme.return_value = mock_theme
        
        service = StyleService()
        theme = service.get_theme("opreto")
        
        assert theme == mock_theme
        mock_get_theme.assert_called_once_with("opreto")
        assert service._current_theme == mock_theme
        
    @patch('src.infrastructure.theme_repository.FileThemeRepository.get_default_theme')
    def test_get_theme_default(self, mock_get_default):
        mock_theme = Mock(spec=Theme)
        mock_get_default.return_value = mock_theme
        
        service = StyleService()
        theme = service.get_theme()
        
        assert theme == mock_theme
        mock_get_default.assert_called_once()
        
    @patch('src.infrastructure.theme_repository.FileThemeRepository.get_theme')
    @patch('src.infrastructure.theme_repository.FileThemeRepository.get_default_theme')
    def test_get_theme_fallback_to_default(self, mock_get_default, mock_get_theme):
        mock_get_theme.return_value = None  # Theme not found
        mock_default_theme = Mock(spec=Theme)
        mock_get_default.return_value = mock_default_theme
        
        service = StyleService()
        theme = service.get_theme("nonexistent")
        
        assert theme == mock_default_theme
        
    def test_get_style_generator(self):
        service = StyleService()
        service._current_theme = Mock(spec=Theme)
        service._style_generator = Mock(spec=StyleGenerator)
        
        generator = service.get_style_generator()
        assert generator == service._style_generator
        
    @patch('src.infrastructure.theme_repository.FileThemeRepository.get_theme')
    def test_get_style_generator_creates_new(self, mock_get_theme):
        mock_theme = Mock(spec=Theme)
        mock_get_theme.return_value = mock_theme
        
        service = StyleService()
        generator = service.get_style_generator("opreto")
        
        assert generator is not None
        assert isinstance(generator, StyleGenerator)
        
    @patch('src.presentation.style_generator.StyleGenerator.generate_css')
    def test_generate_css(self, mock_generate_css):
        mock_css = "body { color: red; }"
        mock_generate_css.return_value = mock_css
        
        service = StyleService()
        service._style_generator = Mock(spec=StyleGenerator)
        service._style_generator.generate_css.return_value = mock_css
        
        css = service.generate_css()
        assert css == mock_css
        
    @patch('src.presentation.style_generator.StyleGenerator.get_chart_colors')
    def test_get_chart_colors(self, mock_get_colors):
        mock_colors = {"primary": "#000000"}
        mock_get_colors.return_value = mock_colors
        
        service = StyleService()
        service._style_generator = Mock(spec=StyleGenerator)
        service._style_generator.get_chart_colors.return_value = mock_colors
        
        colors = service.get_chart_colors()
        assert colors == mock_colors
        
    @patch('src.infrastructure.theme_repository.FileThemeRepository.save_theme')
    def test_save_custom_theme(self, mock_save):
        mock_theme = Mock(spec=Theme)
        
        service = StyleService()
        service.save_custom_theme(mock_theme)
        
        mock_save.assert_called_once_with(mock_theme)
        
    def test_list_available_themes(self):
        service = StyleService()
        themes = service.list_available_themes()
        
        assert "default" in themes
        assert "opreto" in themes