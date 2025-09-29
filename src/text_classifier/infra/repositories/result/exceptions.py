from http import HTTPStatus

from text_classifier.exceptions import AppError


class ResultRepoError(AppError):
    pass


class DuplicatedResultError(ResultRepoError):
    _status_code = HTTPStatus.CONFLICT


class ResultNotFoundError(ResultRepoError):
    _status_code = HTTPStatus.NOT_FOUND
