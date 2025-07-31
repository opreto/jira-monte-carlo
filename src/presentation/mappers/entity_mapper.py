"""Mapper for converting domain entities to presentation DTOs"""

from typing import Dict, Any

from ...domain.entities import Issue, Sprint, SimulationResult
from ...domain.value_objects import VelocityMetrics, HistoricalData
from ...domain.process_health import (
    ProcessHealthMetrics,
    AgingAnalysis,
    WIPAnalysis,
    SprintHealthAnalysis,
    BlockedItemsAnalysis,
    LeadTimeAnalysis,
)


class EntityMapper:
    """Maps domain entities to presentation-friendly formats"""

    def map_issue_to_dict(self, issue: Issue) -> Dict[str, Any]:
        """Convert issue entity to dictionary

        Args:
            issue: Issue entity

        Returns:
            Dictionary representation
        """
        return {
            "id": issue.id,
            "title": issue.title,
            "status": issue.status,
            "estimation": issue.estimation,
            "velocity": issue.velocity,
            "sprint": issue.sprint,
            "labels": issue.labels,
            "issue_type": issue.issue_type,
            "assignee": issue.assignee,
            "created_date": issue.created_date.isoformat()
            if issue.created_date
            else None,
            "resolved_date": issue.resolved_date.isoformat()
            if issue.resolved_date
            else None,
            "project": issue.project,
            "is_blocked": issue.is_blocked,
            "parent_id": issue.parent_id,
            "custom_fields": issue.custom_fields,
        }

    def map_sprint_to_dict(self, sprint: Sprint) -> Dict[str, Any]:
        """Convert sprint entity to dictionary

        Args:
            sprint: Sprint entity

        Returns:
            Dictionary representation
        """
        return {
            "id": sprint.id,
            "name": sprint.name,
            "start_date": sprint.start_date.isoformat() if sprint.start_date else None,
            "end_date": sprint.end_date.isoformat() if sprint.end_date else None,
            "state": sprint.state,
            "velocity": sprint.velocity,
            "committed_points": sprint.committed_points,
            "completed_points": sprint.completed_points,
            "issue_count": sprint.issue_count,
            "goal": sprint.goal,
        }

    def map_velocity_metrics(self, metrics: VelocityMetrics) -> Dict[str, Any]:
        """Convert velocity metrics to dictionary

        Args:
            metrics: Velocity metrics

        Returns:
            Dictionary representation
        """
        return {
            "average": round(metrics.average, 2),
            "median": round(metrics.median, 2),
            "std_dev": round(metrics.std_dev, 2),
            "min": round(metrics.min_velocity, 2),
            "max": round(metrics.max_velocity, 2),
            "trend": round(metrics.trend, 3) if metrics.trend else None,
            "coefficient_of_variation": round(metrics.std_dev / metrics.average, 3)
            if metrics.average > 0
            else 0,
        }

    def map_simulation_result(self, result: SimulationResult) -> Dict[str, Any]:
        """Convert simulation result to dictionary

        Args:
            result: Simulation result

        Returns:
            Dictionary representation
        """
        return {
            "percentiles": {
                f"{int(k * 100)}%": round(v, 1) for k, v in result.percentiles.items()
            },
            "histogram": {str(k): round(v, 3) for k, v in result.histogram.items()},
            "mean": round(result.mean, 2),
            "std_dev": round(result.std_dev, 2),
            "min": int(result.min_value),
            "max": int(result.max_value),
            "sample_size": result.sample_size,
        }

    def map_health_metrics(self, metrics: ProcessHealthMetrics) -> Dict[str, Any]:
        """Convert process health metrics to dictionary

        Args:
            metrics: Process health metrics

        Returns:
            Dictionary representation
        """
        result = {
            "overall_score": round(metrics.overall_health_score * 100, 1),
            "components": {},
        }

        if metrics.aging_analysis:
            result["components"]["aging"] = self._map_aging_analysis(
                metrics.aging_analysis
            )

        if metrics.wip_analysis:
            result["components"]["wip"] = self._map_wip_analysis(metrics.wip_analysis)

        if metrics.sprint_health:
            result["components"]["sprint_health"] = self._map_sprint_health(
                metrics.sprint_health
            )

        if metrics.blocked_analysis:
            result["components"]["blocked"] = self._map_blocked_analysis(
                metrics.blocked_analysis
            )

        if metrics.lead_time_analysis:
            result["components"]["lead_time"] = self._map_lead_time_analysis(
                metrics.lead_time_analysis
            )

        return result

    def map_historical_data(self, data: HistoricalData) -> Dict[str, Any]:
        """Convert historical data to dictionary

        Args:
            data: Historical data

        Returns:
            Dictionary representation
        """
        return {
            "sprints": [self.map_sprint_to_dict(s) for s in data.sprints],
            "issues": [self.map_issue_to_dict(i) for i in data.issues],
            "start_date": data.start_date.isoformat() if data.start_date else None,
            "end_date": data.end_date.isoformat() if data.end_date else None,
            "total_sprints": len(data.sprints),
            "total_issues": len(data.issues),
        }

    def _map_aging_analysis(self, aging: AgingAnalysis) -> Dict[str, Any]:
        """Map aging analysis to dictionary"""
        return {
            "fresh_count": aging.fresh_count,
            "active_count": aging.active_count,
            "stale_count": aging.stale_count,
            "abandoned_count": aging.abandoned_count,
            "total_items": aging.total_items,
            "average_age": round(aging.average_age, 1),
            "oldest_item_age": aging.oldest_item_age,
            "score": round(aging.health_score * 100, 1),
            "old_items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "age_days": item.age_days,
                    "status": item.status,
                }
                for item in aging.old_items[:5]  # Top 5 oldest
            ],
        }

    def _map_wip_analysis(self, wip: WIPAnalysis) -> Dict[str, Any]:
        """Map WIP analysis to dictionary"""
        return {
            "total_wip": wip.total_wip,
            "by_status": {
                status: {
                    "count": data["count"],
                    "limit": data.get("limit"),
                    "over_limit": data.get("limit") and data["count"] > data["limit"],
                }
                for status, data in wip.wip_by_status.items()
            },
            "items_over_limit": [
                {
                    "status": item.status,
                    "count": item.count,
                    "limit": item.limit,
                    "excess": item.count - item.limit,
                }
                for item in wip.items_over_limit
            ],
            "score": round(wip.health_score * 100, 1),
        }

    def _map_sprint_health(self, health: SprintHealthAnalysis) -> Dict[str, Any]:
        """Map sprint health analysis to dictionary"""
        return {
            "average_completion_rate": round(health.average_completion_rate * 100, 1),
            "sprints_analyzed": health.sprints_analyzed,
            "average_velocity": round(health.average_velocity, 1)
            if health.average_velocity
            else None,
            "average_scope_change": round(health.average_scope_change * 100, 1)
            if health.average_scope_change
            else None,
            "score": round(health.health_score * 100, 1),
            "completion_by_sprint": {
                sprint: round(rate * 100, 1)
                for sprint, rate in list(health.completion_by_sprint.items())[
                    -5:
                ]  # Last 5 sprints
            },
        }

    def _map_blocked_analysis(self, blocked: BlockedItemsAnalysis) -> Dict[str, Any]:
        """Map blocked items analysis to dictionary"""
        return {
            "blocked_count": blocked.blocked_count,
            "total_items": blocked.total_items,
            "blocked_percentage": round(blocked.blocked_percentage * 100, 1),
            "average_blocked_age": round(blocked.average_blocked_age, 1),
            "score": round(blocked.health_score * 100, 1),
            "blocked_items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "blocked_days": item.blocked_days,
                    "assignee": item.assignee,
                }
                for item in blocked.blocked_items[:5]  # Top 5 blocked items
            ],
        }

    def _map_lead_time_analysis(self, lead_time: LeadTimeAnalysis) -> Dict[str, Any]:
        """Map lead time analysis to dictionary"""
        return {
            "average_lead_time": round(lead_time.average_lead_time, 1),
            "median_lead_time": round(lead_time.median_lead_time, 1),
            "percentile_85": round(lead_time.percentile_85, 1),
            "score": round(lead_time.health_score * 100, 1),
            "by_type": {
                issue_type: round(avg_time, 1)
                for issue_type, avg_time in lead_time.lead_time_by_type.items()
            },
        }
