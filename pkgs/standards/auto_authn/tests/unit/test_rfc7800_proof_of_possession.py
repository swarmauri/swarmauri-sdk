"""Tests for Proof-of-Possession semantics (RFC 7800).

These tests ensure that ``cnf`` claim helpers correctly embed and validate the
JWK thumbprint as described in RFC 7800 and that the behaviour can be toggled
via ``runtime_cfg.Settings.enable_rfc7800``.
"""

import pytest

from auto_authn.v2.rfc7638 import jwk_thumbprint
from auto_authn.v2.rfc7800 import add_cnf_claim, verify_proof_of_possession

JWK = {
    "kty": "oct",
    "k": "AyM1SysPpbyDfgZld3umsuRM1g6N6zI5O0F_S0Q-cek",
}


@pytest.mark.unit
def test_cnf_claim_round_trip():
    """``add_cnf_claim`` adds a matching ``cnf`` structure."""
    payload = {"sub": "alice"}
    augmented = add_cnf_claim(payload, JWK)
    thumb = jwk_thumbprint(JWK)
    assert augmented["cnf"]["jkt"] == thumb
    assert verify_proof_of_possession(augmented, JWK, enabled=True)
    assert not verify_proof_of_possession({"sub": "alice"}, JWK, enabled=True)


@pytest.mark.unit
def test_feature_toggle(monkeypatch):
    """When disabled, verification always passes."""
    payload = {"sub": "bob"}
    assert verify_proof_of_possession(payload, JWK, enabled=False) is True
