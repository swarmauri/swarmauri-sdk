"""Tests for RFC 5280 certificate parsing."""

import pytest

from swarmauri_cert_cfssl.CfsslCertService import CfsslCertService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_cert_fields(cert_pem: bytes) -> None:
    """Parse certificate and verify subject and issuer names per RFC 5280."""
    svc = CfsslCertService(base_url="https://cfssl.example")
    info = await svc.parse_cert(cert_pem)
    assert info["subject"]["CN"] == "test.example"
    assert info["issuer"]["CN"] == "test.example"
    assert info["basic_constraints"]["ca"] is True
