from fastapi.exceptions import RequestValidationError
from faststream import ExceptionMiddleware
from faststream.exceptions import RejectMessage
from loguru import logger

exception_middleware = ExceptionMiddleware()


@exception_middleware.add_handler(RequestValidationError)
def validation_error_handler(exc: RequestValidationError) -> None:
    logger.bind(error=exc.errors()).info("Failed data validation")
    raise RejectMessage


@exception_middleware.add_handler(Exception)
async def generic_error_handler(exc: Exception) -> None:
    logger.bind(error=exc).error("Encountered unknown error")
    raise RejectMessage
