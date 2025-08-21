import pytest

from swarmauri_certs_remote_ca import RemoteCaCertService


@pytest.mark.unit
def test_mentions_rfc5280() -> None:
    assert "RFC 5280" in RemoteCaCertService.__doc__
