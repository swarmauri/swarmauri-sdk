import pytest

from swarmauri_tool_findfile.FindFileTool import FindFileTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "FindFileTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_matches_an_exact_name(tmp_path):
    (tmp_path / "report.txt").write_text("x", encoding="utf-8")
    (tmp_path / "other.txt").write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="report.txt")

    assert result["count"] == 1
    assert result["matches"] == [str(tmp_path / "report.txt")]


@pytest.mark.unit
def test_matches_a_wildcard(tmp_path):
    for name in ("app.log", "worker.log", "notes.txt"):
        (tmp_path / name).write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="*.log")

    names = sorted(path.rsplit("/", 1)[-1] for path in result["matches"])
    assert names == ["app.log", "worker.log"]


@pytest.mark.unit
def test_matching_is_case_insensitive(tmp_path):
    """A lowercase file must match an uppercase pattern, and the reverse."""
    (tmp_path / "report.pdf").write_text("x", encoding="utf-8")
    (tmp_path / "NOTES.TXT").write_text("x", encoding="utf-8")

    upper_pattern = Tool()(path=str(tmp_path), pattern="*.PDF")
    lower_pattern = Tool()(path=str(tmp_path), pattern="*.txt")

    assert upper_pattern["count"] == 1
    assert lower_pattern["count"] == 1


@pytest.mark.unit
def test_single_character_wildcard(tmp_path):
    for name in ("a1.txt", "a22.txt"):
        (tmp_path / name).write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="a?.txt")

    assert [path.rsplit("/", 1)[-1] for path in result["matches"]] == [
        "a1.txt"
    ]


@pytest.mark.unit
def test_not_recursive_by_default(tmp_path):
    nested = tmp_path / "archive"
    nested.mkdir()
    (tmp_path / "top.log").write_text("x", encoding="utf-8")
    (nested / "deep.log").write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="*.log")

    assert result["matches"] == [str(tmp_path / "top.log")]


@pytest.mark.unit
def test_recursive_descends_into_subdirectories(tmp_path):
    nested = tmp_path / "archive" / "2026"
    nested.mkdir(parents=True)
    (tmp_path / "top.log").write_text("x", encoding="utf-8")
    (nested / "deep.log").write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="*.log", recursive=True)

    assert result["count"] == 2
    assert result["matches"] == sorted(
        [str(tmp_path / "top.log"), str(nested / "deep.log")]
    )


@pytest.mark.unit
def test_directories_are_not_returned(tmp_path):
    (tmp_path / "folder.txt").mkdir()
    (tmp_path / "file.txt").write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="*.txt")

    assert result["matches"] == [str(tmp_path / "file.txt")]


@pytest.mark.unit
def test_no_matches_is_not_an_error(tmp_path):
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")

    result = Tool()(path=str(tmp_path), pattern="*.log")

    assert result["count"] == 0
    assert result["matches"] == []
    assert "error" not in result


@pytest.mark.unit
def test_missing_directory_reports_an_error(tmp_path):
    result = Tool()(path=str(tmp_path / "nope"), pattern="*.log")

    assert result["count"] == 0
    assert "does not exist" in str(result["error"])


@pytest.mark.unit
def test_a_file_path_reports_an_error(tmp_path):
    target = tmp_path / "note.txt"
    target.write_text("x", encoding="utf-8")

    result = Tool()(path=str(target), pattern="*.txt")

    assert result["matches"] == []
    assert "is not a directory" in str(result["error"])


@pytest.mark.unit
def test_does_not_follow_symlink_loops(tmp_path):
    (tmp_path / "b.txt").write_text("x", encoding="utf-8")
    try:
        (tmp_path / "loop").symlink_to(tmp_path, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("symlinks are not available on this platform")

    result = Tool()(path=str(tmp_path), pattern="*.txt", recursive=True)

    assert result["count"] == 1


@pytest.mark.unit
def test_expands_a_home_relative_path(tmp_path, monkeypatch):
    # expanduser consults HOME on POSIX and USERPROFILE on Windows; patch both
    # so the test never touches the developer's real home directory.
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.setenv("HOMEDRIVE", tmp_path.drive or "")
    monkeypatch.setenv("HOMEPATH", str(tmp_path)[len(tmp_path.drive) :])
    (tmp_path / "note.txt").write_text("x", encoding="utf-8")

    result = Tool()(path="~", pattern="*.txt")

    assert result["count"] == 1
