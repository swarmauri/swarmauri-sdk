from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Any

# Optional imports
try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
except Exception:  # pragma: no cover
    serialization = None
    rsa = None
    ec = None

@dataclass
class KeyProvider:
    """Abstract provider for an issuer private key."""
    def private_key(self) -> Any:  # should return a cryptography key object
        raise NotImplementedError

class FileKeyProvider(KeyProvider):
    def __init__(self, path: str, password: Optional[str] = None):
        self.path = path
        self.password = password.encode("utf-8") if password else None

    def private_key(self) -> Any:
        if serialization is None:
            raise RuntimeError("cryptography not available")
        data = open(self.path, "rb").read()
        return serialization.load_pem_private_key(data, password=self.password)

class KmsKeyProvider(KeyProvider):
    """Stub KMS provider: expose as a cryptography-like adapter if available.

    NOTE: Real KMS integration would implement a sign() adapter to match the
    AsymmetricPrivateKey interface so x509 builder can call .sign().
    """
    def __init__(self, key_id: str, region: Optional[str] = None):
        self.key_id = key_id
        self.region = region

    def private_key(self) -> Any:
        raise NotImplementedError("KMS adapter not implemented in this stub")


class Pkcs11KeyProvider(KeyProvider):
    def __init__(self, slot: int, label: Optional[str] = None):
        self.slot = slot
        self.label = label

    def private_key(self) -> Any:
        raise NotImplementedError("PKCS#11 adapter not implemented in this stub")
