import os
import subprocess
from pathlib import Path

import httpx
import pytest

GATEWAY = os.environ.get("PEAGEN_TEST_GATEWAY", "https://gw.peagen.com/rpc")


def _gateway_available(url: str) -> bool:
    """Return ``True`` if the gateway URL responds successfully."""
    try:
        response = httpx.get(url, timeout=5)
    except Exception:
        return False
    return response.status_code < 500


@pytest.mark.i9n
def test_remote_doe_gen(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    spec = Path("pkgs/standards/peagen/tests/examples/locking_demo/doe_spec.yaml")
    template = Path(
        "pkgs/standards/peagen/tests/examples/locking_demo/template_project.yaml"
    )
    output = tmp_path / "payloads.yaml"

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "doe",
            "gen",
            str(spec),
            str(template),
            "--output",
            str(output),
        ],
        check=True,
        timeout=60,
    )

    assert output.exists()


@pytest.mark.i9n
def test_remote_doe_process(tmp_path: Path) -> None:
    if not _gateway_available(GATEWAY):
        pytest.skip("gateway not reachable")

    spec = Path("pkgs/standards/peagen/tests/examples/locking_demo/doe_spec.yaml")
    template = Path(
        "pkgs/standards/peagen/tests/examples/locking_demo/template_project.yaml"
    )
    output = tmp_path / "payloads.yaml"

    subprocess.run(
        [
            "peagen",
            "remote",
            "--gateway-url",
            GATEWAY,
            "doe",
            "process",
            str(spec),
            str(template),
            "--output",
            str(output),
            "--watch",
            "--interval",
            "2",
        ],
        check=True,
        timeout=180,
    )

    assert output.exists()
