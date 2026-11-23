"""Keep invalid pattern diagnostics bounded and JSON serializable."""

import json
import os
import subprocess
import sys

import pytest


@pytest.mark.unit
def test_invalid_patterns_return_bounded_errors_without_hanging(tmp_path):
    script = """
import json
import sys
from swarmauri_tool_findfile import FindFileTool

tool = FindFileTool(max_return_bytes=256)
patterns = [
    ["x" * 10_000],
    {"nested": ["x" * 10_000]},
    b"invalid",
    object(),
    None,
    "x" * 10_000,
]
for pattern in patterns:
    result = tool(sys.argv[1], pattern=pattern)
    assert "error" in result
    assert result["count"] == 0
    assert result["matches"] == []
    if not isinstance(pattern, str):
        assert result["pattern"] == ""
    assert len(json.dumps(result, ensure_ascii=True).encode("utf-8")) <= 256
print(json.dumps({"checked": len(patterns)}))
"""
    # Bound the test even if the truncation loop regresses.
    completed = subprocess.run(
        [sys.executable, "-c", script, str(tmp_path)],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
        env=os.environ.copy(),
    )
    assert json.loads(completed.stdout) == {"checked": 6}
