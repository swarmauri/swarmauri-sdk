from pathlib import Path
import pytest

from peagen.core.patch_core import apply_patch


@pytest.mark.unit
def test_apply_patch_json_merge(tmp_path: Path) -> None:
    base_path = tmp_path / "base.yaml"
    patch_path = tmp_path / "patch.yaml"
    base_path.write_text("a: 1\nb:\n  c: 2\n", encoding="utf-8")
    patch_path.write_text("b:\n  d: 3\n", encoding="utf-8")
    out = apply_patch(base_path.read_bytes(), patch_path, "json-merge")
    assert b"d: 3" in out


@pytest.mark.unit
def test_apply_patch_git(tmp_path: Path) -> None:
    base = tmp_path / "file.txt"
    base.write_text("hello\n")
    patch = tmp_path / "p.patch"
    patch.write_text("--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-hello\n+goodbye\n")

    out = apply_patch(base.read_bytes(), patch, "git")
    assert out.decode().strip() == "goodbye"


@pytest.mark.unit
def test_apply_patch_unknown(tmp_path: Path) -> None:
    base = tmp_path / "f.txt"
    patch = tmp_path / "p.patch"
    base.write_text("x")
    patch.write_text("x")
    with pytest.raises(ValueError):
        apply_patch(base.read_bytes(), patch, "unknown")
