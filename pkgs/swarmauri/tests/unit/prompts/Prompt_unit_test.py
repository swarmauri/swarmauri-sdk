import pytest
from swarmauri.prompts.concrete.Prompt import Prompt

@pytest.mark.unit
def test_ubc_resource():
	assert Prompt().resource == 'Prompt'

@pytest.mark.unit
def test_ubc_type():
    prompt = Prompt()
    assert prompt.type == 'Prompt'

@pytest.mark.unit
def test_serialization():
    prompt = Prompt(prompt='test')
    assert prompt.id == Prompt.model_validate_json(prompt.model_dump_json()).id

@pytest.mark.unit
def test_call():
	assert Prompt(prompt='test')() == 'test'

