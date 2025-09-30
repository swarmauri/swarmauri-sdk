from swarmauri_cipher_suite_pep458 import Pep458CipherSuite


def test_supports_and_defaults():
    suite = Pep458CipherSuite()
    supports = suite.supports()

    assert set(supports["sign"]) == {"Ed25519", "RSA-PSS-SHA256"}
    assert suite.default_alg("sign") == "Ed25519"

    rsa_default = suite.default_alg("sign", for_key={"kid": "root", "kty": "RSA"})
    assert rsa_default == "RSA-PSS-SHA256"


def test_policy_contains_role_metadata():
    suite = Pep458CipherSuite()
    policy = suite.policy()

    assert policy["canonicalization"] == "tuf-json"
    assert policy["signature"]["format"] == "tuf/pep458"
    assert {role for role in policy["roles"]} == {
        "root",
        "targets",
        "snapshot",
        "timestamp",
    }


def test_normalize_outputs_descriptor():
    suite = Pep458CipherSuite()
    descriptor = suite.normalize(op="sign", params={"role": "targets", "threshold": 2})

    assert descriptor["dialect"] == "provider"
    assert descriptor["params"]["role"] == "targets"
    assert descriptor["constraints"]["threshold"] == 2
    assert (
        descriptor["mapped"]["provider"]["signer"]
        == "swarmauri_signing_pep458.Pep458Signer"
    )
