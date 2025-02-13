import pytest
from swarmauri_tool_dalechallreadability.DaleChallReadabilityTool import (
    DaleChallReadabilityTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "DaleChallReadabilityTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_call():
    tool = Tool()

    # Input data for the tool
    input_data = {"input_text": "This is a simple sentence for testing purposes."}

    # Call the tool and capture the result
    result = tool(input_data)

    # Expected keys in the result
    expected_keys = {"dale_chall_score"}

    # Verify the result is a dictionary
    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"

    # Verify the result contains the 'dale_chall_score' key
    assert expected_keys.issubset(result.keys()), (
        f"Expected keys {expected_keys}, but got {result.keys()}"
    )

    # Verify the 'dale_chall_score' value is a float
    dale_chall_score = result.get("dale_chall_score")
    assert isinstance(dale_chall_score, float), (
        f"Expected float for 'dale_chall_score', but got {type(dale_chall_score).__name__}"
    )

    # Check if the score is approximately what is expected
    expected_output = 7.98

    assert dale_chall_score == pytest.approx(expected_output, rel=1e-2), (
        f"Expected score {expected_output}, but got {dale_chall_score}"
    )
