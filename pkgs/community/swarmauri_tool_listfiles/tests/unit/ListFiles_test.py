from pathlib import Path

import pytest

from swarmauri_tool_listfiles.ListFilesTool import ListFilesTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "ListFilesTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_lists_files_and_directories(tmp_path):
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    (tmp_path / "sub").mkdir()
    tool = Tool()

    result = tool(path=str(tmp_path))

    names = [entry["name"] for entry in result["entries"]]
    assert result["count"] == 2
    assert names == ["note.txt", "sub"]
    kinds = {entry["name"]: entry["is_dir"] for entry in result["entries"]}
    assert kinds == {"note.txt": False, "sub": True}


@pytest.mark.unit
def test_returns_names_only_by_default(tmp_path):
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    tool = Tool()

    result = tool(path=str(tmp_path))

    assert "path" not in result["entries"][0]


@pytest.mark.unit
def test_full_paths_adds_an_absolute_path(tmp_path):
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    tool = Tool()

    result = tool(path=str(tmp_path), full_paths=True)

    entry = result["entries"][0]
    assert entry["path"] == str(tmp_path / "note.txt")
    assert entry["name"] == "note.txt"


@pytest.mark.unit
def test_empty_directory(tmp_path):
    tool = Tool()

    result = tool(path=str(tmp_path))

    assert result["count"] == 0
    assert result["entries"] == []
    assert "error" not in result


@pytest.mark.unit
def test_entries_are_sorted_case_insensitively(tmp_path):
    for name in ("Zeta", "alpha", "Beta"):
        (tmp_path / name).write_text("x", encoding="utf-8")
    tool = Tool()

    result = tool(path=str(tmp_path))

    names = [entry["name"] for entry in result["entries"]]
    assert names == ["alpha", "Beta", "Zeta"]


@pytest.mark.unit
def test_missing_directory_reports_an_error(tmp_path):
    tool = Tool()

    result = tool(path=str(tmp_path / "nope"))

    assert result["count"] == 0
    assert "does not exist" in str(result["error"])


@pytest.mark.unit
def test_a_file_path_reports_an_error(tmp_path):
    target = tmp_path / "note.txt"
    target.write_text("x", encoding="utf-8")
    tool = Tool()

    result = tool(path=str(target))

    assert result["entries"] == []
    assert "is not a directory" in str(result["error"])


@pytest.mark.unit
def test_expands_a_home_relative_path(tmp_path, monkeypatch):
    # expanduser consults HOME on POSIX and USERPROFILE on Windows; patch both
    # so the test never touches the developer's real home directory.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOMEDRIVE", tmp_path.drive or "")
    monkeypatch.setenv("HOMEPATH", str(tmp_path)[len(tmp_path.drive) :])
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")
    tool = Tool()

    result = tool(path="~")

    assert result["count"] == 1
    assert result["entries"][0]["name"] == "note.txt"


@pytest.mark.unit
def test_full_paths_report_the_entry_not_a_symlink_target(tmp_path):
    """A symlink entry must be addressable by the path that is returned."""
    real = tmp_path / "real.txt"
    real.write_text("x", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(real)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available on this platform")

    result = Tool()(path=str(tmp_path), full_paths=True)

    entry = next(
        item for item in result["entries"] if item["name"] == "link.txt"
    )
    assert entry["path"] == str(tmp_path / "link.txt")


@pytest.mark.unit
def test_unsearchable_probe_returns_an_error(tmp_path, monkeypatch):
    """A probe that raises must be reported, not propagated."""

    def denied(self):
        raise PermissionError("denied")

    monkeypatch.setattr(Path, "exists", denied)

    result = Tool()(path=str(tmp_path))

    assert result["entries"] == []
    assert "Could not read" in str(result["error"])
