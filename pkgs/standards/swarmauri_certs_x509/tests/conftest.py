import sys
import types

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)

# Minimal placeholder to ensure plugin import
providers_mod = types.ModuleType("swarmauri_providers")
certs_mod = types.ModuleType("swarmauri_providers.certs")

sys.modules.setdefault("swarmauri_providers", providers_mod)
sys.modules.setdefault("swarmauri_providers.certs", certs_mod)


@pytest.fixture
def make_key_ref():
    def _make() -> KeyRef:
        sk = ed25519.Ed25519PrivateKey.generate()
        pem = sk.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        return KeyRef(
            kid="k1",
            version=1,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            material=pem,
            public=None,
            tags={},
        )

    return _make
