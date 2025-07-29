"""Domain entities for process health metrics"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class AgingCategory(Enum):
    """Categories for aging work items"""

    FRESH = "fresh"  # 0-7 days
    NORMAL = "normal"  # 8-14 days
    AGING = "aging"  # 15-30 days
    STALE = "stale"  # 31-60 days
    ABANDONED = "abandoned"  # 60+ days


class WIPStatus(Enum):
    """Work in Progress status categories"""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    BLOCKED = "blocked"
    DONE = "done"


@dataclass
class AgingItem:
    """Work item with aging information"""

    key: str
    summary: str
    status: str
    age_days: int
    category: AgingCategory
    assignee: Optional[str] = None
    last_updated: Optional[datetime] = None
    created: datetime = field(default_factory=datetime.now)
    story_points: Optional[float] = None

    @property
    def is_blocked(self) -> bool:
        """Check if item appears to be blocked"""
        blocked_keywords = ["blocked", "impediment", "waiting", "hold"]
        return any(keyword in self.status.lower() for keyword in blocked_keywords)


@dataclass
class AgingAnalysis:
    """Analysis of aging work items"""

    items_by_category: Dict[AgingCategory, List[AgingItem]]
    average_age_by_status: Dict[str, float]
    oldest_items: List[AgingItem]
    blocked_items: List[AgingItem]
    total_items: int
    thresholds: Optional[Dict[str, int]] = None  # Dynamic aging thresholds used

    @property
    def aging_distribution(self) -> Dict[AgingCategory, int]:
        """Get count of items in each aging category"""
        return {category: len(items) for category, items in self.items_by_category.items()}

    @property
    def critical_items(self) -> List[AgingItem]:
        """Get items that need immediate attention (stale + abandoned)"""
        critical = []
        for category in [AgingCategory.STALE, AgingCategory.ABANDONED]:
            critical.extend(self.items_by_category.get(category, []))
        return critical


@dataclass
class WIPItem:
    """Work item in progress"""

    key: str
    summary: str
    status: str
    wip_status: WIPStatus
    assignee: Optional[str] = None
    age_days: int = 0
    story_points: Optional[float] = None


@dataclass
class WIPAnalysis:
    """Work in Progress analysis"""

    items_by_status: Dict[WIPStatus, List[WIPItem]]
    wip_by_assignee: Dict[str, int]
    total_wip: int
    wip_limits: Dict[WIPStatus, int] = field(default_factory=dict)

    @property
    def wip_violations(self) -> Dict[WIPStatus, int]:
        """Get WIP limit violations"""
        violations = {}
        for status, items in self.items_by_status.items():
            if status in self.wip_limits:
                count = len(items)
                limit = self.wip_limits[status]
                if count > limit:
                    violations[status] = count - limit
        return violations

    @property
    def utilization_by_status(self) -> Dict[WIPStatus, float]:
        """Get WIP utilization as percentage of limit"""
        utilization = {}
        for status, items in self.items_by_status.items():
            if status in self.wip_limits and self.wip_limits[status] > 0:
                utilization[status] = len(items) / self.wip_limits[status]
        return utilization


@dataclass
class SprintHealth:
    """Sprint health metrics"""

    sprint_name: str
    start_date: datetime
    end_date: datetime
    committed_points: float
    completed_points: float
    added_points: float  # Scope added during sprint
    removed_points: float  # Scope removed during sprint
    completion_rate: float  # % of committed work completed

    @property
    def scope_change(self) -> float:
        """Net scope change during sprint"""
        return self.added_points - self.removed_points

    @property
    def scope_change_percentage(self) -> float:
        """Scope change as % of original commitment"""
        if self.committed_points == 0:
            return 0
        return abs(self.scope_change) / self.committed_points * 100


@dataclass
class SprintHealthAnalysis:
    """Analysis of sprint health over time"""

    sprint_metrics: List[SprintHealth]
    average_completion_rate: float
    completion_rate_trend: float  # Positive = improving
    average_scope_change: float
    predictability_score: float  # 0-1, based on consistency

    @property
    def recent_sprints(self) -> List[SprintHealth]:
        """Get last 6 sprints"""
        return self.sprint_metrics[-6:] if len(self.sprint_metrics) > 6 else self.sprint_metrics


@dataclass
class BlockedItem:
    """Item that is blocked"""

    key: str
    summary: str
    status: str
    blocked_days: int
    blocker_description: Optional[str] = None
    assignee: Optional[str] = None
    story_points: Optional[float] = None
    first_blocked_date: Optional[datetime] = None

    @property
    def severity(self) -> str:
        """Get severity based on blocked duration"""
        if self.blocked_days <= 2:
            return "low"
        elif self.blocked_days <= 5:
            return "medium"
        else:
            return "high"


@dataclass
class BlockedItemsAnalysis:
    """Analysis of blocked items"""

    blocked_items: List[BlockedItem]
    total_blocked_points: float
    average_blocked_days: float
    blockers_by_type: Dict[str, int]  # Categories of blockers
    repeat_blockers: List[str]  # Frequently occurring blockers

    @property
    def items_by_severity(self) -> Dict[str, List[BlockedItem]]:
        """Group items by severity"""
        severity_groups = {"low": [], "medium": [], "high": []}
        for item in self.blocked_items:
            severity_groups[item.severity].append(item)
        return severity_groups


@dataclass
class HealthScoreComponent:
    """Component of the health score calculation"""

    name: str
    score: float  # 0-1
    weight: float = 1.0
    description: str = ""
    insights: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ProcessHealthMetrics:
    """Combined process health metrics"""

    aging_analysis: Optional[AgingAnalysis] = None
    wip_analysis: Optional[WIPAnalysis] = None
    sprint_health: Optional[SprintHealthAnalysis] = None
    blocked_items: Optional[BlockedItemsAnalysis] = None

    @property
    def health_score(self) -> float:
        """Overall process health score (0-1)"""
        scores = []

        if self.aging_analysis:
            # Lower score for more aging items
            aging_ratio = len(self.aging_analysis.critical_items) / self.aging_analysis.total_items
            scores.append(1 - min(aging_ratio * 2, 1))  # Double weight for critical items

        if self.wip_analysis:
            # Lower score for WIP violations
            violation_count = sum(self.wip_analysis.wip_violations.values())
            violation_score = 1 - min(violation_count / 10, 1)  # Max penalty at 10 violations
            scores.append(violation_score)

        if self.sprint_health:
            # Use predictability score directly
            scores.append(self.sprint_health.predictability_score)

        if self.blocked_items:
            # Lower score for more blocked items
            if self.blocked_items.blocked_items:
                blocked_ratio = len(self.blocked_items.items_by_severity["high"]) / len(
                    self.blocked_items.blocked_items
                )
                scores.append(1 - min(blocked_ratio * 2, 1))
            else:
                scores.append(1.0)

        return sum(scores) / len(scores) if scores else 0.5

    @property
    def health_score_breakdown(self) -> List[HealthScoreComponent]:
        """Detailed breakdown of health score calculation"""
        components = []

        if self.aging_analysis:
            # Aging component
            critical_count = len(self.aging_analysis.critical_items)
            aging_ratio = critical_count / self.aging_analysis.total_items
            score = 1 - min(aging_ratio * 2, 1)

            insights = []
            if critical_count > 0:
                insights.append(f"{critical_count} items ({aging_ratio:.0%}) are stale or abandoned")

            recommendations = []
            if score < 0.7:
                recommendations.append("Review and prioritize stale items")
                recommendations.append("Consider closing or archiving abandoned items")
                if self.aging_analysis.average_age_by_status:
                    slowest_status = max(self.aging_analysis.average_age_by_status.items(), key=lambda x: x[1])
                    recommendations.append(
                        f"Focus on '{slowest_status[0]}' items (avg {slowest_status[1]:.0f} days old)"
                    )

            components.append(
                HealthScoreComponent(
                    name="Aging Items",
                    score=score,
                    description=f"Based on {critical_count} critical items out of {self.aging_analysis.total_items} total",
                    insights=insights,
                    recommendations=recommendations,
                )
            )

        if self.wip_analysis:
            # WIP component
            violation_count = sum(self.wip_analysis.wip_violations.values())
            score = 1 - min(violation_count / 10, 1)

            insights = []
            if violation_count > 0:
                for status, count in self.wip_analysis.wip_violations.items():
                    insights.append(f"{status.value}: {count} items over limit")

            recommendations = []
            if score < 0.8:
                recommendations.append("Reduce work in progress to improve flow")
                if self.wip_analysis.wip_by_assignee:
                    overloaded = [
                        (name, count) for name, count in self.wip_analysis.wip_by_assignee.items() if count > 3
                    ]
                    if overloaded:
                        overloaded.sort(key=lambda x: x[1], reverse=True)
                        recommendations.append(f"Rebalance work: {overloaded[0][0]} has {overloaded[0][1]} items")

            components.append(
                HealthScoreComponent(
                    name="Work In Progress",
                    score=score,
                    description=f"{self.wip_analysis.total_wip} items in progress, {violation_count} WIP limit violations",
                    insights=insights,
                    recommendations=recommendations,
                )
            )

        if self.sprint_health:
            # Sprint health component
            score = self.sprint_health.predictability_score

            insights = []
            insights.append(f"Average completion rate: {self.sprint_health.average_completion_rate:.0%}")
            if self.sprint_health.completion_rate_trend > 0:
                insights.append(
                    f"Completion rate improving by {self.sprint_health.completion_rate_trend:.1%} per sprint"
                )
            elif self.sprint_health.completion_rate_trend < 0:
                insights.append(
                    f"Completion rate declining by {abs(self.sprint_health.completion_rate_trend):.1%} per sprint"
                )

            recommendations = []
            if score < 0.8:
                recommendations.append("Improve sprint planning accuracy")
                if self.sprint_health.average_scope_change > 0.2:
                    recommendations.append(
                        f"Reduce scope changes (currently {self.sprint_health.average_scope_change:.0%})"
                    )

            components.append(
                HealthScoreComponent(
                    name="Sprint Predictability",
                    score=score,
                    description=f"Based on {len(self.sprint_health.sprint_metrics)} recent sprints",
                    insights=insights,
                    recommendations=recommendations,
                )
            )

        if self.blocked_items:
            # Blocked items component
            if self.blocked_items.blocked_items:
                high_severity = len(self.blocked_items.items_by_severity.get("high", []))
                blocked_ratio = high_severity / len(self.blocked_items.blocked_items)
                score = 1 - min(blocked_ratio * 2, 1)

                insights = []
                insights.append(f"{len(self.blocked_items.blocked_items)} blocked items")
                insights.append(f"Average blocked time: {self.blocked_items.average_blocked_days:.0f} days")

                recommendations = []
                if score < 0.8:
                    recommendations.append("Escalate high-severity blockers")
                    if self.blocked_items.repeat_blockers:
                        recommendations.append(f"Address recurring blocker: {self.blocked_items.repeat_blockers[0]}")
            else:
                score = 1.0
                insights = ["No blocked items"]
                recommendations = []

            components.append(
                HealthScoreComponent(
                    name="Blocked Items",
                    score=score,
                    description=f"{len(self.blocked_items.blocked_items)} items blocked",
                    insights=insights,
                    recommendations=recommendations,
                )
            )

        return components
