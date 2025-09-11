import pytest

from swarmauri_certs_acme import AcmeCertService


@pytest.mark.unit
def test_acmecertservice_mentions_rfc8555() -> None:
    assert "RFC 8555" in AcmeCertService.__doc__
