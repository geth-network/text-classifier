from faststream.rabbit import RabbitExchange, RabbitQueue
from faststream.rabbit.fastapi import RabbitRouter

from text_classifier.entrypoints.v1.enums import ExchangeName, QueueName
from text_classifier.entrypoints.v1.schemas import ModerationRequest

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
    ),
    no_reply=True,
)
def moderate_text(request: ModerationRequest) -> None:
    pass


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
async def process_moderation_result() -> None:
    pass


@router.subscriber(
    queue=RabbitQueue(
        name=QueueName.DLQ_TEXT_MODERATION,
        exchange=RabbitExchange(name=ExchangeName.DLX_TEXT_CLASSIFIER, durable=True),
    ),
    no_reply=True,
)
async def dlq_moderation_consumer() -> None:
    pass
