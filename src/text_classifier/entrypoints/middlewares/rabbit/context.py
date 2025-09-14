from contextlib import ExitStack
from typing import Any, Awaitable, Callable

from loguru import logger
from faststream import BaseMiddleware
from aio_pika.message import IncomingMessage
from faststream.broker.message import StreamMessage


class ContextMiddleware(BaseMiddleware):

    async def consume_scope(
        self,
        call_next: Callable[[Any], Awaitable[Any]],
        msg: StreamMessage[IncomingMessage],
    ) -> Any:
        raw_message = msg.raw_message
        with ExitStack() as stack:
            stack.enter_context(
                logger.contextualize(
                    correlation_id=raw_message.correlation_id,
                    routing_key=raw_message.routing_key,
                )
            )
            logger.bind(raw_body=msg.body, properties=dict(raw_message.properties)).info(
                "Received new rabbit message"
            )
            return await call_next(msg)

    async def on_publish(
        self,
        msg: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        logger.bind(msg=msg, args=args, kwargs=kwargs).info(
            "Publishing message to RabbitMQ"
        )
        return msg
