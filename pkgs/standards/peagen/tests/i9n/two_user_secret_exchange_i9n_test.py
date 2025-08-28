import os
import subprocess
import pathlib
import shutil

import httpx
import pytest

WORKER_LIST = "Worker.list"

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway responds with a valid worker list."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
        if response.status_code != 200:
            return False
        data = response.json()
    except Exception:
        return False
    return "result" in data


@pytest.mark.i9n
@pytest.mark.skip(reason="remote secrets workflow deprecated")
def test_two_user_secret_exchange(tmp_path: pathlib.Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    user1_home = tmp_path / "user1"
    user2_home = tmp_path / "user2"
    user1_key_dir = user1_home / "keys"
    user2_key_dir = user2_home / "keys"

    # create expected locations for the CLI
    (user1_home / ".peagen").mkdir(parents=True, exist_ok=True)
    (user2_home / ".peagen").mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [
            "peagen",
            "local",
            "deploykey",
            "create",
            "--key-dir",
            str(user1_key_dir),
            "--passphrase",
            "",
        ],
        check=True,
        timeout=60,
    )
    # move key pair to HOME/.peagen/keys for CLI use
    shutil.copytree(user1_key_dir, user1_home / ".peagen" / "keys")
    subprocess.run(
        [
            "peagen",
            "local",
            "deploykey",
            "create",
            "--key-dir",
            str(user2_key_dir),
            "--passphrase",
            "",
        ],
        check=True,
        timeout=60,
    )
    shutil.copytree(user2_key_dir, user2_home / ".peagen" / "keys")

    env1 = os.environ.copy()
    env1["HOME"] = str(user1_home)
    env2 = os.environ.copy()
    env2["HOME"] = str(user2_home)

    pub_path = user1_key_dir / "ssh-public"

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "add",
            "shared-secret",
            "the_secret",
            "--recipient",
            str(pub_path),
        ],
        env=env2,
        check=True,
        timeout=60,
    )

    res2 = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "get",
            "shared-secret",
        ],
        env=env2,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    assert "the_secret" in res2.stdout

    res1 = subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "get",
            "shared-secret",
        ],
        env=env1,
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    assert "the_secret" in res1.stdout

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "remove",
            "shared-secret",
        ],
        env=env2,
        check=True,
        timeout=60,
    )
