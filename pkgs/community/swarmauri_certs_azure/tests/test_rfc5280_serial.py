"""Tests for serial number generation per RFC 5280."""

from swarmauri_certs_azure.certs.AzureKeyVaultCertService import _serial_or_random


def test_serial_or_random_rfc5280() -> None:
    fixed = _serial_or_random(42)
    assert fixed == 42
    rnd = _serial_or_random(None)
    assert 0 < rnd < 2**128
