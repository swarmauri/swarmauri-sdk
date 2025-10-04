from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any, Dict

# Optional cryptography for signing compatibility
try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
except Exception:  # pragma: no cover
    hashes = None
    Prehashed = None

@dataclass
class KmsClientAdapter:
    """A minimal in-memory KMS-like adapter interface.

    This is NOT a secure KMS. It exists so the rest of the system has a working
    implementation in dev environments. Production should provide a real client.
    """
    keys: Dict[str, Any]

    async def sign(self, *, key_id: str, message: bytes, algorithm: str = "SHA256") -> bytes:
        key = self.keys.get(key_id)
        if key is None:
            raise KeyError(f"unknown key_id: {key_id}")
        if hasattr(key, "sign"):
            if hashes is None:
                # Best-effort raw sign
                return key.sign(message)
            # Choose hash algorithm
            algo = getattr(hashes, algorithm, None) or hashes.SHA256
            h = algo()
            try:
                return key.sign(message, Prehashed(h))
            except Exception:
                # Fallback to direct hash if Prehashed not supported
                from cryptography.hazmat.primitives.asymmetric import padding
                return key.sign(message, padding.PKCS1v15(), h)
        raise TypeError("provided key does not support .sign()")

def from_config(config: dict) -> Optional[KmsClientAdapter]:
    # For dev: allow wiring a preloaded key dict via runtime; default is None.
    return None
