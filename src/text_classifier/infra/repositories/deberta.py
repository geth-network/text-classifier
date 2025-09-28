import time
from threading import Lock
from typing import ClassVar, TypedDict

from loguru import logger
from transformers import Pipeline, TextClassificationPipeline, pipeline

from text_classifier.infra.repositories.enums import DebertaCategory

_lock = Lock()


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
        output: ModelOutput = self._pipe(text)[0]
        end = time.monotonic()
        logger.bind(model_output=output, elapsed=end - start).info("Completed pipeline")
        humanized_label = self._LABELS_TO_CATEGORY[output["label"]]
        return PipelineResult(category=humanized_label, score=output["score"])


_pipeline = None


def init_pipeline(path: str = "KoalaAI/Text-Moderation") -> TextClassificationPipeline:
    global _pipeline  # noqa: PLW0603
    if _pipeline is None:
        with _lock:
            _pipeline = pipeline("text-classification", path)
            logger.bind(path=path).info("Initialized pipeline")
    return _pipeline


def get_deberta_repo(pipe: TextClassificationPipeline | None = None) -> DebertaRepo:
    if pipe is None:
        pipe = init_pipeline()
    return DebertaRepo(pipe)
