"""Tests for RFC 5280 certificate chain validation."""

import asyncio
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
import pytest

from swarmauri_signing_casigner import CASigner
from swarmauri_core.crypto.types import KeyRef, KeyType, KeyUse, ExportPolicy


@pytest.mark.test
def test_verify_chain_rfc5280():
    async def _run() -> bool:
        signer = CASigner()
        ca_sk = Ed25519PrivateKey.generate()
        ca_ref = KeyRef(
            kid="ca",
            version=1,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            tags={"crypto_obj": ca_sk},
        )
        root = signer.issue_self_signed(ca_ref, {"CN": "Root"}, is_ca=True)
        leaf_sk = Ed25519PrivateKey.generate()
        leaf_ref = KeyRef(
            kid="leaf",
            version=1,
            type=KeyType.ED25519,
            uses=(KeyUse.SIGN,),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            tags={"crypto_obj": leaf_sk},
        )
        csr = signer.create_csr({"CN": "Leaf"}, leaf_ref)
        cert = signer.sign_csr(csr, ca_ref, root, is_ca=False)
        return signer.verify_chain(cert, roots_pems=[root])

    assert asyncio.run(_run())
