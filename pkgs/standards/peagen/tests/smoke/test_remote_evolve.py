import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")

SPEC_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "simple_evolve_demo"
    / "evolve_remote_spec.yaml"
)


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway URL responds successfully."""
    try:
        resp = httpx.get(url, timeout=5)
    except Exception:
        return False
    return resp.status_code < 500


@pytest.mark.i9n
def test_remote_evolve(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    cmd = [
        "peagen",
        "remote",
        "-q",
        "--gateway-url",
        GATEWAY,
        "evolve",
        str(SPEC_PATH),
        "--watch",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
    last_line = result.stdout.strip().splitlines()[-1]
    data = json.loads(last_line)
    assert data["status"] == "success"
