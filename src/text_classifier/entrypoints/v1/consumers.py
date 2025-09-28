from typing import Any

from faststream.rabbit import RabbitExchange, RabbitQueue
from faststream.rabbit.fastapi import RabbitMessage, RabbitRouter
from loguru import logger

from text_classifier.entrypoints.v1.deps import DebertaRepoDep, ResultRepoDep
from text_classifier.entrypoints.v1.enums import ExchangeName, QueueName
from text_classifier.entrypoints.v1.schemas import ModerationRequest
from text_classifier.infra.repositories.result.models import ModerationResult
from text_classifier.services import text_moderator

router = RabbitRouter()


@router.subscriber(
    queue=RabbitQueue(
        name=QueueName.MODERATION_IN,
        durable=True,
        arguments={
            "x-max-priority": 3,
            "x-dead-letter-exchange": ExchangeName.DLX_TEXT_CLASSIFIER,
            "x-dead-letter-routing-key": QueueName.DLQ_TEXT_MODERATION,
            "x-max-length": 5000,
            "x-overflow": "reject-publish-dlx",
            "x-expires": 259200000,  # 3 days
        },
    )
)
def moderate_text(repo: DebertaRepoDep, request: ModerationRequest) -> ModerationResult:
    return text_moderator.moderate(repo, request.task_id, request.text)


@router.subscriber(
    queue=RabbitQueue(
        name=QueueName.PROCESS_MODERATION_RESULT,
        durable=True,
        arguments={
            "x-max-priority": 3,
            "x-dead-letter-exchange": ExchangeName.DLX_TEXT_CLASSIFIER,
            "x-dead-letter-routing-key": QueueName.DLQ_TEXT_MODERATION,
            "x-max-length": 5000,
            "x-overflow": "reject-publish-dlx",
            "x-expires": 259200000,  # 3 days
        },
    ),
    no_reply=True,
)
def process_moderation_result_consumer(
    request: ModerationResult, repo: ResultRepoDep
) -> None:
    text_moderator.process_result(repo, request)


@router.subscriber(
    queue=RabbitQueue(
        name=QueueName.DLQ_TEXT_MODERATION,
        durable=True,
        arguments={
            "x-expires": 259200000  # 3 days
        },
    ),
    exchange=RabbitExchange(name=ExchangeName.DLX_TEXT_CLASSIFIER, durable=True),
    no_reply=True,
)
def dlq_moderation_consumer(
    body: dict[str, Any], msg: RabbitMessage, repo: ResultRepoDep
) -> None:
    logger.bind(body=body, headers=msg.raw_message.headers).error(
        "Caught dead lettered message"
    )
    if task_id := body.get("task_id"):
        text_moderator.handle_dead_message(repo, task_id)
