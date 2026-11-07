import errno
import os
import sys
from importlib import import_module
from pathlib import Path
from unittest.mock import Mock

import pytest

from swarmauri_tool_createfile.CreateFileTool import CreateFileTool as Tool
from swarmauri_tool_createfile import _paths


@pytest.fixture(autouse=True)
def trusted_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "CreateFileTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_creates_file_with_content(tmp_path):
    target = tmp_path / "note.txt"
    tool = Tool()

    result = tool(path=str(target), content="hello\n")

    assert result["created"] is True
    assert result["path"] == str(target)
    assert result["bytes_written"] == len("hello\n".encode("utf-8"))
    assert target.read_text(encoding="utf-8") == "hello\n"


@pytest.mark.unit
def test_creates_empty_file_when_content_omitted(tmp_path):
    target = tmp_path / "empty.txt"
    tool = Tool()

    result = tool(path=str(target))

    assert result["created"] is True
    assert result["bytes_written"] == 0
    assert target.read_text(encoding="utf-8") == ""


@pytest.mark.unit
def test_refuses_to_overwrite_an_existing_file(tmp_path):
    target = tmp_path / "keep.txt"
    target.write_text("original\n", encoding="utf-8")
    tool = Tool()

    result = tool(path=str(target), content="replacement\n")

    assert result["created"] is False
    assert "error" in result
    assert target.read_text(encoding="utf-8") == "original\n"
    assert "bytes_written" not in result


@pytest.mark.unit
def test_refuses_when_the_path_is_a_directory(tmp_path):
    tool = Tool()

    result = tool(path=str(tmp_path), content="x")

    assert result["created"] is False
    assert "error" in result


@pytest.mark.unit
def test_reports_a_missing_parent_directory(tmp_path):
    target = tmp_path / "missing" / "note.txt"
    tool = Tool(allowed_roots=[str(target.parent)])

    result = tool(path=str(target), content="hello\n")

    assert result["created"] is False
    assert "does not exist" in str(result["error"])
    assert not target.exists()
    assert not target.parent.exists()


@pytest.mark.unit
def test_writes_utf8_content(tmp_path):
    target = tmp_path / "accented.txt"
    content = "caf\u00e9 na\u00efve \u4f60\u597d\n"
    tool = Tool()

    result = tool(path=str(target), content=content)

    assert result["created"] is True
    assert target.read_text(encoding="utf-8") == content
    assert result["bytes_written"] == len(content.encode("utf-8"))


@pytest.mark.unit
def test_expands_a_home_relative_path(tmp_path, monkeypatch):
    # expanduser consults HOME on POSIX and USERPROFILE on Windows; patch both
    # so the test never touches the developer's real home directory.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOMEDRIVE", tmp_path.drive or "")
    monkeypatch.setenv("HOMEPATH", str(tmp_path)[len(tmp_path.drive) :])
    tool = Tool()

    result = tool(path="~/note.txt", content="hi\n")

    assert result["created"] is True
    assert result["path"] == str(tmp_path / "note.txt")
    assert (tmp_path / "note.txt").read_text(encoding="utf-8") == "hi\n"


@pytest.mark.unit
def test_refuses_a_dangling_symlink(tmp_path):
    """A dangling symlink must not be written through."""
    link = tmp_path / "link.txt"
    missing = tmp_path / "missing.txt"
    try:
        link.symlink_to(missing)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available on this platform")

    result = Tool()(path=str(link), content="hello\n")

    assert result["created"] is False
    assert not missing.exists()


@pytest.mark.unit
@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_containment_and_symlink_policy(tmp_path, monkeypatch, fallback):
    if fallback:
        monkeypatch.setattr(_paths, "_linux_openat2", lambda *args: None)
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    try:
        (allowed / "link").symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        if getattr(exc, "winerror", None) != 1314:
            raise
        pytest.skip(
            "Creating file symlinks requires Windows symlink privilege"
        )
    tool = Tool(allowed_roots=[str(allowed)])
    for target in (
        outside / "new.txt",
        allowed / ".." / "outside" / "new.txt",
        allowed / "link" / "new.txt",
        tmp_path / "allowed-prefix" / "new.txt",
    ):
        result = tool(str(target), "unwanted")
        assert result["created"] is False
    assert not (outside / "new.txt").exists()
    assert tool(str(allowed / "valid.txt"), "ok")["created"] is True


@pytest.mark.unit
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_rejects_symlink_in_allowed_root(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    alias = tmp_path / "alias"
    try:
        alias.symlink_to(real, target_is_directory=True)
    except OSError as exc:
        if getattr(exc, "winerror", None) != 1314:
            raise
        pytest.skip(
            "Creating file symlinks requires Windows symlink privilege"
        )
    result = Tool(allowed_roots=[str(alias)])(str(alias / "new.txt"))
    assert result["created"] is False
    assert not (real / "new.txt").exists()


@pytest.mark.unit
def test_empty_allowed_roots_fail_closed(tmp_path):
    result = Tool(allowed_roots=[])(str(tmp_path / "new.txt"))
    assert result["created"] is False
    assert not (tmp_path / "new.txt").exists()


@pytest.mark.unit
def test_relative_root_configuration_is_rejected(tmp_path):
    result = Tool(allowed_roots=["."])(str(tmp_path / "new.txt"))
    assert result["created"] is False


@pytest.mark.unit
def test_relative_destination_is_supported(tmp_path):
    result = Tool()("relative.txt", "hello")
    assert result["created"] is True
    assert result["path"] == str(tmp_path / "relative.txt")


@pytest.mark.unit
def test_invalid_utf8_is_rejected_before_creation(tmp_path):
    target = tmp_path / "new.txt"
    result = Tool()(str(target), "\ud800")
    assert result["created"] is False
    assert not target.exists()


@pytest.mark.unit
@pytest.mark.parametrize(
    "path", ["", " ", "bad\x00name", "~__swarmauri_unknown_user__/new.txt"]
)
def test_invalid_paths_return_structured_errors(path):
    result = Tool()(path)
    assert result["created"] is False
    assert "error" in result


@pytest.mark.unit
def test_write_failure_retains_partial_output_without_unlink(
    tmp_path, monkeypatch
):
    target = tmp_path / "new.txt"
    real_write = os.write

    def failing_write(descriptor, data):
        real_write(descriptor, b"partial")
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(os, "write", failing_write)
    result = Tool()(str(target), "hello")
    assert result["created"] is False
    assert "Partial output may remain" in result["error"]
    assert target.read_bytes() == b"partial"


@pytest.mark.unit
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_failed_write_never_deletes_replacement(tmp_path, monkeypatch):
    target = tmp_path / "new.txt"

    def replace_then_fail(descriptor, data):
        target.rename(tmp_path / "original.txt")
        target.write_text("another process owns this", encoding="utf-8")
        raise OSError(errno.ENOSPC, "write failed")

    monkeypatch.setattr(os, "write", replace_then_fail)
    result = Tool()(str(target), "hello")
    assert result["created"] is False
    assert target.read_text(encoding="utf-8") == "another process owns this"


@pytest.mark.unit
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_size_comes_from_the_open_descriptor(tmp_path, monkeypatch):
    target = tmp_path / "new.txt"
    real_fstat = os.fstat

    def replace_then_stat(descriptor):
        target.rename(tmp_path / "original.txt")
        target.write_text("a much longer replacement", encoding="utf-8")
        return real_fstat(descriptor)

    tool_module = import_module(Tool.__module__)
    monkeypatch.setattr(
        tool_module, "os", Mock(wraps=os, fstat=replace_then_stat)
    )
    result = Tool()(str(target), "hello")
    assert result["created"] is True
    assert result["bytes_written"] == 5


@pytest.mark.unit
def test_short_writes_are_completed(tmp_path, monkeypatch):
    real_write = os.write
    monkeypatch.setattr(os, "write", lambda fd, data: real_write(fd, data[:1]))
    result = Tool()("new.txt", "café\r\n")
    assert result["created"] is True
    assert (tmp_path / "new.txt").read_bytes() == "café\r\n".encode("utf-8")


@pytest.mark.unit
def test_no_progress_write_returns_error(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "write", lambda fd, data: 0)
    assert Tool()("new.txt", "hello")["created"] is False


@pytest.mark.unit
def test_fstat_failure_is_reported(tmp_path, monkeypatch):
    def failed(descriptor):
        raise OSError(errno.EIO, "stat failed")

    tool_module = import_module(Tool.__module__)
    monkeypatch.setattr(tool_module, "os", Mock(wraps=os, fstat=failed))
    result = Tool()("new.txt", "hello")
    assert result["created"] is False
    assert "stat failed" in result["error"]


@pytest.mark.unit
@pytest.mark.parametrize("fallback", [False, True])
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_directory_swap_cannot_redirect_creation(
    tmp_path, monkeypatch, fallback
):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    open_root = _paths._open_root
    if fallback:
        monkeypatch.setattr(_paths, "_linux_openat2", lambda *args: None)

    def swap_root(root, flags):
        descriptor = open_root(root, flags)
        allowed.rename(tmp_path / "original-root")
        allowed.symlink_to(outside, target_is_directory=True)
        return descriptor

    monkeypatch.setattr(_paths, "_open_root", swap_root)
    result = Tool(allowed_roots=[str(allowed)])(
        str(allowed / "new.txt"), "hello"
    )
    assert result["created"] is True
    assert not (outside / "new.txt").exists()
    assert (tmp_path / "original-root" / "new.txt").read_text() == "hello"


@pytest.mark.unit
@pytest.mark.skipif(
    os.name == "nt", reason="POSIX-specific setup or descriptor hooks"
)
def test_unsupported_platform_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "supports_dir_fd", set())
    result = Tool()(str(tmp_path / "new.txt"), "hello")
    assert result["created"] is False
    assert "secure directory-relative" in result["error"]
    assert not (tmp_path / "new.txt").exists()


@pytest.mark.unit
@pytest.mark.skipif(sys.platform != "linux", reason="Linux openat2 ABI")
def test_openat2_flags_are_beneath_and_no_symlinks(tmp_path, monkeypatch):
    captured = {}

    class FakeLibc:
        class Call:
            restype = None

            def __call__(self, number, root_fd, path, how, size):
                captured["number"] = number.value
                captured["resolve"] = how._obj.resolve
                return 123

        syscall = Call()

    monkeypatch.setattr(
        _paths.ctypes, "CDLL", lambda *args, **kwargs: FakeLibc()
    )
    monkeypatch.setattr(_paths.platform, "machine", lambda: "x86_64")
    assert _paths._linux_openat2(9, Path("new.txt"), 1) == 123
    assert captured == {"number": 437, "resolve": 0x08 | 0x04}


@pytest.mark.unit
@pytest.mark.skipif(
    sys.platform != "linux", reason="Linux syscall availability"
)
@pytest.mark.parametrize("code", [errno.ENOSYS, errno.EINVAL, errno.EPERM])
def test_openat2_unavailability_and_denials(code, monkeypatch):
    class FakeLibc:
        class Call:
            restype = None

            def __call__(self, *args):
                _paths.ctypes.set_errno(code)
                return -1

        syscall = Call()

    monkeypatch.setattr(
        _paths.ctypes, "CDLL", lambda *args, **kwargs: FakeLibc()
    )
    monkeypatch.setattr(_paths.platform, "machine", lambda: "x86_64")
    if code == errno.EPERM:
        with pytest.raises(PermissionError):
            _paths._linux_openat2(9, Path("new.txt"), 1)
    else:
        assert _paths._linux_openat2(9, Path("new.txt"), 1) is None


@pytest.mark.unit
@pytest.mark.skipif(os.name == "nt", reason="POSIX creation policy")
def test_nested_create_is_rejected_before_opening_the_root(
    tmp_path, monkeypatch
):
    root = tmp_path / "root"
    ancestor = root / "movable"
    parent = ancestor / "child"
    parent.mkdir(parents=True)
    moved = tmp_path / "moved"
    open_root = _paths._open_root

    def move_ancestor_on_open(*args):
        ancestor.rename(moved)
        return open_root(*args)

    with monkeypatch.context() as patch:
        patch.setattr(_paths, "_open_root", move_ancestor_on_open)
        result = Tool(allowed_roots=[str(root)])(
            str(parent / "new.txt"), "fixture"
        )
    assert result["created"] is False
    assert "direct child of a configured root" in result["error"]
    assert not moved.exists()
    assert not (parent / "new.txt").exists()

    tool = Tool(allowed_roots=[str(root), str(parent)])
    assert tool(str(parent / "new.txt"), "fixture")["created"]
    assert (parent / "new.txt").read_text(encoding="utf-8") == "fixture"


@pytest.mark.unit
@pytest.mark.skipif(
    sys.platform != "linux", reason="Linux openat2 root lookup"
)
def test_root_is_resolved_without_opening_a_movable_ancestor(
    tmp_path, monkeypatch
):
    ancestor = tmp_path / "ancestor"
    allowed = ancestor / "allowed"
    allowed.mkdir(parents=True)
    moved = tmp_path / "moved"
    original = os.open

    def move_after_open(name, *args, **kwargs):
        descriptor = original(name, *args, **kwargs)
        if name == ancestor.name and kwargs.get("dir_fd") is not None:
            ancestor.rename(moved)
        return descriptor

    monkeypatch.setattr(os, "open", move_after_open)
    monkeypatch.setattr(
        os, "supports_dir_fd", os.supports_dir_fd | {move_after_open}
    )
    tool = Tool(allowed_roots=[str(allowed)])
    assert tool(str(allowed / "new.txt"), "fixture")["created"]
    assert (allowed / "new.txt").read_text(encoding="utf-8") == "fixture"
    assert not moved.exists()
