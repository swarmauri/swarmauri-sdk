import pytest

from swarmauri_certs_acme import AcmeCertService


@pytest.mark.unit
def test_acmecertservice_mentions_rfc5280() -> None:
    assert "RFC 5280" in AcmeCertService.__doc__
