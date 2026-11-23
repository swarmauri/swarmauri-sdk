import importlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

PACKAGE = "swarmauri_tool_listfiles"
CLASS = "ListFilesTool"
Tool = getattr(importlib.import_module(PACKAGE + "." + CLASS), CLASS)
fs = importlib.import_module(PACKAGE + "._filesystem")
IS_FIND = CLASS == "FindFileTool"


def call(tool, path, **kwargs):
    if IS_FIND:
        return tool(str(path), kwargs.pop("pattern", "*"), **kwargs)
    return tool(str(path), **kwargs)


def items(result):
    return result["matches" if IS_FIND else "entries"]


@pytest.fixture(autouse=True)
def trusted_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_root_containment_and_no_symlinks(tmp_path, monkeypatch, fallback):
    if fallback:
        monkeypatch.setattr(fs, "_linux_openat2", lambda *args: None)
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    (allowed / "link").symlink_to(outside, target_is_directory=True)
    tool = Tool(allowed_roots=[str(allowed)])
    for path in [
        outside,
        allowed / ".." / "outside",
        allowed / "link",
        tmp_path / "allowed-prefix",
    ]:
        result = call(tool, path)
        assert "error" in result
        assert items(result) == []
    assert "error" not in call(tool, allowed)


def test_empty_roots_fail_closed(tmp_path):
    assert "error" in call(Tool(allowed_roots=[]), tmp_path)


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_symlink_in_trusted_root_fails_closed(tmp_path):
    actual = tmp_path / "actual"
    actual.mkdir()
    link = tmp_path / "alias"
    link.symlink_to(actual, target_is_directory=True)
    assert "error" in call(Tool(allowed_roots=[str(link)]), link)


@pytest.mark.parametrize(
    "path", ["", " ", "bad\x00suffix", "~__swarmauri_unknown_user__/"]
)
def test_invalid_paths_are_structured(path):
    result = call(Tool(), path)
    assert "error" in result
    assert items(result) == []


@pytest.mark.parametrize(
    "configuration",
    [
        {"max_scanned_entries": 1},
        {"max_results": 1},
        {"max_return_bytes": 1},
    ],
)
def test_limits_never_report_partial_success(tmp_path, configuration):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.txt").touch()
    result = call(Tool(**configuration), tmp_path)
    assert "limit" in result["error"]
    assert result["count"] == 0
    assert items(result) == []


def test_deadline_is_enforced(tmp_path, monkeypatch):
    (tmp_path / "a.txt").touch()
    ticks = iter([0.0, 3.0, 3.0])
    monkeypatch.setattr(
        fs, "time", SimpleNamespace(monotonic=lambda: next(ticks))
    )
    result = call(Tool(), tmp_path)
    assert "elapsed-time" in result["error"]
    assert items(result) == []


@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_root_rename_cannot_redirect_open(tmp_path, monkeypatch, fallback):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    inside = allowed / "child"
    inside.mkdir()
    (inside / "public.txt").touch()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").touch()
    original = fs._linux_openat2

    def swap(root_fd, relative, flags):
        if not allowed.is_symlink():
            allowed.rename(tmp_path / "moved")
            allowed.symlink_to(outside, target_is_directory=True)
        return None if fallback else original(root_fd, relative, flags)

    monkeypatch.setattr(fs, "_linux_openat2", swap)
    result = call(Tool(allowed_roots=[str(allowed)]), inside)
    assert "error" not in result
    assert "secret.txt" not in str(items(result))
    assert "public.txt" in str(items(result))


@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_intermediate_swap_cannot_escape(tmp_path, monkeypatch, fallback):
    inside = tmp_path / "child"
    inside.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").touch()
    original = fs._linux_openat2

    def swap(root_fd, relative, flags):
        inside.rename(tmp_path / "moved")
        inside.symlink_to(outside, target_is_directory=True)
        return None if fallback else original(root_fd, relative, flags)

    monkeypatch.setattr(fs, "_linux_openat2", swap)
    result = call(Tool(), inside)
    assert "error" in result
    assert items(result) == []


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_unsupported_platform_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "supports_dir_fd", set())
    result = call(Tool(), tmp_path)
    assert "secure directory-relative" in result["error"]
    assert items(result) == []


@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_symlink_classification_never_follows_target(tmp_path):
    directory = tmp_path / "directory"
    directory.mkdir()
    (tmp_path / "link").symlink_to(directory, target_is_directory=True)
    result = call(Tool(), tmp_path)
    if IS_FIND:
        assert items(result) == []
    else:
        link = next(
            entry for entry in items(result) if entry["name"] == "link"
        )
        assert link["is_dir"] is False


def test_result_and_limits_are_service_owned():
    names = {parameter.name for parameter in Tool().parameters}
    assert "allowed_roots" not in names
    assert "max_results" not in names


@pytest.mark.skipif(
    not Path("/proc/self/fd").is_dir(), reason="Linux FD accounting"
)
def test_errors_do_not_leak_directory_descriptors(tmp_path):
    (tmp_path / "a.txt").touch()
    before = len(os.listdir("/proc/self/fd"))
    for _ in range(20):
        assert "error" in call(Tool(max_return_bytes=1), tmp_path)
    assert len(os.listdir("/proc/self/fd")) == before


def test_huge_invalid_inputs_cannot_expand_error_output(tmp_path):
    tool = Tool(max_return_bytes=256)
    result = call(tool, str(tmp_path) + "/" + "x" * 100_000)
    assert "error" in result
    assert len(json.dumps(result, ensure_ascii=True).encode("utf-8")) <= 256
    if IS_FIND:
        result = call(tool, tmp_path, pattern="😀" * 100_000)
        assert "error" in result
        assert (
            len(json.dumps(result, ensure_ascii=True).encode("utf-8")) <= 256
        )


@pytest.mark.skipif(os.name == "nt", reason="POSIX directory rename")
def test_scan_discards_results_if_open_directory_moves(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    inner = allowed / "inner"
    inner.mkdir(parents=True)
    (inner / "ordinary.txt").touch()
    original = fs.directory_entries

    def moved(descriptor):
        yield from original(descriptor)
        inner.rename(tmp_path / "moved")

    monkeypatch.setattr(fs, "directory_entries", moved)
    tool = Tool(allowed_roots=[str(allowed)])
    result = call(tool, inner)
    assert "error" in result
    assert items(result) == []
