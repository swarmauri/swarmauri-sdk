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
def test_reads_default_first_page(numbered_file: Path) -> None:
    result = ScrollFileTool()(str(numbered_file))

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
def test_reads_middle_and_final_pages(numbered_file: Path) -> None:
    middle = ScrollFileTool()(str(numbered_file), start_line=6, page_size=5)
    final = ScrollFileTool()(str(numbered_file), start_line=11, page_size=5)

    assert [line["content"] for line in middle["lines"]] == [
        f"line {line_number}" for line_number in range(6, 11)
    ]
    assert middle["previous_start_line"] == 1
    assert middle["next_start_line"] == 11
    assert [line["line_number"] for line in final["lines"]] == [11, 12]
    assert final["has_next"] is False
    assert final["next_start_line"] is None


@pytest.mark.unit
def test_scrolls_up_one_page(numbered_file: Path) -> None:
    result = ScrollFileTool()(
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
def test_upward_scroll_does_not_cross_anchor(numbered_file: Path) -> None:
    result = ScrollFileTool()(
        str(numbered_file), start_line=3, page_size=5, direction="up"
    )

    assert [line["line_number"] for line in result["lines"]] == [1, 2]
    assert result["start_line"] == 1
    assert result["end_line"] == 2
    assert result["next_start_line"] == 3


@pytest.mark.unit
def test_clamps_beyond_eof_to_final_page(numbered_file: Path) -> None:
    result = ScrollFileTool()(str(numbered_file), start_line=100, page_size=5)

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

    exact_result = ScrollFileTool()(str(exact), page_size=2)
    empty_result = ScrollFileTool()(str(empty))

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

    result = ScrollFileTool()(str(path))

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
def test_missing_file_raises_file_not_found() -> None:
    with pytest.raises(FileNotFoundError):
        ScrollFileTool()("missing.txt")
