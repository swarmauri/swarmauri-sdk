import pytest
from swarmauri.tools.concrete import ColemanLiauIndexTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == 'ColemanLiauIndexTool'

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
    "input_text, expected_cli_score",
    [
        ("This is a simple test text. It contains two sentences.", -0.7899999999999991),  # Test case 1
        ("Short sentence.", 8.340000000000003),  # Test case 2: very short text
        ("This is another example. It has more words in it.", 1.282666666666669),  # Test case 3: moderate length
        ("A very short. Text.", 13.553333333333338),  # Test case 4: fragmented sentences
        ("", 0.0)  # Test case 5: empty string
    ]
)
def test_call(input_text, expected_cli_score):
    tool = Tool()
    input_data = {"input_text": input_text}

    text = input_data["input_text"]
    num_sentences = tool.count_sentences(text)
    num_words = tool.count_words(text)
    num_characters = tool.count_characters(text)

    L = (num_characters / num_words) * 100 if num_words else 0
    S = (num_sentences / num_words) * 100 if num_words else 0
    expected_cli_score_calculated = 0.0588 * L - 0.296 * S - 15.8 if text else 0.0

    expected_keys = {'coleman_liau_index'}

    result = tool(input_data)
    assert isinstance(result, dict), f"Expected dict, but got {type(result).__name__}"
    assert expected_keys.issubset(result.keys()), f"Expected keys {expected_keys} but got {result.keys()}"
    assert isinstance(result.get("coleman_liau_index"), float), f"Expected float, but got {type(result).__name__}"
    assert result.get("coleman_liau_index") == pytest.approx(expected_cli_score_calculated,
                                                             0.01), f"Expected CLI score {pytest.approx(expected_cli_score_calculated, 0.01)}, but got {result.get('coleman_liau_index')}"
