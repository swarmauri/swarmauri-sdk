import pytest
from swarmauri.tools.concrete import FleschKincaidTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'FleschKincaidTool'

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
    input_data = {
        'input_text': "This is a sample text. It contains several sentences. Each sentence has a few words."
    }
    
    # Expected values
    words = 15
    sentences = 3
    syllables = 21

    words_per_sentence = words / sentences
    syllables_per_word = syllables / words
    
    expected_reading_ease = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
    expected_grade_level = 0.39 * words_per_sentence + 11.8 * syllables_per_word - 15.59

    expected_keys = {'reading_ease', 'grade_level'}

    result = tool(input_data)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"

    assert isinstance(result.get("reading_ease"),
                      float), f"Expected float, but got {type(result.get('reading_ease')).__name__}"
    assert isinstance(result.get("grade_level"),
                      float), f"Expected float, but got {type(result.get('grade_level')).__name__}"

    assert result.get(
        "reading_ease") == expected_reading_ease, f"Expected Reading Ease value is {expected_reading_ease}, but got {result.get('reading_ease')}"
    assert result.get(
        "grade_level") == expected_grade_level, f"Expected Grade Level value is {expected_grade_level}, but got {result.get('grade_level')}"

