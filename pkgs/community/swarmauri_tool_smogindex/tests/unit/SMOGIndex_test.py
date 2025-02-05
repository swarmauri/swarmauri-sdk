import pytest
from swarmauri_tool_smogindex.SMOGIndexTool import (
    SMOGIndexTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "SMOGIndexTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@pytest.mark.parametrize(
    "input_text, expected_smog_index",
    [
        (
            "This is a sample text with some complex sentences and polysyllabic words to test the SMOG Index calculation.",
            8.5,
        ),  # Test case 1: sample text
        ("Simple text with few words.", 2.3),  # Test case 2: simple text
        (
            "A longer piece of text that is still relatively simple but includes a few more sentences and polysyllabic words for a more complex evaluation.",
            6.1,
        ),  # Test case 3: more complex text
        ("", 0.0),  # Test case 4: empty string
        (
            "Text with only short words and sentences.",
            1.8,
        ),  # Test case 5: very simple text
    ],
)
def test_call(input_text, expected_smog_index):
    tool = Tool()

    expected_smog_index_calculated = tool.calculate_smog_index(input_text)

    expected_keys = {"smog_index"}

    result = tool(input_text)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), (
        f"Expected keys {expected_keys} but got {result.keys()}"
    )
    assert isinstance(result.get("smog_index"), float), (
        f"Expected float, but got {type(result.get('smog_index')).__name__}"
    )

    assert result.get("smog_index") == pytest.approx(
        expected_smog_index_calculated, rel=0.1
    ), (
        f"Expected SMOG Index {pytest.approx(expected_smog_index_calculated, rel=0.1)}, but got {result.get('smog_index')}"
    )
