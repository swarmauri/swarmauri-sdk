import asyncio
import json

import pytest

from swarmauri_certs_x509 import X509CertService


@pytest.fixture
def x509_cert_service():
    return X509CertService()


@pytest.mark.unit
def test_ubc_resource(x509_cert_service):
    assert x509_cert_service.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(x509_cert_service):
    assert x509_cert_service.type == "X509CertService"


@pytest.mark.unit
def test_initialization(x509_cert_service):
    assert isinstance(x509_cert_service.id, str)
    assert x509_cert_service.id


@pytest.mark.unit
def test_serialization(x509_cert_service):
    serialized = x509_cert_service.model_dump_json()
    data = json.loads(serialized)

    restored = X509CertService.model_construct(**data)

    assert restored.id == x509_cert_service.id
    assert restored.resource == x509_cert_service.resource
    assert restored.type == x509_cert_service.type


async def _mint_self_signed(make_key_ref) -> bytes:
    svc = X509CertService()
    key = make_key_ref()
    cert = await svc.create_self_signed(key, {"CN": "unit"})
    return cert


def test_create_self_signed_unit(make_key_ref) -> None:
    cert = asyncio.run(_mint_self_signed(make_key_ref))
    assert b"BEGIN CERTIFICATE" in cert
