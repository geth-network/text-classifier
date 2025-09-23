import uuid

from asgi_correlation_id import correlation_id
from faststream.rabbit.fastapi import RabbitRouter

from text_classifier.entrypoints.v1.enums import QueueName
from text_classifier.entrypoints.v1.schemas import (
    EnqueuedModerationText,
    EnqueueModerationText,
    ModerationRequest,
)
from text_classifier.infra.repositories.result.models import ModerationResult
from text_classifier.services import text_moderator

router = RabbitRouter()


@router.post("/queues/classifiers/moderation/")
async def dispatch_request(request: EnqueueModerationText) -> EnqueuedModerationText:
    moderation_request = ModerationRequest(text=request.text, task_id=uuid.uuid4())
    await router.broker.publish(
        moderation_request,
        queue=QueueName.MODERATION_IN,
        mandatory=True,
        persist=True,
        correlation_id=correlation_id.get() or uuid.uuid4().hex,
    )
    return EnqueuedModerationText(task_id=moderation_request.task_id)


@router.get("/queues/classifiers/moderation/{task_id}")
def get_result(task_id: str) -> ModerationResult:
    return text_moderator.retrieve_result(task_id)
