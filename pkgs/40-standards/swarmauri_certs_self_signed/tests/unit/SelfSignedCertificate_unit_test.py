import json
import ipaddress

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509

from swarmauri_certs_self_signed import SelfSignedCertificate
from swarmauri_core.certs.ICertService import (
    BasicConstraintsSpec,
    CertExtensionSpec,
    KeyUsageSpec,
    SubjectSpec,
)
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse


@pytest.fixture
def self_signed_cert():
    return SelfSignedCertificate()


def _rsa_keyref(kid: str = "k1") -> KeyRef:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return KeyRef(
        kid=kid,
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=pem,
    )


@pytest.mark.unit
def test_ubc_resource(self_signed_cert):
    assert self_signed_cert.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(self_signed_cert):
    assert self_signed_cert.type == "SelfSignedCertificate"


@pytest.mark.unit
def test_initialization(self_signed_cert):
    assert isinstance(self_signed_cert.id, str)
    assert self_signed_cert.id


@pytest.mark.unit
def test_serialization(self_signed_cert):
    serialized = self_signed_cert.model_dump_json()
    data = json.loads(serialized)

    restored = SelfSignedCertificate.model_construct(**data)

    assert restored.id == self_signed_cert.id
    assert restored.resource == self_signed_cert.resource
    assert restored.type == self_signed_cert.type


@pytest.mark.test
@pytest.mark.unit
def test_issue_basic():
    keyref = _rsa_keyref()
    cert_bytes = SelfSignedCertificate().issue(keyref)
    cert = x509.load_pem_x509_certificate(cert_bytes)
    assert cert.subject == cert.issuer
    assert (
        cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)[
            0
        ].value
        == "localhost"
    )


@pytest.mark.unit
def test_tls_server_supports_ip_subject_alt_names() -> None:
    keyref = _rsa_keyref("ip-san")
    cert_bytes = SelfSignedCertificate.tls_server(
        "localhost",
        dns_names=["localhost"],
        ip_addrs=["127.0.0.1", "::1"],
    ).issue(keyref)

    cert = x509.load_pem_x509_certificate(cert_bytes)
    san = cert.extensions.get_extension_for_class(
        x509.SubjectAlternativeName
    ).value

    assert ipaddress.ip_address("127.0.0.1") in san.get_values_for_type(
        x509.IPAddress
    )
    assert ipaddress.ip_address("::1") in san.get_values_for_type(
        x509.IPAddress
    )


@pytest.mark.unit
def test_issue_supports_ip_name_constraints() -> None:
    keyref = _rsa_keyref("ip-name-constraints")
    extensions: CertExtensionSpec = CertExtensionSpec(
        basic_constraints=BasicConstraintsSpec(ca=True, path_len=0),
        key_usage=KeyUsageSpec(
            digital_signature=True,
            key_cert_sign=True,
            crl_sign=True,
        ),
        name_constraints={
            "permitted_ip": ["10.0.0.0/24"],
            "excluded_ip": ["192.168.0.0/24"],
        },
    )

    cert_bytes = SelfSignedCertificate(
        subject=SubjectSpec(CN="ip-ca.local"),
        extensions=extensions,
    ).issue(keyref)

    cert = x509.load_pem_x509_certificate(cert_bytes)
    constraints = cert.extensions.get_extension_for_class(
        x509.NameConstraints
    ).value

    assert [name.value for name in constraints.permitted_subtrees] == [
        ipaddress.ip_network("10.0.0.0/24")
    ]
    assert [name.value for name in constraints.excluded_subtrees] == [
        ipaddress.ip_network("192.168.0.0/24")
    ]
