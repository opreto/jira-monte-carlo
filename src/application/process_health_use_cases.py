"""Use cases for process health metrics analysis"""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from ..domain.process_health import (
    AgingAnalysis,
    AgingCategory,
    AgingItem,
    BlockedItem,
    BlockedItemsAnalysis,
    ProcessHealthMetrics,
    SprintHealth,
    SprintHealthAnalysis,
    WIPAnalysis,
    WIPItem,
    WIPStatus,
)
from ..domain.repositories import IssueRepository, SprintRepository


logger = logging.getLogger(__name__)


class AnalyzeAgingWorkItemsUseCase:
    """Analyze aging work items that have been in progress too long"""

    def __init__(self, issue_repository: IssueRepository):
        self.issue_repository = issue_repository

    def execute(self, status_mapping: Dict[str, List[str]]) -> Optional[AgingAnalysis]:
        """Analyze aging work items"""
        # Get all non-done issues
        done_statuses = status_mapping.get("done", [])
        all_issues = self.issue_repository.get_all()

        # Filter to only in-progress items
        in_progress_issues = [issue for issue in all_issues if issue.status not in done_statuses]

        if not in_progress_issues:
            logger.warning("No in-progress issues found for aging analysis")
            return None

        # Compute dynamic aging thresholds based on data distribution
        ages = sorted([issue.age for issue in in_progress_issues])
        self._aging_thresholds = self._compute_aging_thresholds(ages)

        # Categorize items by age
        items_by_category = defaultdict(list)
        all_aging_items = []
        blocked_items = []

        for issue in in_progress_issues:
            age_days = issue.age
            category = self._get_aging_category(age_days)

            aging_item = AgingItem(
                key=issue.key,
                summary=issue.summary,
                status=issue.status,
                age_days=age_days,
                category=category,
                assignee=issue.assignee,
                last_updated=issue.updated,
                created=issue.created,
                story_points=issue.story_points,
            )

            items_by_category[category].append(aging_item)
            all_aging_items.append(aging_item)

            if aging_item.is_blocked:
                blocked_items.append(aging_item)

        # Calculate average age by status
        age_by_status = defaultdict(list)
        for item in all_aging_items:
            age_by_status[item.status].append(item.age_days)

        average_age_by_status = {status: sum(ages) / len(ages) for status, ages in age_by_status.items()}

        # Get oldest items
        oldest_items = sorted(all_aging_items, key=lambda x: x.age_days, reverse=True)[:10]

        return AgingAnalysis(
            items_by_category=dict(items_by_category),
            average_age_by_status=average_age_by_status,
            oldest_items=oldest_items,
            blocked_items=blocked_items,
            total_items=len(all_aging_items),
            thresholds=self._aging_thresholds,
        )

    def _get_aging_category(self, age_days: int) -> AgingCategory:
        """Determine aging category based on days"""
        # Dynamic thresholds - will be set based on data distribution
        if hasattr(self, "_aging_thresholds"):
            thresholds = self._aging_thresholds
            if age_days <= thresholds["fresh"]:
                return AgingCategory.FRESH
            elif age_days <= thresholds["normal"]:
                return AgingCategory.NORMAL
            elif age_days <= thresholds["aging"]:
                return AgingCategory.AGING
            elif age_days <= thresholds["stale"]:
                return AgingCategory.STALE
            else:
                return AgingCategory.ABANDONED
        else:
            # Fallback to sensible defaults if thresholds not computed
            if age_days <= 7:
                return AgingCategory.FRESH
            elif age_days <= 14:
                return AgingCategory.NORMAL
            elif age_days <= 30:
                return AgingCategory.AGING
            elif age_days <= 60:
                return AgingCategory.STALE
            else:
                return AgingCategory.ABANDONED

    def _compute_aging_thresholds(self, ages: List[int]) -> Dict[str, int]:
        """Compute percentile-based aging thresholds"""
        if not ages:
            return {"fresh": 7, "normal": 14, "aging": 30, "stale": 60}

        # Use percentiles to set thresholds
        # Fresh: bottom 20%
        # Normal: 20-40%
        # Aging: 40-60%
        # Stale: 60-80%
        # Abandoned: top 20%

        n = len(ages)
        fresh_idx = max(0, int(n * 0.2) - 1)
        normal_idx = max(0, int(n * 0.4) - 1)
        aging_idx = max(0, int(n * 0.6) - 1)
        stale_idx = max(0, int(n * 0.8) - 1)

        return {
            "fresh": ages[fresh_idx],
            "normal": ages[normal_idx],
            "aging": ages[aging_idx],
            "stale": ages[stale_idx],
        }


class AnalyzeWorkInProgressUseCase:
    """Analyze current work in progress and WIP limits"""

    def __init__(self, issue_repository: IssueRepository):
        self.issue_repository = issue_repository

    def execute(
        self, status_mapping: Dict[str, List[str]], wip_limits: Optional[Dict[str, int]] = None
    ) -> Optional[WIPAnalysis]:
        """Analyze work in progress"""
        # Get all non-done issues
        done_statuses = status_mapping.get("done", [])
        all_issues = self.issue_repository.get_all()

        # Categorize by WIP status
        items_by_status = defaultdict(list)
        wip_by_assignee = defaultdict(int)

        for issue in all_issues:
            if issue.status in done_statuses:
                continue

            wip_status = self._get_wip_status(issue.status, status_mapping)

            wip_item = WIPItem(
                key=issue.key,
                summary=issue.summary,
                status=issue.status,
                wip_status=wip_status,
                assignee=issue.assignee,
                age_days=issue.age,
                story_points=issue.story_points,
            )

            items_by_status[wip_status].append(wip_item)

            if issue.assignee:
                wip_by_assignee[issue.assignee] += 1

        # Default WIP limits if not provided
        if wip_limits is None:
            # Reasonable defaults based on team size
            team_size = len(wip_by_assignee) or 5
            wip_limits = {
                WIPStatus.IN_PROGRESS: team_size * 2,
                WIPStatus.REVIEW: team_size,
                WIPStatus.BLOCKED: 0,  # Should be 0
            }

        # Convert string keys to WIPStatus enum
        wip_limits_enum = {}
        for status_str, limit in wip_limits.items():
            try:
                wip_status = WIPStatus[status_str.upper()]
                wip_limits_enum[wip_status] = limit
            except (KeyError, AttributeError):
                logger.warning(f"Unknown WIP status: {status_str}")

        total_wip = sum(
            len(items)
            for status, items in items_by_status.items()
            if status != WIPStatus.TODO and status != WIPStatus.DONE
        )

        return WIPAnalysis(
            items_by_status=dict(items_by_status),
            wip_by_assignee=dict(wip_by_assignee),
            total_wip=total_wip,
            wip_limits=wip_limits_enum,
        )

    def _get_wip_status(self, status: str, status_mapping: Dict[str, List[str]]) -> WIPStatus:
        """Map issue status to WIP category"""
        status_lower = status.lower()

        # Check for blocked status
        if any(keyword in status_lower for keyword in ["blocked", "impediment", "waiting", "hold"]):
            return WIPStatus.BLOCKED

        # Check status mapping
        for category, statuses in status_mapping.items():
            if status in statuses:
                if category == "todo":
                    return WIPStatus.TODO
                elif category == "done":
                    return WIPStatus.DONE
                elif category == "in_progress":
                    # Further categorize in-progress items
                    if any(keyword in status_lower for keyword in ["review", "qa", "test"]):
                        return WIPStatus.REVIEW
                    else:
                        return WIPStatus.IN_PROGRESS

        # Default to in-progress if not mapped
        return WIPStatus.IN_PROGRESS


class AnalyzeSprintHealthUseCase:
    """Analyze sprint health metrics and predictability"""

    def __init__(self, issue_repository: IssueRepository, sprint_repository: SprintRepository):
        self.issue_repository = issue_repository
        self.sprint_repository = sprint_repository

    def execute(self, lookback_sprints: int = 12) -> Optional[SprintHealthAnalysis]:
        """Analyze sprint health metrics"""
        sprints = self.sprint_repository.get_last_n_sprints(lookback_sprints)

        if not sprints:
            logger.warning("No sprints found for health analysis")
            return None

        sprint_metrics = []

        for sprint in sprints:
            # Get issues in this sprint
            sprint_issues = [
                issue
                for issue in self.issue_repository.get_all()
                if sprint.name in issue.custom_fields.get("sprint", [])
            ]

            if not sprint_issues:
                continue

            # Calculate metrics
            # Note: This is simplified - in reality, we'd need to track when items were added/removed
            committed_points = sum(
                issue.story_points or 0 for issue in sprint_issues if issue.created <= sprint.start_date
            )

            completed_points = sum(
                issue.story_points or 0
                for issue in sprint_issues
                if issue.resolved and issue.resolved <= sprint.end_date
            )

            # Estimate scope changes (simplified)
            added_points = sum(
                issue.story_points or 0
                for issue in sprint_issues
                if issue.created > sprint.start_date and issue.created <= sprint.end_date
            )

            removed_points = 0  # Would need historical data to track removals

            completion_rate = completed_points / committed_points if committed_points > 0 else 0

            sprint_health = SprintHealth(
                sprint_name=sprint.name,
                start_date=sprint.start_date,
                end_date=sprint.end_date,
                committed_points=committed_points,
                completed_points=completed_points,
                added_points=added_points,
                removed_points=removed_points,
                completion_rate=completion_rate,
            )

            sprint_metrics.append(sprint_health)

        if not sprint_metrics:
            return None

        # Calculate aggregated metrics
        completion_rates = [sm.completion_rate for sm in sprint_metrics]
        average_completion_rate = sum(completion_rates) / len(completion_rates)

        # Calculate trend (positive = improving)
        if len(completion_rates) >= 3:
            recent_avg = sum(completion_rates[-3:]) / 3
            older_avg = sum(completion_rates[:-3]) / len(completion_rates[:-3])
            completion_rate_trend = recent_avg - older_avg
        else:
            completion_rate_trend = 0

        # Calculate average scope change
        scope_changes = [sm.scope_change_percentage for sm in sprint_metrics]
        average_scope_change = sum(scope_changes) / len(scope_changes) if scope_changes else 0

        # Calculate predictability (lower variance = higher predictability)
        if len(completion_rates) >= 2:
            mean_rate = average_completion_rate
            variance = sum((rate - mean_rate) ** 2 for rate in completion_rates) / len(completion_rates)
            std_dev = variance**0.5
            # Convert to 0-1 score (lower std dev = higher score)
            predictability_score = max(0, 1 - (std_dev * 2))  # Penalize high variance
        else:
            predictability_score = 0.5

        return SprintHealthAnalysis(
            sprint_metrics=sprint_metrics,
            average_completion_rate=average_completion_rate,
            completion_rate_trend=completion_rate_trend,
            average_scope_change=average_scope_change,
            predictability_score=predictability_score,
        )


class AnalyzeBlockedItemsUseCase:
    """Analyze blocked items and blocking patterns"""

    def __init__(self, issue_repository: IssueRepository):
        self.issue_repository = issue_repository

    def execute(self, status_mapping: Dict[str, List[str]]) -> Optional[BlockedItemsAnalysis]:
        """Analyze blocked items"""
        all_issues = self.issue_repository.get_all()
        done_statuses = status_mapping.get("done", [])

        blocked_items = []
        blocker_descriptions = []

        for issue in all_issues:
            if issue.status in done_statuses:
                continue

            # Check if blocked (in status or labels)
            is_blocked = False
            blocked_keywords = ["blocked", "impediment", "waiting", "hold"]

            if any(keyword in issue.status.lower() for keyword in blocked_keywords):
                is_blocked = True
            elif any(keyword in label.lower() for label in issue.labels for keyword in blocked_keywords):
                is_blocked = True

            if not is_blocked:
                continue

            # Calculate blocked duration
            # Simplified: assume blocked since last update or creation
            last_activity = issue.updated or issue.created
            blocked_days = (datetime.now() - last_activity).days

            # Extract blocker description from labels or custom fields
            blocker_description = None
            for label in issue.labels:
                if any(keyword in label.lower() for keyword in blocked_keywords):
                    blocker_description = label
                    blocker_descriptions.append(label)
                    break

            blocked_item = BlockedItem(
                key=issue.key,
                summary=issue.summary,
                status=issue.status,
                blocked_days=blocked_days,
                blocker_description=blocker_description,
                assignee=issue.assignee,
                story_points=issue.story_points,
                first_blocked_date=last_activity,
            )

            blocked_items.append(blocked_item)

        if not blocked_items:
            logger.info("No blocked items found")
            return None

        # Calculate metrics
        total_blocked_points = sum(item.story_points or 0 for item in blocked_items)
        average_blocked_days = sum(item.blocked_days for item in blocked_items) / len(blocked_items)

        # Categorize blockers
        blocker_counts = defaultdict(int)
        for desc in blocker_descriptions:
            blocker_counts[desc] += 1

        # Find repeat blockers (occurring more than once)
        repeat_blockers = [blocker for blocker, count in blocker_counts.items() if count > 1]

        return BlockedItemsAnalysis(
            blocked_items=blocked_items,
            total_blocked_points=total_blocked_points,
            average_blocked_days=average_blocked_days,
            blockers_by_type=dict(blocker_counts),
            repeat_blockers=repeat_blockers,
        )


class AnalyzeProcessHealthUseCase:
    """Combine all process health metrics"""

    def __init__(
        self,
        aging_use_case: AnalyzeAgingWorkItemsUseCase,
        wip_use_case: AnalyzeWorkInProgressUseCase,
        sprint_health_use_case: AnalyzeSprintHealthUseCase,
        blocked_items_use_case: AnalyzeBlockedItemsUseCase,
    ):
        self.aging_use_case = aging_use_case
        self.wip_use_case = wip_use_case
        self.sprint_health_use_case = sprint_health_use_case
        self.blocked_items_use_case = blocked_items_use_case

    def execute(
        self,
        status_mapping: Dict[str, List[str]],
        wip_limits: Optional[Dict[str, int]] = None,
        lookback_sprints: int = 12,
    ) -> ProcessHealthMetrics:
        """Execute all process health analyses"""
        logger.info("Analyzing process health metrics...")

        # Run all analyses
        aging_analysis = self.aging_use_case.execute(status_mapping)
        wip_analysis = self.wip_use_case.execute(status_mapping, wip_limits)
        sprint_health = self.sprint_health_use_case.execute(lookback_sprints)
        blocked_items = self.blocked_items_use_case.execute(status_mapping)

        metrics = ProcessHealthMetrics(
            aging_analysis=aging_analysis,
            wip_analysis=wip_analysis,
            sprint_health=sprint_health,
            blocked_items=blocked_items,
        )

        logger.info(f"Process health score: {metrics.health_score:.2f}")

        return metrics
