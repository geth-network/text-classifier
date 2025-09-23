from typing import Self

from pydantic import UUID4, model_validator

from text_classifier.common_types import FrozenModel


class TaskResult(FrozenModel):
    label: str
    score: float


class TaskError(FrozenModel):
    error_msg: str
    status_code: int
    is_recoverable: bool


class ModerationResult(FrozenModel):
    task_id: UUID4
    result: TaskResult | None
    error: TaskError | None

    @model_validator(mode="after")
    def validate_result(self) -> Self:
        if (not self.result and not self.error) or (self.result and self.error):
            raise ValueError("Either `result` or `error` must be set")
        if self.result and self.error:
            raise ValueError("Cannot set both `result` and `error`")
        return self
