import pytest

from swarmauri_keyprovider_aws_kms import _b64u


@pytest.mark.unit
def test_base64url_encoding_no_padding():
    data = b"\x00\x01"
    encoded = _b64u(data)
    assert "=" not in encoded
    assert encoded == "AAE"
