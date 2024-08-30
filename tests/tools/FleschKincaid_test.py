import pytest
from swarmauri.standard.tools.concrete.FleschKincaidTool import FleschKincaidTool as Tool

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

    # Call the tool with the input data
    result = tool(input_data)
    
    # Validate the results
    assert 'reading_ease' in result
    assert 'grade_level' in result
    assert abs(result['reading_ease'] - expected_reading_ease) < 0.1
    assert abs(result['grade_level'] - expected_grade_level) < 0.1