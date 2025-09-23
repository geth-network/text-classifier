from http import HTTPStatus
from uuid import UUID

from loguru import logger

from text_classifier.infra.repositories.deberta import init_pipeline
from text_classifier.infra.repositories.result.in_memory import get_result_repo
from text_classifier.infra.repositories.result.models import (
    ModerationResult,
    TaskError,
    TaskResult,
)


def moderate(task_id: UUID, text: str) -> None:
    deberta = init_pipeline()
    result_repo = get_result_repo()
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
        result = None
    else:
        error = None
        result = TaskResult(label=output["category"], score=output["score"])
    moderation_result = ModerationResult(task_id=task_id, result=result, error=error)
    result_repo.save(moderation_result)


def retrieve_result(task_id: str) -> ModerationResult:
    result_repo = get_result_repo()
    return result_repo.get(task_id)


def handle_dead_message(task_id: str) -> None:
    result_repo = get_result_repo()
    result = ModerationResult(
        task_id=task_id,
        result=None,
        error=TaskError(
            error_msg="Internal server error",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            is_recoverable=True,
        ),
    )
    result_repo.save(result)
