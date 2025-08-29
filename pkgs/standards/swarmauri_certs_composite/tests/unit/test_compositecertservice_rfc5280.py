import pytest

from swarmauri_certs_composite import CompositeCertService


@pytest.mark.unit
def test_compositecertservice_mentions_rfc5280() -> None:
    assert "RFC 5280" in CompositeCertService.__doc__
