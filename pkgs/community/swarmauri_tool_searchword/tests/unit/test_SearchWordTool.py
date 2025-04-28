import pytest
from swarmauri_tool_searchword.SearchWordTool import SearchWordTool
from unittest import mock


@pytest.mark.unit
def test_ubc_resource():
    tool = SearchWordTool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert SearchWordTool().type == "SearchWordTool"


@pytest.mark.unit
def test_initialization():
    tool = SearchWordTool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = SearchWordTool()
    assert tool.id == SearchWordTool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.parametrize(
    "file_path, search_word, expected",
    [
        (
            "test_file.txt",
            "sample",
            {
                "lines": [
                    "\x1b[1;31mThis is a sample text.\x1b[0m",
                    "Another line.",
                ],
                "count": 1,
            },
        ),
        (
            "test_file.txt",
            "a sample",
            {
                "lines": [
                    "\x1b[1;31mThis is a sample text.\x1b[0m",
                    "Another line.",
                ],
                "count": 1,
            },
        ),
        (
            "test_file.txt",
            "nonexistent",
            {
                "lines": ["This is a sample text.", "Another line."],
                "count": 0,
            },
        ),
    ],
)
def test_call(file_path, search_word, expected):
    """Test the __call__ method of SearchWordTool."""
    with mock.patch(
        "builtins.open",
        mock.mock_open(read_data="This is a sample text.\nAnother line."),
    ) as mock_file:
        tool = SearchWordTool()
        result = tool(file_path, search_word)

        mock_file.assert_called_once()

        assert isinstance(result["lines"], list), (
            f"Expected list, but got {type(result['lines']).__name__}"
        )
        assert len(result["lines"]) == len(expected["lines"])
        assert result["lines"] == expected["lines"]
        assert isinstance(result["count"], int), (
            f"Expected int, but got {type(result['count']).__name__}"
        )
        assert result["count"] == expected["count"]


@pytest.mark.unit
def test_validate_input():
    """Test the validate_input method of SearchWordTool."""
    tool = SearchWordTool()
    assert tool.validate_input("test_file.txt", "sample") is True
    assert tool.validate_input(123, "sample") is False
    assert tool.validate_input("test_file.txt", None) is False


@pytest.mark.unit
def test_file_not_found():
    """Test that FileNotFoundError is raised for non-existent files."""
    tool = SearchWordTool()
    with pytest.raises(FileNotFoundError):
        tool("nonexistent_file.txt", "sample")
