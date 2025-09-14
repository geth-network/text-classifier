from enum import StrEnum


# https://huggingface.co/KoalaAI/Text-Moderation#text-moderation
class DebertaCategory(StrEnum):
    SEXUAL = "Sexual"
    HATE = "Hate"
    VIOLENCE = "Violence"
    HARASSMENT = "Harassment"
    SELF_HARM = "Self-harm"
    SEXUAL_MINORS = "Sexual/minors"
    HATE_THREATENING = "Hate/threatening"
    VIOLENCE_GRAPHIC = "Violence/graphic"
    OK = "OK"
