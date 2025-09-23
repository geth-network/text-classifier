import time
from typing import ClassVar, TypedDict

from loguru import logger
from transformers import Pipeline, pipeline

from text_classifier.infra.repositories.enums import DebertaCategory


class ModelOutput(TypedDict):
    label: str
    score: float


class PipelineResult(TypedDict):
    category: DebertaCategory
    score: float


class DebertaRepo:
    _LABELS_TO_CATEGORY: ClassVar[dict[str, DebertaCategory]] = {
        "S": DebertaCategory.SEXUAL,
        "H": DebertaCategory.HATE,
        "V": DebertaCategory.VIOLENCE,
        "HR": DebertaCategory.HARASSMENT,
        "SH": DebertaCategory.SELF_HARM,
        "S3": DebertaCategory.SEXUAL_MINORS,
        "H2": DebertaCategory.HATE_THREATENING,
        "V2": DebertaCategory.VIOLENCE_GRAPHIC,
        "OK": DebertaCategory.OK,
    }

    def __init__(self, pipe: Pipeline) -> None:
        self._pipe = pipe

    def run_pipeline(self, text: str) -> PipelineResult:
        logger.bind(text=text).info("Running pipeline")
        start = time.monotonic()
        scores = self._pipe(text)
        end = time.monotonic()
        logger.bind(model_output=scores, elapsed=end - start).info("Completed pipeline")
        max_label = self._get_max_label(scores)
        humanized_label = self._LABELS_TO_CATEGORY[max_label["label"]]
        return PipelineResult(category=humanized_label, score=max_label["score"])

    def _get_max_label(self, result: list[ModelOutput]) -> ModelOutput:
        return sorted(result, key=lambda x: x["score"], reverse=True)[0]


_pipeline = None


def init_pipeline():  # TODO use local path
    global _pipeline  # noqa: PLW0603
    if _pipeline is None:
        _pipeline = pipeline("text-classification", model="KoalaAI/Text-Moderation")
    return _pipeline
