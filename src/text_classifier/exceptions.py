import json
from http import HTTPStatus
from typing import Any


class AppError(Exception):
    _status_code: int | None = None
    _is_recoverable: bool | None = None

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        *,
        _is_recoverable: bool | None = None,
    ):
        super().__init__(message)
        if status_code is not None:
            self._status_code = status_code
        if _is_recoverable is not None:
            self._is_recoverable = _is_recoverable

    @property
    def status_code(self) -> int:
        if self._status_code is None:
            return HTTPStatus.INTERNAL_SERVER_ERROR
        return self._status_code

    @property
    def is_recoverable(self) -> bool:
        return self._is_recoverable or HTTPStatus(self.status_code).is_server_error

    def to_json(self) -> str:
        dict_data = self.to_dict()
        return json.dumps(dict_data)

    def to_dict(self) -> dict[str, Any]:
        return {"msg": str(self), "is_recoverable": self.is_recoverable}
