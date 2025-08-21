from __future__ import annotations

import pytest
from typing import Iterable, Mapping, Sequence, Dict, Any

from swarmauri_core.certs.ICertService import ICertService
from swarmauri_base.certs.CertServiceBase import CertServiceBase
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy
from swarmauri_cert_composite import CompositeCertService


class DummyCertService(CertServiceBase, ICertService):
    """Minimal in-memory cert service used for testing."""

    def __init__(self, name: str, features: Sequence[str]) -> None:
        super().__init__()
        self.type = name
        self._features = tuple(features)
        self.calls: list[str] = []

    def supports(self) -> Mapping[str, Iterable[str]]:
        return {"features": self._features}

    async def create_csr(self, key: KeyRef, subject, **kw) -> bytes:
        self.calls.append("create_csr")
        return f"csr-{self.type}".encode()

    async def create_self_signed(self, key: KeyRef, subject, **kw) -> bytes:
        self.calls.append("create_self_signed")
        return f"self-{self.type}".encode()

    async def sign_cert(self, csr: bytes, ca_key: KeyRef, **kw) -> bytes:
        self.calls.append("sign_cert")
        return f"cert-{self.type}".encode()

    async def verify_cert(self, cert: bytes, **kw) -> Dict[str, Any]:
        self.calls.append("verify_cert")
        return {"backend": self.type, "cert": cert}

    async def parse_cert(self, cert: bytes, **kw) -> Dict[str, Any]:
        self.calls.append("parse_cert")
        return {"backend": self.type, "cert": cert}


@pytest.fixture
def dummy_providers() -> tuple[DummyCertService, DummyCertService]:
    a = DummyCertService("A", ["csr", "self_signed", "verify", "parse"])
    b = DummyCertService("B", ["sign_from_csr"])
    return a, b


@pytest.fixture
def composite(
    dummy_providers: tuple[DummyCertService, DummyCertService],
) -> CompositeCertService:
    return CompositeCertService(list(dummy_providers))


@pytest.fixture
def sample_key() -> KeyRef:
    return KeyRef(
        kid="kid1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.NONE,
    )
