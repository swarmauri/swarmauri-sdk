"""Exercise the Windows tool entry point with real directory handles."""

import os
import subprocess

import pytest

from swarmauri_tool_listfiles import ListFilesTool

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

    tool = ListFilesTool(allowed_roots=[str(allowed)])
    assert tool(str(allowed))["entries"] == [{"name": "jump", "is_dir": False}]
    assert "reparse" in tool(str(junction))["error"]


def test_windows_invalid_path_spellings_are_rejected(tmp_path):
    tool = ListFilesTool(allowed_roots=[str(tmp_path)])
    (tmp_path / "ordinary.txt").write_text("safe", encoding="utf-8")
    for path in (
        tmp_path / "ordinary.txt:stream",
        tmp_path / "ambiguous.",
        tmp_path / "NUL",
        tmp_path / "nul.txt",
        tmp_path / "COM¹.log",
        tmp_path / "LPT2" / "child",
    ):
        assert "Invalid Windows path component" in tool(str(path))["error"]


def test_held_directory_cannot_be_replaced_during_operation(
    tmp_path, monkeypatch
):
    from swarmauri_tool_listfiles import _windows_fs

    allowed = tmp_path / "allowed"
    allowed.mkdir()
    tool = ListFilesTool(allowed_roots=[str(allowed)])
    original = _windows_fs._open_child
    moved = tmp_path / "moved"
    checked = False

    def check(parent, name, *, directory, create=False, **kwargs):
        nonlocal checked
        if name == "child":
            with pytest.raises(OSError):
                allowed.rename(moved)
            checked = True
        return original(
            parent, name, directory=directory, create=create, **kwargs
        )

    monkeypatch.setattr(_windows_fs, "_open_child", check)
    (allowed / "child").mkdir()
    (allowed / "child" / "input.txt").touch()
    assert tool(str(allowed / "child"))["entries"] == [
        {"name": "input.txt", "is_dir": False}
    ]
    assert checked
    # Renaming succeeds once the tool has released every handle.
    allowed.rename(moved)
    assert (moved / "child" / "input.txt").exists()


def test_windows_scan_continues_across_native_buffers(tmp_path):
    names = {f"{i:04d}-é-🧪-{'x' * 100}.txt" for i in range(350)}
    for name in names:
        (tmp_path / name).touch()
    tool = ListFilesTool(allowed_roots=[str(tmp_path)])
    assert {entry["name"] for entry in tool(str(tmp_path))["entries"]} == names


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
        tool = ListFilesTool(allowed_roots=[str(leaf)])
        assert tool(str(leaf))["entries"] == [
            {"name": "file.txt", "is_dir": False}
        ]
    finally:
        subprocess.run(
            ["icacls", str(ancestor), "/remove:d", principal],
            check=True,
            capture_output=True,
        )


def test_scan_omits_preexisting_dos_alias(tmp_path):
    reserved = "\\\\?\\" + str(tmp_path / "NUL.txt")
    with open(reserved, "x", encoding="utf-8"):
        pass
    try:
        tool = ListFilesTool(allowed_roots=[str(tmp_path)])
        assert tool(str(tmp_path))["entries"] == []
    finally:
        os.unlink(reserved)
