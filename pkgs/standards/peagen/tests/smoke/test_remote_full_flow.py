import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")
BASE = Path(__file__).resolve().parents[2] / "tests" / "examples"
DOE_SPEC = BASE / "gateway_demo" / "doe_spec.yaml"
DOE_TEMPLATE = BASE / "gateway_demo" / "template_project.yaml"
EVOLVE_SPEC = BASE / "simple_evolve_demo" / "evolve_remote_spec.yaml"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": "Worker.list", "params": {}, "id": 0}
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
            "--dry-run",
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
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )
    last_line = result.stdout.strip().splitlines()[-1]
    data = json.loads(last_line)
    assert data["status"] == "success"

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
