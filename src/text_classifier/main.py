import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from http import HTTPStatus

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter
from loguru import logger

from text_classifier import __version__
from text_classifier.entrypoints.middlewares import http, rabbit
from text_classifier.entrypoints.v1.consumers import router as consumers_router
from text_classifier.entrypoints.v1.endpoints import router as v1_router
from text_classifier.entrypoints.v1.schemas import ErrorResponse
from text_classifier.exceptions import AppError
from text_classifier.infra.repositories.deberta import init_pipeline
from text_classifier.tools.log import setup_logging


def _init_core_router(log_level: int) -> RabbitRouter:
    router = RabbitRouter(
        middlewares=(rabbit.ContextMiddleware, rabbit.exception_middleware),
        logger=logger,
        log_level=log_level,
        graceful_timeout=120,
        on_return_raises=True,
    )
    router.include_router(consumers_router)
    return router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    init_pipeline()
    yield
    await logger.complete()


def create_app() -> FastAPI:
    log_min_level = logging.INFO
    setup_logging(min_level=log_min_level)

    app = FastAPI(
        title="Text Classifier",
        version=__version__,
        lifespan=lifespan,
        responses={HTTPStatus.INTERNAL_SERVER_ERROR: {"model": ErrorResponse}},
    )
    app.add_middleware(CorrelationIdMiddleware)
    app.add_exception_handler(AppError, http.app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, http.generic_error_handler)

    core_router = _init_core_router(log_min_level)
    app.include_router(core_router)
    app.include_router(v1_router, prefix="/v1")
    return app
