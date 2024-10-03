import pytest
from swarmauri.tools.concrete import GunningFogTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'GunningFogTool'

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
    "input_text, num_of_major_punctuations, num_of_words, num_of_three_plus_syllable_words, expected_score",
    [
        ("This is a sample sentence. It is used to test the Gunning-Fog tool.", 2, 13, 1, 5.65),   # Test case 1
        ("Another example with more complex sentences; used for testing.", 3, 10, 2, 16.93),      # Test case 2
        ("Short sentence.", 1, 3, 0, 20.8),                                                # Test case 3
        ("Punctuation-heavy text! Is it really? Yes, it is! 42", 5, 10, 1, 5.0),             # Test case 4
        ("", 0, 0, 0, 0)                                                                  # Test case 5: empty string
    ]
)
def test_call(input_text, num_of_major_punctuations, num_of_words, num_of_three_plus_syllable_words, expected_score):
    tool = Tool()
    data = {"input_text": input_text}

    expected_keys = {'gunning_fog_score'}

    result = tool(data)

    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("gunning_fog_score"), float), f"Expected float, but got {type(result.get('gunning_fog_score')).__name__}"

    assert result.get("gunning_fog_score") == pytest.approx(expected_score, rel=0.01), f"Expected Gunning-Fog score {pytest.approx(expected_score, rel=0.01)}, but got {result.get('gunning_fog_score')}"