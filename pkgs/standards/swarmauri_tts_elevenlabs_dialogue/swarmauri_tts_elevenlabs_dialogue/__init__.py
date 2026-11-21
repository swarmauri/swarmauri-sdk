"""Alpha elevenlabs_dialogue speech interface; live verification pending."""

from .ElevenLabsDialogueTTS import (
    ElevenLabsDialogueTTS,
    DialogueInput,
    DialogueTurn,
)

__version__ = "0.1.0a1"
__all__ = [
    "ElevenLabsDialogueTTS",
    "__version__",
    "DialogueInput",
    "DialogueTurn",
]
