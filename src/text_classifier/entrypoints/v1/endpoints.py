import uuid

from faststream.rabbit.fastapi import RabbitRouter
from loguru import logger
from text_classifier.entrypoints.v1.enums import QueueName
from text_classifier.entrypoints.v1.schemas import (
    EnqueuedModerationText,
    EnqueueModerationText, ModerationRequest,
)
from asgi_correlation_id import correlation_id

router = RabbitRouter()


@router.post("/queues/classifiers/moderation/")
async def dispatch_request(request: EnqueueModerationText) -> EnqueuedModerationText:
    moderation_request = ModerationRequest(text=request.text)
    await router.broker.publish(
        moderation_request,
        queue=QueueName.MODERATION_IN,
        mandatory=True,
        persist=True,
        correlation_id=correlation_id.get() or uuid.uuid4().hex,
    )
    return EnqueuedModerationText(task_id=moderation_request.task_id)
