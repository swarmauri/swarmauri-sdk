import random; random.seed(0xA11A)
import subprocess
from pathlib import Path
import pytest

from peagen._gitops import _clone_swarmauri_repo


@pytest.mark.unit
def test_clone(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(subprocess, "check_call", lambda cmd: calls.append(cmd))
    monkeypatch.setattr("tempfile.mkdtemp", lambda prefix: str(tmp_path / "repo"))
    p = _clone_swarmauri_repo(use_dev_branch=True)
    assert Path(p).exists()
    assert "mono/dev" in calls[0]

