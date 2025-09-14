from enum import StrEnum


class QueueName(StrEnum):
    MODERATION_IN = "text_moderation_in"
    PROCESS_MODERATION_RESULT = "process_moderation_result"
    DLQ_TEXT_MODERATION = "dlq_text_moderation"


class ExchangeName(StrEnum):
    DLX_TEXT_CLASSIFIER = "dlx_text_classifier"
