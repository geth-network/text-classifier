from asyncio import Lock
from loguru import logger
from text_classifier.infra.repositories.result.base import BaseResultRepository
from text_classifier.infra.repositories.result.exceptions import DuplicatedResultError, \
    ResultNotFoundError
from text_classifier.infra.repositories.result.models import ModerationResult


class InMemoryResultRepository(BaseResultRepository):
    _repo_lock = Lock()

    def __init__(self) -> None:
        self._storage: dict[str, ModerationResult] = {}

    async def set(self, result: ModerationResult) -> None:
        logger.bind(result=result.model_dump()).info("Saving moderation result")
        async with self._repo_lock:
            if result.task_id in self._storage:
                raise DuplicatedResultError(
                    f"Result with {result.task_id=} already exists"
                )
            self._storage[result.task_id] = result

    async def get(self, task_id: str) -> ModerationResult:
        async with self._repo_lock:
            try:
                result = self._storage[task_id]
            except KeyError as err:
                raise ResultNotFoundError(f"Result with {task_id=} not found") from err
        logger.bind(result=result.model_dump()).info("Got moderation result from DB")
        return result
