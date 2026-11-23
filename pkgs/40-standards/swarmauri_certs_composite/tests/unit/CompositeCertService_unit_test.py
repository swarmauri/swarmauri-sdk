import json

import pytest
from swarmauri_certs_composite import CompositeCertService
from swarmauri_core.certs.ICertService import ICertService


class DummyCertService(ICertService):
    type = "DummyCertService"

    def supports(self):
        return {
            "features": (
                "csr",
                "self_signed",
                "sign_from_csr",
                "verify",
                "parse",
            )
        }

    async def create_csr(self, *args, **kwargs):
        return b"csr"

    async def create_self_signed(self, *args, **kwargs):
        return b"self-signed"

    async def sign_cert(self, *args, **kwargs):
        return b"cert"

    async def verify_cert(self, *args, **kwargs):
        return {"status": "ok"}

    async def parse_cert(self, *args, **kwargs):
        return {"parsed": True}


@pytest.fixture
def cipher_suite():
    return CompositeCertService([DummyCertService()])


@pytest.mark.unit
def test_ubc_resource(cipher_suite):
    assert cipher_suite.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(cipher_suite):
    assert cipher_suite.type == "CompositeCertService"


@pytest.mark.unit
def test_initialization(cipher_suite):
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite):
    serialized = cipher_suite.model_dump_json()
    data = json.loads(serialized)

    restored = CompositeCertService.model_construct(**data)
    restored._providers = cipher_suite._providers

    assert restored.id == cipher_suite.id
    assert restored.resource == cipher_suite.resource
    assert restored.type == cipher_suite.type
