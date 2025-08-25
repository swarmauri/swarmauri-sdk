import pytest
from auto_authn import AutoAuthnConfig


def test_login_url_uses_custom_domain():
    config = AutoAuthnConfig(
        domain="auth.yourapp.com",
        brand_colors={"primary": "#ff0000"},
        copy="Welcome back",
        helper_text="Need help?"
    )
    assert config.login_url() == "https://auth.yourapp.com/login"
    assert config.brand_colors["primary"] == "#ff0000"
    assert config.copy == "Welcome back"
    assert config.helper_text == "Need help?"
    assert config.uses_custom_domain()


def test_rejects_third_party_domains():
    config = AutoAuthnConfig(domain="login.microsoftonline.com")
    assert not config.uses_custom_domain()
