"""Domain entities for process health metrics"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


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
    detail_items: Optional[List[Dict[str, Any]]] = None  # For expandable item lists


@dataclass
class ProcessHealthMetrics:
    """Combined process health metrics"""

    aging_analysis: Optional[AgingAnalysis] = None
    wip_analysis: Optional[WIPAnalysis] = None
    sprint_health: Optional[SprintHealthAnalysis] = None
    blocked_items: Optional[BlockedItemsAnalysis] = None
    lead_time_analysis: Optional["LeadTimeAnalysis"] = None

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
        
        if self.lead_time_analysis:
            # Use same improved scoring as in breakdown
            avg_lead_time = self.lead_time_analysis.average_lead_time
            
            if avg_lead_time <= 7:
                lead_time_score = 1.0
            elif avg_lead_time <= 14:
                lead_time_score = 0.9
            elif avg_lead_time <= 21:
                lead_time_score = 0.7
            elif avg_lead_time <= 30:
                lead_time_score = 0.5
            else:
                lead_time_score = max(0.2, 0.5 - (avg_lead_time - 30) / 60)
            
            defect_penalty = min(0.3, self.lead_time_analysis.defect_rate * 0.5)
            
            flow_eff = self.lead_time_analysis.average_flow_efficiency
            flow_bonus = 0
            if flow_eff > 0.8:
                flow_bonus = 0.1
            elif flow_eff > 0.6:
                flow_bonus = 0.05
            
            scores.append(max(0, min(1, lead_time_score - defect_penalty + flow_bonus)))

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

            # Collect abandoned items for details
            detail_items = None
            if critical_count > 0:
                detail_items = []
                for item in self.aging_analysis.critical_items:
                    if item.category == AgingCategory.ABANDONED:
                        detail_items.append({
                            "key": item.key,
                            "summary": item.summary,
                            "age_days": item.age_days,
                            "status": item.status,
                            "assignee": item.assignee or "Unassigned",
                            "type": "abandoned"
                        })
                # Also include stale items if space permits
                for item in self.aging_analysis.critical_items:
                    if item.category == AgingCategory.STALE and len(detail_items) < 20:
                        detail_items.append({
                            "key": item.key,
                            "summary": item.summary,
                            "age_days": item.age_days,
                            "status": item.status,
                            "assignee": item.assignee or "Unassigned",
                            "type": "stale"
                        })
                # Sort by age descending (oldest first)
                if detail_items:
                    detail_items.sort(key=lambda x: x["age_days"], reverse=True)
            
            components.append(
                HealthScoreComponent(
                    name="Aging Items",
                    score=score,
                    description=(
                        f"Based on {critical_count} critical items out of "
                        f"{self.aging_analysis.total_items} total"
                    ),
                    insights=insights,
                    recommendations=recommendations,
                    detail_items=detail_items,
                )
            )

        if self.wip_analysis:
            # WIP component with smarter scoring
            violation_count = sum(self.wip_analysis.wip_violations.values())
            total_limit = sum(self.wip_analysis.wip_limits.values())
            
            # Calculate score based on severity of violations
            if total_limit > 0:
                violation_ratio = violation_count / total_limit
                score = max(0, 1 - violation_ratio)
            else:
                score = 1.0 if violation_count == 0 else 0.5

            insights = []
            # Provide team size context
            team_size = len(self.wip_analysis.wip_by_assignee)
            if team_size > 0:
                insights.append(f"Team size: {team_size} active members")
                
            if violation_count > 0:
                for status, count in self.wip_analysis.wip_violations.items():
                    limit = self.wip_analysis.wip_limits.get(status, 0)
                    actual = len(self.wip_analysis.items_by_status.get(status, []))
                    insights.append(f"{status.value}: {actual}/{limit} items ({count} over limit)")
            else:
                insights.append("All WIP limits are being respected")

            recommendations = []
            if score < 0.8:
                recommendations.append("Reduce work in progress to improve flow")
                if self.wip_analysis.wip_by_assignee:
                    # Calculate ideal WIP per person based on team size
                    ideal_wip = max(2, 5 - team_size // 3)  # Smaller teams can handle more per person
                    overloaded = [
                        (name, count) for name, count in self.wip_analysis.wip_by_assignee.items() 
                        if count > ideal_wip
                    ]
                    if overloaded:
                        overloaded.sort(key=lambda x: x[1], reverse=True)
                        recommendations.append(
                            f"Rebalance work: {overloaded[0][0]} has {overloaded[0][1]} items "
                            f"(ideal: {ideal_wip} per person)"
                        )

            components.append(
                HealthScoreComponent(
                    name="Work In Progress",
                    score=score,
                    description=(
                        f"{self.wip_analysis.total_wip} items in progress, "
                        f"{violation_count} WIP limit violations"
                    ),
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
        
        if self.lead_time_analysis:
            # Lead time component with improved scoring
            avg_lead_time = self.lead_time_analysis.average_lead_time
            
            # Lead time score: excellent < 7 days, good < 14 days, declining after
            if avg_lead_time <= 7:
                lead_time_score = 1.0
            elif avg_lead_time <= 14:
                lead_time_score = 0.9
            elif avg_lead_time <= 21:
                lead_time_score = 0.7
            elif avg_lead_time <= 30:
                lead_time_score = 0.5
            else:
                # Gradually decline for very long lead times
                lead_time_score = max(0.2, 0.5 - (avg_lead_time - 30) / 60)
            
            # Defect penalty: scale based on defect rate
            defect_penalty = min(0.3, self.lead_time_analysis.defect_rate * 0.5)
            
            # Flow efficiency bonus: high efficiency indicates good process flow
            flow_eff = self.lead_time_analysis.average_flow_efficiency
            flow_bonus = 0
            if flow_eff > 0.8:  # Excellent flow efficiency
                flow_bonus = 0.1
            elif flow_eff > 0.6:  # Good flow efficiency
                flow_bonus = 0.05
            
            # Calculate final score with bounds [0, 1]
            score = max(0, min(1, lead_time_score - defect_penalty + flow_bonus))
            
            insights = []
            insights.append(f"Average lead time: {avg_lead_time:.1f} days")
            insights.append(f"Median lead time: {self.lead_time_analysis.median_lead_time:.1f} days")
            if self.lead_time_analysis.defect_rate > 0:
                insights.append(f"Defect rate: {self.lead_time_analysis.defect_rate:.1%}")
            
            if flow_eff > 0:
                insights.append(f"Flow efficiency: {flow_eff:.1%} (active work time vs wait time)")
            
            recommendations = []
            if avg_lead_time > 21:
                recommendations.append("Focus on reducing cycle time for faster delivery")
            if self.lead_time_analysis.defect_rate > 0.15:
                recommendations.append("High defect rate - improve quality practices")
            elif self.lead_time_analysis.defect_rate > 0.10:
                recommendations.append("Consider additional quality checks to reduce defects")
            
            if flow_eff < 0.4 and flow_eff > 0:
                recommendations.append("Low flow efficiency - reduce wait times between work stages")
            elif flow_eff > 0.8:
                insights.append("Excellent flow efficiency indicates minimal wait times")
            
            components.append(
                HealthScoreComponent(
                    name="Lead Time & Quality",
                    score=score,
                    description=f"Based on {len(self.lead_time_analysis.metrics)} completed items",
                    insights=insights,
                    recommendations=recommendations,
                )
            )

        return components


@dataclass
class LeadTimeMetrics:
    """Metrics for lead time analysis"""
    
    issue_key: str
    created_date: datetime
    resolved_date: Optional[datetime]
    lead_time_days: Optional[float]
    cycle_time_days: Optional[float]  # Time from first move to done
    wait_time_days: Optional[float]  # Time spent waiting/blocked
    issue_type: str
    labels: List[str] = field(default_factory=list)
    
    @property
    def is_defect(self) -> bool:
        """Check if issue is a defect/bug"""
        return self.issue_type.lower() in ["bug", "defect", "incident"]
    
    @property
    def flow_efficiency(self) -> Optional[float]:
        """Calculate flow efficiency (active time / total time)"""
        if self.lead_time_days and self.cycle_time_days:
            return self.cycle_time_days / self.lead_time_days
        return None


@dataclass 
class LeadTimeAnalysis:
    """Analysis of lead times across issues"""
    
    metrics: List[LeadTimeMetrics]
    
    @property
    def average_lead_time(self) -> float:
        """Average lead time in days"""
        lead_times = [m.lead_time_days for m in self.metrics if m.lead_time_days]
        return sum(lead_times) / len(lead_times) if lead_times else 0
    
    @property
    def median_lead_time(self) -> float:
        """Median lead time in days"""
        lead_times = sorted([m.lead_time_days for m in self.metrics if m.lead_time_days])
        if not lead_times:
            return 0
        mid = len(lead_times) // 2
        if len(lead_times) % 2 == 0:
            return (lead_times[mid - 1] + lead_times[mid]) / 2
        return lead_times[mid]
    
    @property
    def defect_rate(self) -> float:
        """Percentage of issues that are defects"""
        if not self.metrics:
            return 0
        defect_count = sum(1 for m in self.metrics if m.is_defect)
        return defect_count / len(self.metrics)
    
    @property
    def average_flow_efficiency(self) -> float:
        """Average flow efficiency across resolved issues"""
        efficiencies = [m.flow_efficiency for m in self.metrics if m.flow_efficiency]
        return sum(efficiencies) / len(efficiencies) if efficiencies else 0
    
    @property
    def lead_time_percentiles(self) -> Dict[int, float]:
        """Calculate lead time percentiles"""
        lead_times = sorted([m.lead_time_days for m in self.metrics if m.lead_time_days])
        if not lead_times:
            return {50: 0, 85: 0, 95: 0}
        
        def percentile(data, p):
            n = len(data)
            k = (n - 1) * p / 100
            f = int(k)
            c = k - f
            if f + 1 < n:
                return data[f] * (1 - c) + data[f + 1] * c
            else:
                return data[f]
        
        return {
            50: percentile(lead_times, 50),
            85: percentile(lead_times, 85),
            95: percentile(lead_times, 95),
        }
