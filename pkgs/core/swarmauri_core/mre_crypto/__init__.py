"""Multi-Recipient Encryption interfaces and types."""

from .types import MultiRecipientEnvelope, RecipientInfo, RecipientId, MreMode

__all__ = [
    "IMreCrypto",
    "MultiRecipientEnvelope",
    "RecipientInfo",
    "RecipientId",
    "MreMode",
]


def __getattr__(name: str):  # pragma: no cover - thin wrapper
    if name == "IMreCrypto":
        from .IMreCrypto import IMreCrypto as _IMreCrypto

        return _IMreCrypto
    raise AttributeError(name)
