"""Mapper for converting domain data to chart view models"""

from typing import Dict, List, Any, Optional
import statistics

from ..models.view_models import ChartViewModel
from ...domain.entities import SimulationResult
from ...domain.value_objects import VelocityMetrics, HistoricalData
from ...domain.process_health import (
    ProcessHealthMetrics,
    AgingAnalysis,
    WIPAnalysis,
    SprintHealthAnalysis,
    LeadTimeAnalysis,
    BlockedItemsAnalysis
)


class ChartMapper:
    """Maps domain data to chart view models"""
    
    def create_probability_distribution_chart(
        self,
        simulation_result: SimulationResult
    ) -> ChartViewModel:
        """Create probability distribution chart
        
        Args:
            simulation_result: Simulation results
            
        Returns:
            Chart view model
        """
        # Extract histogram data
        hist_data = simulation_result.histogram
        sprints = list(hist_data.keys())
        probabilities = list(hist_data.values())
        
        # Create bar chart data
        data = {
            'x': sprints,
            'y': probabilities,
            'type': 'bar',
            'name': 'Probability',
            'marker': {
                'color': '#3b82f6',
                'opacity': 0.8
            }
        }
        
        # Create layout
        layout = {
            'title': {
                'text': 'Probability Distribution',
                'font': {'size': 18}
            },
            'xaxis': {
                'title': 'Number of Sprints',
                'gridcolor': '#e5e5e5'
            },
            'yaxis': {
                'title': 'Probability (%)',
                'gridcolor': '#e5e5e5',
                'tickformat': '.1%'
            },
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'t': 40, 'r': 20, 'b': 60, 'l': 60},
            'hoverlabel': {
                'bgcolor': 'white',
                'bordercolor': '#888',
                'font': {'size': 12}
            }
        }
        
        # Generate insights
        insights = []
        mode_sprints = max(hist_data.keys(), key=lambda k: hist_data[k])
        insights.append(f"Most likely completion: {mode_sprints} sprints")
        
        return ChartViewModel(
            chart_id="probability_distribution",
            chart_type="bar",
            title="Probability Distribution",
            description="The likelihood of completing work in different numbers of sprints",
            data=data,
            layout=layout,
            insights=insights
        )
    
    def create_confidence_intervals_chart(
        self,
        simulation_result: SimulationResult
    ) -> ChartViewModel:
        """Create confidence intervals chart
        
        Args:
            simulation_result: Simulation results
            
        Returns:
            Chart view model
        """
        # Extract percentile data
        percentiles = simulation_result.percentiles
        confidence_levels = []
        sprints = []
        colors = []
        
        confidence_map = [
            (0.5, "50% (Optimistic)", "#10b981"),
            (0.7, "70% (Likely)", "#3b82f6"),
            (0.85, "85% (Conservative)", "#f59e0b"),
            (0.95, "95% (Very Conservative)", "#ef4444")
        ]
        
        for conf, label, color in confidence_map:
            if conf in percentiles:
                confidence_levels.append(label)
                sprints.append(percentiles[conf])
                colors.append(color)
        
        # Create horizontal bar chart
        data = {
            'x': sprints,
            'y': confidence_levels,
            'type': 'bar',
            'orientation': 'h',
            'marker': {
                'color': colors
            },
            'text': [f"{int(s)} sprints" for s in sprints],
            'textposition': 'outside'
        }
        
        layout = {
            'title': {
                'text': 'Confidence Intervals',
                'font': {'size': 18}
            },
            'xaxis': {
                'title': 'Sprints to Complete',
                'gridcolor': '#e5e5e5'
            },
            'yaxis': {
                'title': 'Confidence Level',
                'gridcolor': '#e5e5e5'
            },
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'t': 40, 'r': 120, 'b': 60, 'l': 150},
            'bargap': 0.3
        }
        
        # Generate insights
        insights = []
        if 0.85 in percentiles and 0.5 in percentiles:
            spread = percentiles[0.85] - percentiles[0.5]
            insights.append(f"Range: {spread:.1f} sprints between optimistic and conservative")
        
        return ChartViewModel(
            chart_id="confidence_intervals",
            chart_type="bar",
            title="Confidence Intervals",
            description="Range of completion estimates at different confidence levels",
            data=data,
            layout=layout,
            insights=insights
        )
    
    def create_velocity_trend_chart(
        self,
        historical_data: HistoricalData,
        velocity_metrics: VelocityMetrics
    ) -> ChartViewModel:
        """Create velocity trend chart
        
        Args:
            historical_data: Historical sprint data
            velocity_metrics: Calculated velocity metrics
            
        Returns:
            Chart view model
        """
        # Extract velocity data
        sprints = []
        velocities = []
        
        for sprint in historical_data.sprints[-10:]:  # Last 10 sprints
            sprints.append(sprint.name)
            velocities.append(sprint.velocity)
        
        # Main velocity line
        velocity_trace = {
            'x': sprints,
            'y': velocities,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'Velocity',
            'line': {
                'color': '#3b82f6',
                'width': 3
            },
            'marker': {
                'size': 8,
                'color': '#3b82f6'
            }
        }
        
        # Average line
        avg_trace = {
            'x': sprints,
            'y': [velocity_metrics.average] * len(sprints),
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Average',
            'line': {
                'color': '#10b981',
                'width': 2,
                'dash': 'dash'
            }
        }
        
        # Trend line (simplified)
        if velocity_metrics.trend:
            trend_values = []
            for i in range(len(sprints)):
                trend_val = velocity_metrics.average + (velocity_metrics.trend * i)
                trend_values.append(trend_val)
            
            trend_trace = {
                'x': sprints,
                'y': trend_values,
                'type': 'scatter',
                'mode': 'lines',
                'name': 'Trend',
                'line': {
                    'color': '#f59e0b',
                    'width': 2,
                    'dash': 'dot'
                }
            }
            data = [velocity_trace, avg_trace, trend_trace]
        else:
            data = [velocity_trace, avg_trace]
        
        layout = {
            'title': {
                'text': 'Historical Velocity Trend',
                'font': {'size': 18}
            },
            'xaxis': {
                'title': 'Sprint',
                'gridcolor': '#e5e5e5'
            },
            'yaxis': {
                'title': 'Velocity (Story Points)',
                'gridcolor': '#e5e5e5'
            },
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'t': 40, 'r': 20, 'b': 80, 'l': 60},
            'legend': {
                'x': 0.02,
                'y': 0.98,
                'bgcolor': 'rgba(255,255,255,0.8)',
                'bordercolor': '#ccc',
                'borderwidth': 1
            },
            'hovermode': 'x unified'
        }
        
        # Generate insights
        insights = []
        insights.append(f"Average velocity: {velocity_metrics.average:.1f} points/sprint")
        if velocity_metrics.trend:
            trend_dir = "increasing" if velocity_metrics.trend > 0 else "decreasing"
            insights.append(f"Velocity is {trend_dir}")
        
        return ChartViewModel(
            chart_id="velocity_trend",
            chart_type="line",
            title="Historical Velocity Trend",
            description="Team velocity over recent sprints with trend line",
            data=data,
            layout=layout,
            insights=insights
        )
    
    def create_health_gauge_chart(
        self,
        health_metrics: ProcessHealthMetrics
    ) -> ChartViewModel:
        """Create health score gauge chart
        
        Args:
            health_metrics: Process health metrics
            
        Returns:
            Gauge chart view model
        """
        score = health_metrics.overall_health_score * 100
        
        # Determine color based on score
        if score >= 90:
            bar_color = "#10b981"  # Green
        elif score >= 75:
            bar_color = "#3b82f6"  # Blue
        elif score >= 60:
            bar_color = "#f59e0b"  # Orange
        else:
            bar_color = "#ef4444"  # Red
        
        data = {
            'type': 'indicator',
            'mode': 'gauge+number+delta',
            'value': score,
            'title': {
                'text': 'Process Health Score',
                'font': {'size': 24}
            },
            'delta': {
                'reference': 75,
                'increasing': {'color': '#10b981'},
                'decreasing': {'color': '#ef4444'}
            },
            'gauge': {
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': bar_color},
                'bgcolor': 'white',
                'borderwidth': 2,
                'bordercolor': '#e5e5e5',
                'steps': [
                    {'range': [0, 60], 'color': '#fee2e2'},
                    {'range': [60, 75], 'color': '#fed7aa'},
                    {'range': [75, 90], 'color': '#dbeafe'},
                    {'range': [90, 100], 'color': '#d1fae5'}
                ],
                'threshold': {
                    'line': {'color': 'black', 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        }
        
        layout = {
            'margin': {'t': 40, 'r': 40, 'b': 40, 'l': 40},
            'height': 300,
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
        
        insights = []
        insights.append(f"Overall health: {score:.0f}%")
        
        return ChartViewModel(
            chart_id="health_gauge",
            chart_type="gauge",
            title="Process Health Score",
            description="Overall health of your development process",
            data=data,
            layout=layout,
            insights=insights
        )
    
    def create_aging_chart(
        self,
        aging_analysis: AgingAnalysis
    ) -> ChartViewModel:
        """Create work item aging chart
        
        Args:
            aging_analysis: Aging analysis data
            
        Returns:
            Chart view model
        """
        categories = ['Fresh (<7d)', 'Active (7-30d)', 'Stale (30-90d)', 'Abandoned (>90d)']
        values = [
            aging_analysis.fresh_count,
            aging_analysis.active_count,
            aging_analysis.stale_count,
            aging_analysis.abandoned_count
        ]
        colors = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
        
        data = {
            'values': values,
            'labels': categories,
            'type': 'pie',
            'hole': 0.4,
            'marker': {
                'colors': colors,
                'line': {
                    'color': 'white',
                    'width': 2
                }
            },
            'textposition': 'outside',
            'textinfo': 'label+percent'
        }
        
        layout = {
            'title': {
                'text': 'Work Item Age Distribution',
                'font': {'size': 18}
            },
            'margin': {'t': 40, 'r': 20, 'b': 20, 'l': 20},
            'showlegend': True,
            'legend': {
                'orientation': 'v',
                'x': 1,
                'y': 0.5
            },
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)'
        }
        
        insights = []
        if aging_analysis.abandoned_count > 0:
            insights.append(f"{aging_analysis.abandoned_count} items need attention")
        
        return ChartViewModel(
            chart_id="aging_distribution",
            chart_type="pie",
            title="Work Item Age Distribution",
            description="Distribution of work items by age",
            data=data,
            layout=layout,
            insights=insights
        )
    
    def create_wip_by_status_chart(
        self,
        wip_analysis: WIPAnalysis
    ) -> ChartViewModel:
        """Create WIP by status chart
        
        Args:
            wip_analysis: WIP analysis data
            
        Returns:
            Chart view model
        """
        statuses = []
        counts = []
        limits = []
        colors = []
        
        for status, data in wip_analysis.wip_by_status.items():
            statuses.append(status)
            counts.append(data['count'])
            limits.append(data.get('limit', data['count'] * 1.2))
            
            # Color based on limit violation
            if 'limit' in data and data['count'] > data['limit']:
                colors.append('#ef4444')  # Red for violation
            else:
                colors.append('#3b82f6')  # Blue for normal
        
        # Current WIP bars
        wip_trace = {
            'x': statuses,
            'y': counts,
            'type': 'bar',
            'name': 'Current WIP',
            'marker': {
                'color': colors
            }
        }
        
        # WIP limits line
        limit_trace = {
            'x': statuses,
            'y': limits,
            'type': 'scatter',
            'mode': 'lines+markers',
            'name': 'WIP Limit',
            'line': {
                'color': '#ef4444',
                'width': 2,
                'dash': 'dash'
            },
            'marker': {
                'size': 8,
                'color': '#ef4444'
            }
        }
        
        data = [wip_trace, limit_trace]
        
        layout = {
            'title': {
                'text': 'Work In Progress by Status',
                'font': {'size': 18}
            },
            'xaxis': {
                'title': 'Status',
                'gridcolor': '#e5e5e5'
            },
            'yaxis': {
                'title': 'Number of Items',
                'gridcolor': '#e5e5e5'
            },
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'t': 40, 'r': 20, 'b': 100, 'l': 60},
            'legend': {
                'x': 0.02,
                'y': 0.98
            },
            'barmode': 'group'
        }
        
        insights = []
        violations = len(wip_analysis.items_over_limit)
        if violations > 0:
            insights.append(f"{violations} statuses exceed WIP limits")
        
        return ChartViewModel(
            chart_id="wip_by_status",
            chart_type="bar",
            title="Work In Progress by Status",
            description="Current WIP compared to limits for each status",
            data=data,
            layout=layout,
            insights=insights
        )
    
    def create_sprint_completion_chart(
        self,
        sprint_health: SprintHealthAnalysis
    ) -> ChartViewModel:
        """Create sprint completion trend chart
        
        Args:
            sprint_health: Sprint health analysis data
            
        Returns:
            Chart view model
        """
        sprints = []
        completion_rates = []
        colors = []
        
        # Get last 10 sprints
        recent_sprints = list(sprint_health.completion_by_sprint.items())[-10:]
        
        for sprint_name, rate in recent_sprints:
            sprints.append(sprint_name)
            completion_rates.append(rate * 100)
            
            # Color based on completion rate
            if rate >= 0.8:
                colors.append('#10b981')  # Green
            elif rate >= 0.6:
                colors.append('#f59e0b')  # Orange
            else:
                colors.append('#ef4444')  # Red
        
        data = {
            'x': sprints,
            'y': completion_rates,
            'type': 'bar',
            'marker': {
                'color': colors
            },
            'text': [f"{rate:.0f}%" for rate in completion_rates],
            'textposition': 'outside'
        }
        
        # Add average line
        avg_trace = {
            'x': sprints,
            'y': [sprint_health.average_completion_rate * 100] * len(sprints),
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Average',
            'line': {
                'color': '#6b7280',
                'width': 2,
                'dash': 'dash'
            }
        }
        
        layout = {
            'title': {
                'text': 'Sprint Completion Trend',
                'font': {'size': 18}
            },
            'xaxis': {
                'title': 'Sprint',
                'gridcolor': '#e5e5e5'
            },
            'yaxis': {
                'title': 'Completion Rate (%)',
                'gridcolor': '#e5e5e5',
                'range': [0, 110]
            },
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'margin': {'t': 40, 'r': 20, 'b': 80, 'l': 60},
            'showlegend': True
        }
        
        insights = []
        avg_rate = sprint_health.average_completion_rate * 100
        insights.append(f"Average completion: {avg_rate:.0f}%")
        
        return ChartViewModel(
            chart_id="sprint_completion",
            chart_type="bar",
            title="Sprint Completion Trend",
            description="Sprint completion rates over time",
            data=[data, avg_trace],
            layout=layout,
            insights=insights
        )