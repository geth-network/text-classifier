import uuid
from typing import Annotated

from pydantic import UUID4, Field

from text_classifier.common_types import FrozenModel


class EnqueueModerationText(FrozenModel):
    text: Annotated[str, Field(min_length=1, max_length=8000)]


class EnqueuedTask(FrozenModel):
    task_id: UUID4


class ModerationRequest(EnqueueModerationText):
    task_id: Annotated[UUID4, Field(default_factory=lambda: uuid.uuid4())]


class ErrorResponse(FrozenModel):
    msg: str
    is_recoverable: bool
