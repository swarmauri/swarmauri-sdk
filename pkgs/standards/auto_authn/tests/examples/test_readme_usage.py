import os
import uuid
import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.mark.example
def test_health_endpoint_in_readme():
    from auto_authn.v2.app import app

    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "alive"}


@pytest.mark.example
def test_password_grant_flow_in_readme():
    from auto_authn.v2.app import app

    client = TestClient(app)
    slug = f"tenant-{uuid.uuid4().hex[:6]}"
    client.post(
        "/tenant",
        json={"slug": slug, "name": "Example", "email": "ops@example.com"},
    )
    client.post(
        "/register",
        json={
            "tenant_slug": slug,
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecretPwd123",
        },
    )
    tokens = client.post(
        "/token",
        data={
            "grant_type": "password",
            "username": "alice",
            "password": "SecretPwd123",
        },
    ).json()
    assert "access_token" in tokens and "refresh_token" in tokens


@pytest.mark.example
def test_refresh_token_flow_in_readme():
    from auto_authn.v2.app import app

    client = TestClient(app)
    slug = f"tenant-{uuid.uuid4().hex[:6]}"
    client.post(
        "/tenant",
        json={"slug": slug, "name": "Example", "email": "ops@example.com"},
    )
    tokens = client.post(
        "/register",
        json={
            "tenant_slug": slug,
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecretPwd123",
        },
    ).json()
    refreshed = client.post(
        "/token/refresh", json={"refresh_token": tokens["refresh_token"]}
    ).json()
    assert "access_token" in refreshed


@pytest.mark.example
def test_token_revocation_flow_in_readme():
    os.environ["AUTO_AUTHN_ENABLE_RFC7009"] = "1"
    import auto_authn.v2.app as app_module

    importlib.reload(app_module)
    client = TestClient(app_module.app)
    resp = client.post("/revoke", data={"token": "deadbeef"})
    assert resp.status_code == 200 and resp.json() == {}
