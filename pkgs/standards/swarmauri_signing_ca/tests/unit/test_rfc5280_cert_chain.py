"""RFC 5280 certificate chain tests."""

from cryptography.hazmat.primitives.asymmetric import ed25519

from swarmauri_signing_ca import CASigner


def test_rfc5280_chain_verification():
    signer = CASigner()
    root_key = {"kind": "cryptography_obj", "obj": ed25519.Ed25519PrivateKey.generate()}
    root_cert = signer.issue_self_signed(root_key, {"CN": "root"})
    leaf_key = {"kind": "cryptography_obj", "obj": ed25519.Ed25519PrivateKey.generate()}
    csr = signer.create_csr({"CN": "leaf"}, leaf_key)
    leaf_cert = signer.sign_csr(csr, root_key, root_cert)
    assert signer.verify_chain(leaf_cert, roots_pems=[root_cert])
