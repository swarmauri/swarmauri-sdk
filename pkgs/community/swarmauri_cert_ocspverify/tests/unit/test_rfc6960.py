import pytest

from swarmauri_cert_ocspverify import OcspVerifyService


@pytest.mark.unit
def test_ocspverify_mentions_rfc6960() -> None:
    assert "RFC 6960" in OcspVerifyService.__doc__
