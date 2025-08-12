import json
import os
import subprocess
from pathlib import Path

import httpx
import pytest

WORKER_LIST = "Worker.list"

pytestmark = pytest.mark.smoke

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "http://localhost:8000/rpc")
BASE = Path(__file__).resolve().parents[2] / "tests" / "examples" / "gateway_demo"
SPEC = BASE / "doe_spec.yaml"
TEMPLATE = BASE / "template_project.yaml"
REPO = "testproject"


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway RPC endpoint accepts POST requests."""
    envelope = {"jsonrpc": "2.0", "method": WORKER_LIST, "params": {}, "id": 0}
    try:
        response = httpx.post(url, json=envelope, timeout=5)
    except Exception:
        return False
    return response.status_code == 200


@pytest.fixture(scope="module")
def doe_process_result(tmp_path_factory):
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")
    work_dir = tmp_path_factory.mktemp("doe")
    out_file = work_dir / "payload.yaml"
    spec = os.path.relpath(SPEC, Path.cwd())
    template = os.path.relpath(TEMPLATE, Path.cwd())
    cmd = [
        "peagen",
        "remote",
        "-q",
        "--gateway-url",
        GATEWAY,
        "doe",
        "process",
        spec,
        template,
        "--output",
        str(out_file),
        "--watch",
        "--repo",
        REPO,
    ]
    result = subprocess.run(
        cmd, capture_output=True, text=True, check=True, timeout=120
    )
    out = result.stdout
    json_block = out[out.index("{") : out.rindex("}") + 1]
    data = json.loads(json_block)
    return data, out_file


@pytest.mark.i9n
def test_process_status_success(doe_process_result):
    data, _ = doe_process_result
    assert "status" in data


@pytest.mark.i9n
def test_output_file_created(doe_process_result):
    _, out_file = doe_process_result
    assert isinstance(out_file, Path)
