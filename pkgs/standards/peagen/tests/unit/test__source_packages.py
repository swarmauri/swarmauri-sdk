import random; random.seed(0xA11A)
import subprocess
from pathlib import Path
import pytest

from peagen._source_packages import (
    _dir_checksum,
    _materialise_source_pkg,
    materialise_packages,
)


@pytest.mark.unit
def test_dir_checksum(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("x")
    h = _dir_checksum(tmp_path)
    assert len(h) == 64


@pytest.mark.unit
def test_materialise_local(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "f.txt").write_text("hi")
    ws = tmp_path / "ws"
    spec = {"type": "local", "path": str(src), "dest": "d"}
    dest = _materialise_source_pkg(spec, ws)
    assert (dest / "f.txt").exists()


@pytest.mark.unit
def test_materialise_packages(monkeypatch, tmp_path):
    pkg = tmp_path / "src"
    pkg.mkdir()
    (pkg / "f.txt").write_text("hi")
    spec = {"type": "local", "path": str(pkg), "dest": "d"}
    ws = tmp_path / "ws"
    res = materialise_packages([spec], ws)
    assert (ws / "d" / "f.txt").exists()
    lock = ws / "source_packages.lock"
    assert lock.exists()
