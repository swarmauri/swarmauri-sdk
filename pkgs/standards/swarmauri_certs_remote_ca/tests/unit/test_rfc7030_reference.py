import pytest

from swarmauri_certs_remote_ca import RemoteCaCertService


@pytest.mark.unit
def test_mentions_rfc7030() -> None:
    assert "RFC 7030" in RemoteCaCertService.__doc__
