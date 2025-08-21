import hashlib

import pytest

from asn1crypto import x509 as ax509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from swarmauri_certservice_aws_kms.AwsKmsCertService import _skid_from_pub


@pytest.mark.xfail(reason="asn1crypto missing extensions", raises=TypeError)
def test_skid_from_public(subject_key_ref):
    priv = serialization.load_pem_private_key(subject_key_ref.material, password=None)
    pub = priv.public_key()
    skid = _skid_from_pub(pub)
    spki = ax509.PublicKeyInfo.load(
        pub.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
    )
    expected = hashlib.sha1(bytes(spki["public_key"].native)).digest()
    assert skid == expected
