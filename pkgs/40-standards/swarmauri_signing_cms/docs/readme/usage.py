import asyncio
from swarmauri_core.crypto.types import KeyUse, ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec
from swarmauri_certs_x509 import X509CertService
from swarmauri_keyprovider_local import LocalKeyProvider


async def build_smime_identity():
    key_provider = LocalKeyProvider()
    certs = X509CertService()

    ca_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="Example CMS CA",
    )
    ca_key = await key_provider.create_key(ca_spec)
    ca_cert = await certs.create_self_signed(
        ca_key,
        {"CN": "Example CMS Root", "O": "Example Org"},
        extensions={
            "basic_constraints": {"ca": True, "path_len": 0},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
                "key_cert_sign": True,
                "crl_sign": True,
            },
        },
    )

    leaf_spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ECDSA_P256_SHA256,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        label="CMS Signer",
    )
    leaf_key = await key_provider.create_key(leaf_spec)
    csr = await certs.create_csr(
        leaf_key,
        {"CN": "cms-signer.example", "emailAddress": "signer@example.org"},
        san={"email": ["signer@example.org"]},
    )
    leaf_cert = await certs.sign_cert(
        csr,
        ca_key,
        ca_cert=ca_cert,
        extensions={
            "basic_constraints": {"ca": False},
            "key_usage": {
                "digital_signature": True,
                "content_commitment": True,
            },
            "extended_key_usage": {"oids": ["emailProtection"]},
        },
    )

    cms_key_ref = {
        "kind": "pem",
        "private_key": leaf_key.material,
        "certificate": leaf_cert,
        "extra_certificates": [ca_cert],
    }
    trust_chain = [ca_cert]
    return cms_key_ref, trust_chain


cms_key_ref, trust_chain = asyncio.run(build_smime_identity())
