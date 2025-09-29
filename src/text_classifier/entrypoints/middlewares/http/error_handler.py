from fastapi import Request
from fastapi.responses import ORJSONResponse
from loguru import logger

from text_classifier.exceptions import AppError


def app_error_handler(_: Request, exc: AppError) -> ORJSONResponse:
    logger.bind(error=exc.to_dict()).info("Encountered app error")
    return ORJSONResponse(exc.to_dict(), status_code=exc.status_code)


def generic_error_handler(_: Request, exc: Exception) -> ORJSONResponse:
    logger.bind(error=exc).error("Encountered unknown error")
    error = AppError(str(exc))
    return ORJSONResponse(error.to_dict(), status_code=error.status_code)
