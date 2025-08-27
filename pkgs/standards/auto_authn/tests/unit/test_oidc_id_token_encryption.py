import pytest

import auto_authn.oidc_discovery as oidc_discovery
from auto_authn.oidc_id_token import mint_id_token, verify_id_token
from auto_authn.runtime_cfg import settings


@pytest.mark.unit
def test_id_token_encryption_and_metadata(monkeypatch):
    monkeypatch.setattr(settings, "enable_id_token_encryption", True)
    monkeypatch.setattr(settings, "id_token_encryption_key", "0" * 32)
    oidc_discovery.refresh_discovery_cache()
    token = mint_id_token(
        sub="user",
        aud="client",
        nonce="n",
        issuer="https://issuer",
    )
    assert token.count(".") == 4
    claims = verify_id_token(token, issuer="https://issuer", audience="client")
    assert claims["sub"] == "user"
    config = oidc_discovery._build_openid_config()  # noqa: SLF001
    assert config["id_token_encryption_alg_values_supported"] == ["dir"]
    assert config["id_token_encryption_enc_values_supported"] == ["A256GCM"]
