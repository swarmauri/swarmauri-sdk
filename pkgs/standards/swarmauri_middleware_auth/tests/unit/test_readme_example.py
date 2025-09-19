"""Execute the README usage example to guard against regressions."""

from __future__ import annotations

import asyncio
import re
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_signing_jws import JwsSignerVerifier


@pytest.mark.example
def test_readme_usage_example_executes() -> None:
    """Run the README usage example and confirm it protects a route."""

    readme_path = Path(__file__).resolve().parents[2] / "README.md"
    readme_text = readme_path.read_text(encoding="utf-8")

    match = re.search(r"## Usage.*?```python\n(?P<code>.*?)```", readme_text, re.S)
    assert match is not None, "Usage example not found in README.md"

    namespace: dict[str, object] = {"__name__": "__test__"}
    exec(match.group("code"), namespace)  # noqa: S102 - executing documented example

    app = namespace.get("app")
    auth_middleware = namespace.get("auth_middleware")
    secret_key = namespace.get("SECRET_KEY")
    issuer = namespace.get("ISSUER")
    audience = namespace.get("AUDIENCE")

    assert app is not None, "Example did not define 'app'"
    assert auth_middleware is not None, "Example did not define 'auth_middleware'"
    assert secret_key is not None, "Example did not define 'SECRET_KEY'"
    assert issuer is not None, "Example did not define 'ISSUER'"
    assert audience is not None, "Example did not define 'AUDIENCE'"

    client = TestClient(app, raise_server_exceptions=False)  # type: ignore[arg-type]

    unauthenticated = client.get("/protected")
    assert unauthenticated.status_code == 401

    signer = JwsSignerVerifier()
    token = asyncio.run(
        signer.sign_compact(
            payload={
                "sub": "user123",
                "iat": int(time.time()),
                "exp": int(time.time()) + 60,
                "aud": audience,
                "iss": issuer,
            },
            alg=JWAAlg.HS256,
            key={"kind": "raw", "key": secret_key, "alg": "HS256"},
            typ="JWT",
        )
    )

    authenticated = client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )

    assert authenticated.status_code == 200
    assert authenticated.json() == {"subject": "user123"}
