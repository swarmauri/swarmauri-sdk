import subprocess
from pathlib import Path

import os
import pytest

pytestmark = pytest.mark.smoke

gateway = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=True)


def fingerprint(pub: Path) -> str:
    out = run(["gpg", "--show-keys", "--with-colons", str(pub)]).stdout
    for line in out.splitlines():
        if line.startswith("fpr"):
            return line.split(":")[9]
    raise RuntimeError("fingerprint not found")


@pytest.mark.skip("unstable external gateway")
def test_gateway_key_and_secret_flow(tmp_path: Path) -> None:
    key_dir = tmp_path / "keys"
    run(["peagen", "keys", "create", "--key-dir", str(key_dir)])
    run(
        [
            "peagen",
            "login",
            "--key-dir",
            str(key_dir),
            "--gateway-url",
            gateway,
        ]
    )
    run(
        [
            "peagen",
            "keys",
            "upload",
            "--key-dir",
            str(key_dir),
            "--gateway-url",
            gateway,
        ]
    )
    fp = fingerprint(key_dir / "public.asc")

    run(
        [
            "peagen",
            "remote",
            "-q",
            "secrets",
            "add",
            "smoke-secret",
            "secret-value",
            "--recipient",
            str(key_dir / "public.asc"),
            "--gateway-url",
            gateway,
        ]
    )
    out = run(
        [
            "peagen",
            "remote",
            "-q",
            "secrets",
            "get",
            "smoke-secret",
            "--gateway-url",
            gateway,
        ]
    ).stdout.strip()
    assert out == "secret-value"
    run(
        [
            "peagen",
            "remote",
            "-q",
            "secrets",
            "remove",
            "smoke-secret",
            "--gateway-url",
            gateway,
        ]
    )
    run(
        [
            "peagen",
            "keys",
            "remove",
            fp,
            "--gateway-url",
            gateway,
        ]
    )
