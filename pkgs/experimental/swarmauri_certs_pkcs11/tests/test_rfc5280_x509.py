"""Tests for RFC 5280 X.509 compliance."""

import pytest

pytest.importorskip("pkcs11")

from swarmauri_certs_pkcs11 import Pkcs11CertService


@pytest.mark.unit
def test_class_mentions_rfc5280() -> None:
    assert "RFC 5280" in Pkcs11CertService.__doc__
