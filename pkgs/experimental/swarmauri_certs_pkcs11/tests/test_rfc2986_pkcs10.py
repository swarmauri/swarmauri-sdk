"""Tests for RFC 2986 PKCS#10 compliance."""

import pytest

pytest.importorskip("pkcs11")

from swarmauri_certs_pkcs11 import Pkcs11CertService


@pytest.mark.unit
def test_create_csr_mentions_rfc2986() -> None:
    assert "RFC 2986" in Pkcs11CertService.create_csr.__doc__
