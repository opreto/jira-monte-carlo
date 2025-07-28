from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from .entities import Issue, Sprint
from .value_objects import DateRange, FieldMapping


class IssueRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Issue]:
        pass

    @abstractmethod
    def get_by_status(self, status: str) -> List[Issue]:
        pass

    @abstractmethod
    def get_by_date_range(self, date_range: DateRange) -> List[Issue]:
        pass

    @abstractmethod
    def get_completed_in_range(self, date_range: DateRange) -> List[Issue]:
        pass

    @abstractmethod
    def save_all(self, issues: List[Issue]) -> None:
        """Save/add multiple issues to the repository"""
        pass


class SprintRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Sprint]:
        pass

    @abstractmethod
    def get_by_date_range(self, date_range: DateRange) -> List[Sprint]:
        pass

    @abstractmethod
    def get_last_n_sprints(self, n: int) -> List[Sprint]:
        pass

    @abstractmethod
    def add_sprints(self, sprints: List[Sprint]) -> None:
        """Add multiple sprints to the repository"""
        pass


class ConfigRepository(ABC):
    @abstractmethod
    def save_field_mapping(self, mapping: FieldMapping) -> None:
        pass

    @abstractmethod
    def load_field_mapping(self) -> Optional[FieldMapping]:
        pass

    @abstractmethod
    def save_status_mapping(self, status_mapping: Dict[str, List[str]]) -> None:
        pass

    @abstractmethod
    def load_status_mapping(self) -> Optional[Dict[str, List[str]]]:
        pass
