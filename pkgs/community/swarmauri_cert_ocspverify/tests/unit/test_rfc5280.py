import pytest

from swarmauri_cert_ocspverify import OcspVerifyService


@pytest.mark.unit
def test_ocspverify_mentions_rfc5280() -> None:
    assert "RFC 5280" in OcspVerifyService.__doc__
