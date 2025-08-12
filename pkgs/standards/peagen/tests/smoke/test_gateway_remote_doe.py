import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
REPO = "testproject"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


@pytest.mark.i9n
def test_remote_login(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    subprocess.run(
        ["peagen", "login", "--gateway-url", GATEWAY],
        check=True,
        timeout=60,
    )


@pytest.mark.i9n
def test_remote_keys_fetch(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

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
def test_remote_secret_roundtrip(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "add",
            "smoke-secret",
            "value",
        ],
        check=True,
        timeout=60,
    )

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "secrets",
            "remove",
            "smoke-secret",
        ],
        check=True,
        timeout=60,
    )


@pytest.mark.i9n
def test_remote_doe_process(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    root = Path(__file__).resolve().parents[2]
    spec = root / "tests" / "examples" / "gateway_demo" / "doe_spec.yaml"
    template = root / "tests" / "examples" / "gateway_demo" / "template_project.yaml"

    gateway = GATEWAY[:-4] if GATEWAY.endswith("/rpc") else GATEWAY

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            gateway,
            "doe",
            "process",
            str(spec),
            str(template),
            "--repo",
            REPO,
        ],
        check=True,
        timeout=60,
    )
