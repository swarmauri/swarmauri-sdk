"""Exercise the Windows tool entry point with real directory handles."""

import os
import subprocess

import pytest

from swarmauri_tool_scrollfile import ScrollFileTool

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

    tool = ScrollFileTool(allowed_roots=[str(allowed)])
    with pytest.raises(PermissionError, match="reparse"):
        tool(str(junction / "secret.txt"))
    assert (outside / "secret.txt").read_text(encoding="utf-8") == "outside"


def test_windows_invalid_path_spellings_are_rejected(tmp_path):
    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    (tmp_path / "ordinary.txt").write_text("safe", encoding="utf-8")
    for path in (
        tmp_path / "ordinary.txt:stream",
        tmp_path / "ambiguous.",
        tmp_path / "NUL",
        tmp_path / "nul.txt",
        tmp_path / "COM¹.log",
        tmp_path / "LPT2" / "child",
    ):
        with pytest.raises(ValueError, match="Invalid Windows path component"):
            tool(str(path))


def test_held_directory_cannot_be_replaced_during_operation(
    tmp_path, monkeypatch
):
    from swarmauri_tool_scrollfile import _windows_fs

    allowed = tmp_path / "allowed"
    allowed.mkdir()
    (allowed / "input.txt").write_text("inside", encoding="utf-8")
    tool = ScrollFileTool(allowed_roots=[str(allowed)])
    original = _windows_fs._open_child
    moved = tmp_path / "moved"
    checked = False

    def check(parent, name, *, directory, create=False):
        nonlocal checked
        if name == "input.txt":
            with pytest.raises(OSError):
                allowed.rename(moved)
            checked = True
        return original(parent, name, directory=directory, create=create)

    monkeypatch.setattr(_windows_fs, "_open_child", check)
    assert tool(str(allowed / "input.txt"))["lines"][0]["content"] == "inside"
    assert checked
    # Renaming succeeds once the tool has released every handle.
    allowed.rename(moved)
    assert (moved / "input.txt").exists()


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
        tool = ScrollFileTool(allowed_roots=[str(leaf)])
        assert tool(str(leaf / "file.txt"))["lines"][0]["content"] == "ok"
    finally:
        subprocess.run(
            ["icacls", str(ancestor), "/remove:d", principal],
            check=True,
            capture_output=True,
        )
