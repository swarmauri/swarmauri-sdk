import pytest

from swarmauri_core.certs import ICertService


@pytest.mark.unit
def test_create_csr_mentions_rfc2986() -> None:
    assert "RFC 2986" in ICertService.create_csr.__doc__
