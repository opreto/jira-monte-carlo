"""Responsive chart configuration utilities"""

from typing import Dict, Any, Optional


class ResponsiveChartConfig:
    """Configuration for responsive Plotly charts"""

    @staticmethod
    def get_responsive_layout(base_layout: Dict[str, Any], viewport_width: Optional[int] = None) -> Dict[str, Any]:
        """
        Get responsive layout configuration based on viewport width

        Args:
            base_layout: Base Plotly layout configuration
            viewport_width: Optional viewport width for server-side optimization

        Returns:
            Updated layout configuration with responsive settings
        """
        responsive_layout = base_layout.copy()

        # Base responsive settings
        responsive_layout.update(
            {
                "autosize": True,
                "margin": {"t": 40, "l": 60, "r": 20, "b": 60, "pad": 0},  # Top  # Left  # Right  # Bottom
                "showlegend": True,
                "legend": {"orientation": "h", "yanchor": "bottom", "y": -0.2, "xanchor": "center", "x": 0.5},
                "font": {"size": 14, "family": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'},
            }
        )

        # Mobile optimizations
        if viewport_width and viewport_width < 768:
            responsive_layout.update(
                {
                    "margin": {"t": 30, "l": 40, "r": 10, "b": 40, "pad": 0},
                    "font": {"size": 12},
                    "showlegend": False,  # Hide legend on mobile to save space
                    "xaxis": {
                        **responsive_layout.get("xaxis", {}),
                        "tickangle": -45 if "xaxis" in responsive_layout else 0,
                    },
                }
            )

        # Tablet optimizations
        elif viewport_width and 768 <= viewport_width < 1024:
            responsive_layout.update({"margin": {"t": 35, "l": 50, "r": 15, "b": 50, "pad": 0}, "font": {"size": 13}})

        # 4K optimizations
        elif viewport_width and viewport_width >= 1920:
            responsive_layout.update(
                {
                    "margin": {"t": 50, "l": 80, "r": 30, "b": 80, "pad": 0},
                    "font": {"size": 16},
                    "legend": {"font": {"size": 14}},
                }
            )

        return responsive_layout

    @staticmethod
    def get_responsive_config() -> Dict[str, Any]:
        """Get Plotly config for responsive behavior"""
        return {
            "responsive": True,
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d", "autoScale2d", "toggleSpikelines"],
            "modeBarButtonsToAdd": ["toImage"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "sprint-radar-chart",
                "scale": 2,  # Higher resolution for retina displays
            },
        }

    @staticmethod
    def get_mobile_friendly_colors() -> Dict[str, str]:
        """Get high-contrast colors optimized for mobile viewing"""
        return {
            "primary": "#03564c",
            "secondary": "#4ecdc4",
            "accent": "#ff6b6b",
            "success": "#00A86B",
            "warning": "#FFA500",
            "error": "#DC143C",
            "neutral": "#6c757d",
            "background": "#ffffff",
            "text": "#212529",
        }

    @staticmethod
    def optimize_data_for_mobile(data: list, max_points: int = 50) -> list:
        """
        Optimize chart data for mobile by reducing data points

        Args:
            data: List of Plotly data traces
            max_points: Maximum number of data points for mobile

        Returns:
            Optimized data traces
        """
        optimized_data = []

        for trace in data:
            if "x" in trace and len(trace["x"]) > max_points:
                # Sample data points evenly
                step = len(trace["x"]) // max_points
                trace_copy = trace.copy()
                trace_copy["x"] = trace["x"][::step]
                if "y" in trace:
                    trace_copy["y"] = trace["y"][::step]
                if "text" in trace:
                    trace_copy["text"] = trace["text"][::step]
                optimized_data.append(trace_copy)
            else:
                optimized_data.append(trace)

        return optimized_data

    @staticmethod
    def get_chart_height(chart_type: str, viewport_width: Optional[int] = None) -> str:
        """
        Get optimal chart height based on chart type and viewport

        Args:
            chart_type: Type of chart (e.g., 'bar', 'line', 'scatter')
            viewport_width: Optional viewport width

        Returns:
            CSS height value
        """
        # Default heights by chart type - Compact design
        heights = {
            "bar": {"mobile": "40vh", "tablet": "35vh", "desktop": "30vh", "4k": "25vh"},
            "line": {"mobile": "35vh", "tablet": "30vh", "desktop": "25vh", "4k": "20vh"},
            "scatter": {"mobile": "40vh", "tablet": "35vh", "desktop": "30vh", "4k": "25vh"},
            "pie": {"mobile": "35vh", "tablet": "30vh", "desktop": "25vh", "4k": "20vh"},
            "gauge": {"mobile": "25vh", "tablet": "25vh", "desktop": "20vh", "4k": "20vh"},
        }

        chart_heights = heights.get(chart_type, heights["bar"])

        if viewport_width:
            if viewport_width < 768:
                return chart_heights["mobile"]
            elif viewport_width < 1024:
                return chart_heights["tablet"]
            elif viewport_width >= 1920:
                return chart_heights["4k"]
            else:
                return chart_heights["desktop"]

        # Return a responsive height that works for all viewports
        return "clamp(250px, 30vh, 500px)"
