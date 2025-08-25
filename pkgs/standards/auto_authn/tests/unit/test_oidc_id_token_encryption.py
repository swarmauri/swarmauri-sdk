import asyncio
import base64

from auto_authn.v2.oidc_id_token import mint_id_token, verify_id_token
from auto_authn.v2.runtime_cfg import settings
from auto_authn.v2.rfc8414 import openid_configuration, refresh_discovery_cache


# Mark as unit test according to existing pattern


def test_encrypted_id_token(monkeypatch):
    key = base64.urlsafe_b64encode(b"0" * 32).rstrip(b"=").decode()
    monkeypatch.setattr(settings, "id_token_jwe_key", key)
    refresh_discovery_cache()
    token = mint_id_token(
        sub="alice",
        aud="client",
        nonce="n",
        issuer="https://issuer",
    )
    assert token.count(".") == 4
    claims = verify_id_token(token, issuer="https://issuer", audience="client")
    assert claims["sub"] == "alice"
    cfg = asyncio.run(openid_configuration())
    assert cfg["id_token_encryption_alg_values_supported"] == ["dir"]
    assert cfg["id_token_encryption_enc_values_supported"] == ["A256GCM"]
