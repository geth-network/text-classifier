import uuid
from datetime import timedelta
from http import HTTPStatus
from typing import Annotated

from asgi_correlation_id import correlation_id
from fastapi import Query
from faststream.rabbit.fastapi import RabbitRouter
from loguru import logger
from pydantic import UUID4

from text_classifier.entrypoints.v1.deps import ResultRepoDep
from text_classifier.entrypoints.v1.enums import QueueName
from text_classifier.entrypoints.v1.schemas import (
    EnqueuedTask,
    EnqueueModerationText,
    ErrorResponse,
    ModerationRequest,
)
from text_classifier.infra.repositories.result.models import (
    ListModerationResults,
    ModerationResult,
)
from text_classifier.services import text_moderator

router = RabbitRouter(logger=logger)


@router.post("/queues/classifiers/moderation/")
async def dispatch_request(request: EnqueueModerationText) -> EnqueuedTask:
    moderation_request = ModerationRequest(text=request.text, task_id=uuid.uuid4())
    await router.broker.publish(
        moderation_request,
        queue=QueueName.MODERATION_IN,
        mandatory=True,
        persist=True,
        correlation_id=correlation_id.get() or uuid.uuid4().hex,
        expiration=timedelta(minutes=15),
        reply_to=QueueName.PROCESS_MODERATION_RESULT,
    )
    logger.bind(task=moderation_request.model_dump_json()).info(
        "Enqueued moderation task"
    )
    return EnqueuedTask(task_id=moderation_request.task_id)


@router.get(
    "/queues/classifiers/moderation/{task_id}",
    responses={HTTPStatus.NOT_FOUND: {"model": ErrorResponse}},
)
def get_result(repo: ResultRepoDep, task_id: UUID4) -> ModerationResult:
    return text_moderator.retrieve_result(repo, task_id)


@router.get("/queues/classifiers/moderation/")
def list_results(
    repo: ResultRepoDep,
    limit: Annotated[int, Query(le=1000, ge=1)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ListModerationResults:
    results = text_moderator.list_results(repo, limit, offset)
    return ListModerationResults(data=results)
