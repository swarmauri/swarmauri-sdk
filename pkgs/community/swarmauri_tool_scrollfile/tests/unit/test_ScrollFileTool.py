from importlib import import_module
from pathlib import Path

import pytest
from swarmauri_tool_scrollfile import ScrollFileTool, __version__


@pytest.fixture
def numbered_file(tmp_path: Path) -> Path:
    path = tmp_path / "numbered.txt"
    path.write_text(
        "".join(f"line {line_number}\n" for line_number in range(1, 13)),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def scroll_tool(tmp_path: Path) -> ScrollFileTool:
    return ScrollFileTool(allowed_roots=[str(tmp_path)])


@pytest.mark.unit
def test_component_contract_and_serialization() -> None:
    tool = ScrollFileTool()

    assert tool.resource == "Tool"
    assert tool.type == "ScrollFileTool"
    assert isinstance(tool.id, str)
    assert (
        ScrollFileTool.model_validate_json(tool.model_dump_json()).id
        == tool.id
    )
    assert [parameter.name for parameter in tool.parameters] == [
        "file_path",
        "start_line",
        "page_size",
        "direction",
    ]
    assert __version__ == "0.1.0"


@pytest.mark.unit
def test_reads_default_first_page(
    scroll_tool: ScrollFileTool, numbered_file: Path
) -> None:
    result = scroll_tool(str(numbered_file))

    assert [line["line_number"] for line in result["lines"]] == list(
        range(1, 11)
    )
    assert result["start_line"] == 1
    assert result["end_line"] == 10
    assert result["has_previous"] is False
    assert result["has_next"] is True
    assert result["previous_start_line"] is None
    assert result["next_start_line"] == 11


@pytest.mark.unit
def test_reads_middle_and_final_pages(
    scroll_tool: ScrollFileTool, numbered_file: Path
) -> None:
    middle = scroll_tool(str(numbered_file), start_line=6, page_size=5)
    final = scroll_tool(str(numbered_file), start_line=11, page_size=5)

    assert [line["content"] for line in middle["lines"]] == [
        f"line {line_number}" for line_number in range(6, 11)
    ]
    assert middle["previous_start_line"] == 1
    assert middle["next_start_line"] == 11
    assert [line["line_number"] for line in final["lines"]] == [11, 12]
    assert final["has_next"] is False
    assert final["next_start_line"] is None


@pytest.mark.unit
def test_scrolls_up_one_page(
    scroll_tool: ScrollFileTool, numbered_file: Path
) -> None:
    result = scroll_tool(
        str(numbered_file), start_line=11, page_size=5, direction="up"
    )

    assert [line["line_number"] for line in result["lines"]] == [
        6,
        7,
        8,
        9,
        10,
    ]
    assert result["previous_start_line"] == 1
    assert result["next_start_line"] == 11


@pytest.mark.unit
def test_upward_scroll_does_not_cross_anchor(
    scroll_tool: ScrollFileTool, numbered_file: Path
) -> None:
    result = scroll_tool(
        str(numbered_file), start_line=3, page_size=5, direction="up"
    )

    assert [line["line_number"] for line in result["lines"]] == [1, 2]
    assert result["start_line"] == 1
    assert result["end_line"] == 2
    assert result["next_start_line"] == 3


@pytest.mark.unit
def test_clamps_beyond_eof_to_final_page(
    scroll_tool: ScrollFileTool, numbered_file: Path
) -> None:
    result = scroll_tool(str(numbered_file), start_line=100, page_size=5)

    assert [line["line_number"] for line in result["lines"]] == [
        8,
        9,
        10,
        11,
        12,
    ]
    assert result["start_line"] == 8
    assert result["end_line"] == 12
    assert result["has_next"] is False


@pytest.mark.unit
def test_exact_page_and_empty_file(tmp_path: Path) -> None:
    exact = tmp_path / "exact.txt"
    exact.write_text("one\ntwo\n", encoding="utf-8")
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    exact_result = tool(str(exact), page_size=2)
    empty_result = tool(str(empty))

    assert exact_result["has_next"] is False
    assert exact_result["end_line"] == 2
    assert empty_result["lines"] == []
    assert empty_result["start_line"] == 1
    assert empty_result["end_line"] is None
    assert empty_result["has_previous"] is False
    assert empty_result["has_next"] is False


@pytest.mark.unit
def test_preserves_utf8_and_strips_only_line_endings(tmp_path: Path) -> None:
    path = tmp_path / "utf8.txt"
    path.write_text("café  \nनमस्ते\r\n", encoding="utf-8", newline="")

    result = ScrollFileTool(allowed_roots=[str(tmp_path)])(str(path))

    assert [line["content"] for line in result["lines"]] == [
        "café  ",
        "नमस्ते",
    ]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"file_path": ""}, "file_path"),
        ({"file_path": "file.txt", "start_line": 0}, "start_line"),
        ({"file_path": "file.txt", "start_line": True}, "start_line"),
        ({"file_path": "file.txt", "page_size": 0}, "page_size"),
        ({"file_path": "file.txt", "page_size": False}, "page_size"),
        ({"file_path": "file.txt", "direction": "sideways"}, "direction"),
    ],
)
def test_rejects_invalid_arguments(
    kwargs: dict[str, object], message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        ScrollFileTool()(**kwargs)


@pytest.mark.unit
def test_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ScrollFileTool(allowed_roots=[str(tmp_path)])(
            str(tmp_path / "missing.txt")
        )


@pytest.mark.unit
def test_rejects_paths_outside_allowed_roots(tmp_path: Path) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("private\n", encoding="utf-8")

    tool = ScrollFileTool(allowed_roots=[str(allowed_root)])
    with pytest.raises(PermissionError, match="allowed_roots"):
        tool(str(outside_file))


@pytest.mark.unit
def test_rejects_parent_traversal_outside_allowed_root(
    tmp_path: Path,
) -> None:
    allowed_root = tmp_path / "allowed"
    allowed_root.mkdir()
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("private\n", encoding="utf-8")

    tool = ScrollFileTool(allowed_roots=[str(allowed_root)])
    with pytest.raises(PermissionError, match="allowed_roots"):
        tool(str(allowed_root / ".." / "outside.txt"))


@pytest.mark.unit
def test_rejects_symlinks_by_default(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("content\n", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    with pytest.raises(PermissionError, match="symlinks"):
        tool(str(link))


@pytest.mark.unit
def test_allows_symlinks_only_with_explicit_opt_in(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("content\n", encoding="utf-8")
    link = tmp_path / "link.txt"
    link.symlink_to(target)

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)], allow_symlinks=True)
    assert tool(str(link))["lines"][0]["content"] == "content"


@pytest.mark.unit
def test_rejects_non_regular_files(tmp_path: Path) -> None:
    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    with pytest.raises(ValueError, match="regular file"):
        tool(str(tmp_path))


@pytest.mark.unit
def test_enforces_argument_budgets(tmp_path: Path) -> None:
    path = tmp_path / "file.txt"
    path.write_text("content\n", encoding="utf-8")
    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])

    with pytest.raises(ValueError, match="page_size cannot exceed"):
        tool(str(path), page_size=ScrollFileTool.MAX_PAGE_SIZE + 1)
    with pytest.raises(ValueError, match="start_line cannot exceed"):
        tool(
            str(path),
            start_line=ScrollFileTool.MAX_SCANNED_LINES + 1,
        )


@pytest.mark.unit
def test_rejects_oversized_individual_lines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "long-line.txt"
    path.write_text("12345\n", encoding="utf-8")
    monkeypatch.setattr(ScrollFileTool, "MAX_LINE_BYTES", 4)

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    with pytest.raises(ValueError, match="individual-line byte limit"):
        tool(str(path))


@pytest.mark.unit
def test_enforces_scanned_and_returned_byte_budgets(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "file.txt"
    path.write_text("1234\n5678\n", encoding="utf-8")
    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])

    monkeypatch.setattr(ScrollFileTool, "MAX_SCANNED_BYTES", 4)
    with pytest.raises(ValueError, match="scanned-byte limit"):
        tool(str(path))

    monkeypatch.setattr(ScrollFileTool, "MAX_SCANNED_BYTES", 100)
    monkeypatch.setattr(ScrollFileTool, "MAX_RETURN_BYTES", 3)
    with pytest.raises(ValueError, match="returned-byte limit"):
        tool(str(path))


@pytest.mark.unit
def test_enforces_returned_byte_budget_for_beyond_eof_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "file.txt"
    path.write_text("aa\nbb\n", encoding="utf-8")
    monkeypatch.setattr(ScrollFileTool, "MAX_RETURN_BYTES", 3)

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    with pytest.raises(ValueError, match="returned-byte limit"):
        tool(str(path), start_line=100, page_size=2)


@pytest.mark.unit
def test_enforces_scanned_line_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "file.txt"
    path.write_text("first\nsecond\n", encoding="utf-8")
    monkeypatch.setattr(ScrollFileTool, "MAX_SCANNED_LINES", 1)

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    with pytest.raises(ValueError, match="scanned-line limit"):
        tool(str(path), page_size=1)


@pytest.mark.unit
def test_enforces_elapsed_time_budget(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "file.txt"
    path.write_text("content\n", encoding="utf-8")
    timestamps = iter([0.0, ScrollFileTool.MAX_ELAPSED_SECONDS + 1])
    scroll_file_module = import_module(
        "swarmauri_tool_scrollfile.ScrollFileTool"
    )
    monkeypatch.setattr(
        scroll_file_module.time,
        "monotonic",
        timestamps.__next__,
    )

    tool = ScrollFileTool(allowed_roots=[str(tmp_path)])
    with pytest.raises(ValueError, match="elapsed-time limit"):
        tool(str(path))
