import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
BASE = Path(__file__).resolve().parents[2] / "tests" / "examples"
DOE_SPEC = BASE / "gateway_demo" / "doe_spec.yaml"
DOE_TEMPLATE = BASE / "gateway_demo" / "template_project.yaml"
EVOLVE_SPEC = BASE / "simple_evolve_demo" / "evolve_remote_spec.yaml"
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
def test_remote_full_flow(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    subprocess.run(
        ["peagen", "login", "--gateway-url", GATEWAY], check=True, timeout=60
    )

    result = subprocess.run(
        ["peagen", "keys", "fetch-server", "--gateway-url", GATEWAY],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    assert isinstance(json.loads(result.stdout), dict)

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

    gateway = GATEWAY[:-4] if GATEWAY.endswith("/rpc") else GATEWAY
    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            gateway,
            "doe",
            "process",
            str(DOE_SPEC),
            str(DOE_TEMPLATE),
            "--repo",
            REPO,
        ],
        check=True,
        timeout=60,
    )

    result = subprocess.run(
        [
            "peagen",
            "remote",
            "-q",
            "--gateway-url",
            GATEWAY,
            "evolve",
            str(EVOLVE_SPEC),
            "--watch",
            "--repo",
            REPO,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    out = result.stdout
    lines = out.splitlines()
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("{"):
            json_block = "\n".join(lines[idx:])
            break
    data = json.loads(json_block)
    assert data["status"] == "success"

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
