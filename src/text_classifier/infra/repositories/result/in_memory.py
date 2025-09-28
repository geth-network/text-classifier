from threading import Lock

from loguru import logger

from text_classifier.infra.repositories.result.base import BaseResultRepository
from text_classifier.infra.repositories.result.exceptions import (
    DuplicatedResultError,
    ResultNotFoundError,
)
from text_classifier.infra.repositories.result.models import ModerationResult

_repo_lock = Lock()


class InMemoryResultRepository(BaseResultRepository):
    def __init__(self) -> None:
        self._storage: dict[str, ModerationResult] = {}

    def save(self, result: ModerationResult) -> None:
        logger.bind(result=result.model_dump()).info("Saving moderation result")
        with _repo_lock:
            if result.task_id.hex in self._storage:
                raise DuplicatedResultError(
                    f"Result with {result.task_id=} already exists"
                )
            self._storage[result.task_id.hex] = result

    def get(self, task_id: str) -> ModerationResult:
        with _repo_lock:
            try:
                result = self._storage[task_id]
            except KeyError as err:
                raise ResultNotFoundError(f"Result with {task_id=} not found") from err
        logger.bind(result=result.model_dump()).info("Got moderation result from DB")
        return result

    def list(self, *, limit: int, offset: int) -> list[ModerationResult]:
        with _repo_lock:
            results = list(self._storage.values())[offset:limit]
        logger.bind(results=results).info("Got moderation results from DB")
        return results


_repo: InMemoryResultRepository | None = None


def get_result_repo() -> InMemoryResultRepository:
    global _repo  # noqa: PLW0603
    with _repo_lock:
        if _repo is None:
            _repo = InMemoryResultRepository()
            logger.info("Initialized result repo")
    return _repo
