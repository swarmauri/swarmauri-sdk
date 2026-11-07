"""Exercise the Windows tool entry point with real directory handles."""

import os
import subprocess

import pytest

from swarmauri_tool_createfile import CreateFileTool

pytestmark = [
    pytest.mark.unit,
    pytest.mark.skipif(
        os.name != "nt", reason="Native Windows filesystem backend"
    ),
]


def test_junctions_are_never_traversed(tmp_path):
    from _winapi import CreateJunction

    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("outside", encoding="utf-8")
    junction = allowed / "jump"
    CreateJunction(str(outside), str(junction))

    tool = CreateFileTool(allowed_roots=[str(allowed)])
    assert not tool(str(junction / "new.txt"), "new")["created"]
    assert not (outside / "new.txt").exists()
    assert not tool(str(junction / "secret.txt"), "replace")["created"]
    assert (outside / "secret.txt").read_text(encoding="utf-8") == "outside"


def test_windows_invalid_path_spellings_are_rejected(tmp_path):
    tool = CreateFileTool(allowed_roots=[str(tmp_path)])
    (tmp_path / "ordinary.txt").write_text("safe", encoding="utf-8")
    for path in (
        tmp_path / "ordinary.txt:stream",
        tmp_path / "ambiguous.",
        tmp_path / "NUL",
        tmp_path / "nul.txt",
        tmp_path / "COM¹.log",
        tmp_path / "LPT2" / "child",
    ):
        result = tool(str(path), "new")
        assert result["created"] is False
        assert "Invalid Windows path component" in result["error"]


def test_held_directory_cannot_be_replaced_during_operation(
    tmp_path, monkeypatch
):
    from swarmauri_tool_createfile import _windows_fs

    allowed = tmp_path / "allowed"
    parent = allowed / "nested"
    parent.mkdir(parents=True)
    tool = CreateFileTool(allowed_roots=[str(allowed)])
    original = _windows_fs._open_child
    moved = tmp_path / "moved"
    checked = False

    def check(parent_handle, name, *, directory, create=False):
        nonlocal checked
        if name == "new.txt":
            with pytest.raises(OSError):
                parent.rename(moved)
            checked = True
        return original(
            parent_handle, name, directory=directory, create=create
        )

    monkeypatch.setattr(_windows_fs, "_open_child", check)
    assert tool(str(parent / "new.txt"), "new")["created"]
    assert checked
    # Renaming succeeds once the tool has released every handle.
    parent.rename(moved)
    assert (moved / "new.txt").read_text(encoding="utf-8") == "new"


def test_traverse_only_ancestor(tmp_path):
    ancestor = tmp_path / "ancestor"
    leaf = ancestor / "leaf"
    leaf.mkdir(parents=True)
    (leaf / "file.txt").write_text("ok", encoding="utf-8")
    principal = subprocess.check_output(["whoami"], text=True).strip()
    subprocess.run(
        ["icacls", str(ancestor), "/deny", f"{principal}:(RD)"],
        check=True,
        capture_output=True,
    )
    try:
        assert (leaf / "file.txt").read_text(encoding="utf-8") == "ok"
        tool = CreateFileTool(allowed_roots=[str(leaf)])
        assert tool(str(leaf / "new.txt"), "ok")["created"]
    finally:
        subprocess.run(
            ["icacls", str(ancestor), "/remove:d", principal],
            check=True,
            capture_output=True,
        )
