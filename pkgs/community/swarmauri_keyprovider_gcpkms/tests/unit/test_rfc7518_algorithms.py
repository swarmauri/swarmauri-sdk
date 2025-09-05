import pytest
from cryptography.hazmat.primitives import hashes

from swarmauri_keyprovider_gcpkms.GcpKmsKeyProvider import _hash_from_algo


@pytest.mark.unit
def test_rfc7518_hash_sha256():
    assert isinstance(_hash_from_algo("RSA_SIGN_PKCS1_2048_SHA256"), hashes.SHA256)


@pytest.mark.unit
def test_rfc7518_hash_default():
    assert isinstance(_hash_from_algo("RSA_SIGN_PKCS1_2048_SHA1"), hashes.SHA256)
