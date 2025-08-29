import base64
import types
from typing import Any

import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

from swarmauri_keyprovider_vaulttransit import VaultTransitKeyProvider


class FakeTransit:
    def __init__(self, pem: bytes):
        self._pem = pem

    def read_key(self, name: str, mount_point: str) -> dict:
        return {
            "data": {
                "latest_version": 1,
                "keys": {"1": {"public_key": self._pem.decode()}},
            }
        }

    def list_keys(self, mount_point: str) -> dict:
        return {"data": {"keys": ["test"]}}

    def export_key(
        self, name: str, key_type: str, version: str | None, mount_point: str
    ) -> dict:
        return {"data": {"keys": {"1": self._pem.decode()}}}

    def create_key(self, **kwargs: Any) -> None:  # pragma: no cover - not used
        pass

    def rotate_key(self, **kwargs: Any) -> None:  # pragma: no cover
        pass

    def delete_key(self, **kwargs: Any) -> None:  # pragma: no cover
        pass

    def destroy_key(self, **kwargs: Any) -> None:  # pragma: no cover
        pass


class FakeSys:
    def generate_random_bytes(self, n_bytes: int) -> dict:
        data = base64.b64encode(b"\x00" * n_bytes).decode()
        return {"data": {"random_bytes": data}}


class FakeClient:
    def __init__(self, pem: bytes):
        self.secrets = types.SimpleNamespace(transit=FakeTransit(pem))
        self.sys = FakeSys()

    def is_authenticated(self) -> bool:
        return True


@pytest.fixture()
def provider() -> VaultTransitKeyProvider:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.public_key().public_bytes(
        serialization.Encoding.PEM,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    client = FakeClient(pem)
    return VaultTransitKeyProvider(url="http://vault", token="t", client=client)
