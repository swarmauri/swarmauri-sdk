import pytest
from swarmauri.tools.concrete import FleschReadingEaseTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'FleschReadingEaseTool'

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
    "text, expected_score",
    [
        ("The cat sat on the mat.", 116.145),  # Test case 1: simple sentence
        ("This is a more complex sentence, with more words.", 94.30),  # Test case 2: more complex sentence
        ("Short sentence.", 77.90),  # Test case 3: short sentence
        ("", 206.835),  # Test case 4: empty string
        ("A very difficult sentence, with lots of complexity!", 40.09)  # Test case 5: complex sentence with punctuation
    ]
)
def test_call(text, expected_score):
    tool = Tool()

    expected_keys = {'flesch_reading_ease'}

    result = tool(text)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("flesch_reading_ease"), float), f"Expected float, but got {type(result).__name__}"

    assert result.get("flesch_reading_ease") == pytest.approx(expected_score,
                                                              rel=1e-2), f"Expected Flesch score {pytest.approx(expected_score, rel=1e-2)}, but got {result.get('flesch_reading_ease')}"
