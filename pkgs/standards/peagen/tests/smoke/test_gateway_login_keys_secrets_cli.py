import json
import subprocess

import pytest

GATEWAY = "https://gw.peagen.com/rpc"


@pytest.mark.i9n
def test_login_and_fetch_keys(tmp_path):
    key_dir = tmp_path / "keys"
    subprocess.run(
        [
            "peagen",
            "login",
            "--gateway-url",
            GATEWAY,
            "--key-dir",
            str(key_dir),
            "--passphrase",
            "testpass",
        ],
        check=True,
        timeout=60,
    )

    result = subprocess.run(
        ["peagen", "keys", "fetch-server", "--gateway-url", GATEWAY],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    data = json.loads(result.stdout)
    assert isinstance(data, dict)


@pytest.mark.i9n
def test_secret_roundtrip(tmp_path):
    subprocess.run(
        [
            "peagen",
            "remote",
            "secrets",
            "add",
            "smoke-secret",
            "value",
            "--gateway-url",
            GATEWAY,
        ],
        check=True,
        timeout=60,
    )

    subprocess.run(
        [
            "peagen",
            "remote",
            "secrets",
            "remove",
            "smoke-secret",
            "--gateway-url",
            GATEWAY,
        ],
        check=True,
        timeout=60,
    )
