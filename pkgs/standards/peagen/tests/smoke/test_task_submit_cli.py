import json
import subprocess
import uuid
from pathlib import Path

import pytest

pytestmark = pytest.mark.smoke


def _command_available() -> bool:
    result = subprocess.run(
        ["peagen", "task", "submit", "--help"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


@pytest.mark.i9n
def test_cli_task_submit_local(tmp_path: Path) -> None:
    if not _command_available():
        pytest.skip("task submit command not available")

    result = subprocess.run(
        ["peagen", "task", "submit", "demo", "{}", "--local"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = result.stdout.splitlines()
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("{"):
            payload = json.loads(lines[idx])
            break
    else:
        pytest.fail("no JSON payload found in output")

    assert uuid.UUID(payload.get("taskId"))
