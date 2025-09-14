import time
from typing import ClassVar, TypedDict

from loguru import logger
from transformers import pipeline, Pipeline
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from text_classifier.infra.repositories.enums import DebertaCategory


class PipelineResult(TypedDict):
    label: str
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

    def run_pipeline(self, text: str) -> DebertaCategory:
        logger.bind(text=text).info("Running pipeline")
        start = time.monotonic()
        res = self._pipe(text)
        end = time.monotonic()
        logger.bind(pipeline_result=res, elapsed=end-start).info("Completed pipeline")
        max_label = self._get_max_label(res)
        return self._LABELS_TO_CATEGORY[max_label]

    def _get_max_label(self, result: list[PipelineResult]) -> str:
        return sorted(result, key=lambda x: x["score"], reverse=True)[0]["label"]


def init_pipeline():  # TODO use local path
    return pipeline("text-classification", model="KoalaAI/Text-Moderation")
