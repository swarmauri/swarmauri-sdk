import builtins
from pathlib import Path

import pytest

from swarmauri_tool_createfile.CreateFileTool import CreateFileTool as Tool


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
    tool = Tool()

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
def test_removes_the_partial_file_when_the_write_fails(tmp_path, monkeypatch):
    """A failed write must not leave a partial file behind."""
    target = tmp_path / "note.txt"
    real_open = Path.open

    class FailingHandle:
        """Stands in for a successfully created file whose write then fails."""

        def __enter__(self):
            with builtins.open(str(target), "w", encoding="utf-8") as created:
                created.write("partial")
            return self

        def __exit__(self, *exc_info):
            return False

        def write(self, data):
            raise OSError("No space left on device")

    def fake_open(self, *args, **kwargs):
        if self == target:
            return FailingHandle()
        return real_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fake_open)

    result = Tool()(path=str(target), content="hello\n")

    assert result["created"] is False
    assert "No space left" in str(result["error"])
    assert not target.exists()
