import json
import subprocess
from pathlib import Path

import pytest

SPEC_PATH = (
    Path(__file__).resolve().parents[2]
    / "tests"
    / "examples"
    / "simple_evolve_demo"
    / "evolve_remote_spec.yaml"
)


@pytest.mark.infra
def test_remote_evolve_gateway(tmp_path):
    """Run the simple evolve demo against a local gateway."""
    cmd = [
        "peagen",
        "remote",
        "-q",
        "--gateway-url",
        "http://localhost:8000/rpc",
        "evolve",
        str(SPEC_PATH),
        "--watch",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=60)
    last_line = result.stdout.strip().splitlines()[-1]
    data = json.loads(last_line)
    assert data["status"] == "success"
