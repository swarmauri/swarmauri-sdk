import pytest

from swarmauri_core.certs import ICertService


@pytest.mark.unit
def test_icertservice_mentions_rfc5280() -> None:
    assert "RFC 5280" in ICertService.__doc__
