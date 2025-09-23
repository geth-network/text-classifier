from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter

from text_classifier.entrypoints.middlewares.rabbit.context import ContextMiddleware
from text_classifier.entrypoints.v1.consumers import router as consumers_router
from text_classifier.entrypoints.v1.endpoints import router as v1_router


def _init_core_router() -> RabbitRouter:
    router = RabbitRouter(middlewares=(ContextMiddleware,))
    router.include_router(consumers_router)
    return router


def create_app() -> None:
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    core_router = _init_core_router()
    app.include_router(core_router)
    app.include_router(v1_router, prefix="/v1")
