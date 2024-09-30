import pytest
from swarmauri.tools.concrete import TextLengthTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'TextLengthTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.unit
def test_call(): 
    tool = Tool()
    text = "This is a simple test sentence."

    num_characters = 26
    num_words = 7
    num_sentences = 1

    expected_keys = {"num_characters", "num_words", "num_sentences"}

    result = tool(text)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("num_characters"),
                      int), f"Expected int, but got {type(result.get('num_characters')).__name__}"
    assert isinstance(result.get("num_words"),
                      int), f"Expected int, but got {type(result.get('num_words')).__name__}"
    assert isinstance(result.get("num_sentences"),
                      int), f"Expected int, but got {type(result.get('num_sentences')).__name__}"

    assert result.get(
        "num_characters") == num_characters, f"Expected Number of Characters is {num_characters}, but got {result.get('num_characters')}"
    assert result.get(
        "num_words") == num_words, f"Expected Number of Words is {num_words}, but got {result.get('num_words')}"
    assert result.get(
        "num_sentences") == num_sentences, f"Expected Number of Sentence is {num_sentences}, but got {result.get('num_sentences')}"

