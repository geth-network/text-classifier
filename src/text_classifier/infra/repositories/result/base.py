from abc import ABC, abstractmethod

from text_classifier.infra.repositories.result.models import ModerationResult


class BaseResultRepository(ABC):
    @abstractmethod
    def get(self, task_id: str) -> ModerationResult:
        pass

    @abstractmethod
    def save(self, result: ModerationResult) -> None:
        pass

    @abstractmethod
    def list(self, *, limit: int, offset: int) -> list[ModerationResult]:
        pass
