"""Multi-Recipient Encryption interfaces and types."""

from .types import MultiRecipientEnvelope, RecipientInfo, RecipientId, MreMode

__all__ = [
    "IMreCrypto",
    "MultiRecipientEnvelope",
    "RecipientInfo",
    "RecipientId",
    "MreMode",
]


def __getattr__(name: str):
    if name == "IMreCrypto":
        from .IMreCrypto import IMreCrypto

        return IMreCrypto
    raise AttributeError(f"module {__name__} has no attribute {name}")
