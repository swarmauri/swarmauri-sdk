import pytest
from swarmauri.standard.tools.concrete.ColemanLiauIndexTool import ColemanLiauIndexTool as Tool

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
def test_call():
    tool = Tool()
    # Example input text for CLI calculation
    input_data = {"input_text": "This is a simple test text. It contains two sentences."}
    
    # Calculating expected CLI score manually
    num_sentences = 2
    num_words = 10
    num_characters = 42

    L = (num_characters / num_words) * 100
    S = (num_sentences / num_words) * 100
    expected_cli_score = 0.0588 * L - 0.296 * S - 15.8

    # Assert that the CLI tool calculates the expected value
    assert tool(input_data) == pytest.approx(expected_cli_score, 0.01)