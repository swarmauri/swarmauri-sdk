from swarmauri_certs_crlverifyservice import CrlVerifyService


def test_crlverifyservice_mentions_rfc5280() -> None:
    assert "RFC 5280" in CrlVerifyService.__doc__
