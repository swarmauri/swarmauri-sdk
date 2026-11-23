import pytest

from swarmauri_certs_composite import CompositeCertService


@pytest.mark.unit
def test_compositecertservice_mentions_rfc2986() -> None:
    assert "RFC 2986" in CompositeCertService.__doc__
