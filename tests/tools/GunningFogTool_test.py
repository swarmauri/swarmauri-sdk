import pytest
from swarmauri.standard.tools.concrete.GunningFogTool import GunningFogTool as Tool

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
def test_call():
    tool = Tool()
    data = {"input_text": "This is a sample sentence. It is used to test the Gunning-Fog tool."}
    num_of_major_punctuations = 2
    num_of_words = 13
    num_of_three_plus_syllable_words = 1

    expected_score = 0.4 * (
        ( num_of_words / num_of_major_punctuations) + 100 * (num_of_three_plus_syllable_words / num_of_words)
    )
    assert tool(data) == pytest.approx(expected_score, rel=1e-2)