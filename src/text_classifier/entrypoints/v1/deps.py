from typing import Annotated

from fastapi import Depends

from text_classifier.infra.repositories.deberta import DebertaRepo, get_deberta_repo
from text_classifier.infra.repositories.result import InMemoryResultRepository
from text_classifier.infra.repositories.result.in_memory import get_result_repo

DebertaRepoDep = Annotated[DebertaRepo, Depends(get_deberta_repo)]
ResultRepoDep = Annotated[InMemoryResultRepository, Depends(get_result_repo)]
