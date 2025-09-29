from http import HTTPStatus
from uuid import UUID

from loguru import logger

from text_classifier.infra.repositories.deberta import DebertaRepo
from text_classifier.infra.repositories.result import InMemoryResultRepository
from text_classifier.infra.repositories.result.models import (
    ModerationResult,
    TaskError,
    TaskResult,
)


def moderate(deberta: DebertaRepo, task_id: UUID, text: str) -> ModerationResult:
    error: TaskError | None
    try:
        output = deberta.run_pipeline(text)
    except Exception as err:  # noqa: BLE001
        logger.bind(error=err, input_text=text).error(
            "Encountered unknown error while running pipeline"
        )
        error = TaskError(
            error_msg="Internal server error",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            is_recoverable=True,
        )
        task_result = None
    else:
        error = None
        task_result = TaskResult(label=output["category"], score=output["score"])
    result = ModerationResult(task_id=task_id, result=task_result, error=error)
    logger.bind(task_result=result.model_dump_json()).info("Completed text moderation")
    return result


def process_result(repo: InMemoryResultRepository, result: ModerationResult) -> None:
    logger.bind(result=result.model_dump_json()).info("Processing moderation result")
    repo.save(result)


def retrieve_result(repo: InMemoryResultRepository, task_id: UUID) -> ModerationResult:
    return repo.get(task_id)


def list_results(
    repo: InMemoryResultRepository, limit: int, offset: int
) -> list[ModerationResult]:
    return repo.list(limit=limit, offset=offset)


def handle_dead_message(repo: InMemoryResultRepository, task_id: str) -> None:
    result = ModerationResult(
        task_id=task_id,
        result=None,
        error=TaskError(
            error_msg="Internal server error",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            is_recoverable=True,
        ),
    )
    repo.save(result)
