import json
import subprocess
import uuid

import pytest

pytestmark = pytest.mark.smoke


def test_cli_task_submit_returns_id(tmp_path):
    """peagen task submit should output a valid taskId using local queue."""
    result = subprocess.run(
        ["peagen", "task", "submit", "--queue", "in_memory", "--payload", "{}"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    data = json.loads(result.stdout.strip().splitlines()[-1])
    assert uuid.UUID(data["taskId"])
