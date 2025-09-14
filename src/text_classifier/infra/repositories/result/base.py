from abc import ABC, abstractmethod

from text_classifier.infra.repositories.result.models import ModerationResult


class BaseResultRepository(ABC):


    @abstractmethod
    async def get(self, task_id: str) -> ModerationResult:
        pass

    @abstractmethod
    async def set(self, result: ModerationResult) -> str:
        pass
