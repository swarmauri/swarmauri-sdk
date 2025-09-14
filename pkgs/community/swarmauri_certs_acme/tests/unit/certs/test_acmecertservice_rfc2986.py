import pytest

from swarmauri_certs_acme import AcmeCertService


@pytest.mark.unit
def test_acmecertservice_mentions_rfc2986() -> None:
    assert "RFC 2986" in AcmeCertService.__doc__
