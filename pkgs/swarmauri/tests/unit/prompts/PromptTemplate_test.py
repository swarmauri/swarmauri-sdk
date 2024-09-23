import pytest
from swarmauri.prompts.concrete.PromptTemplate import PromptTemplate

@pytest.mark.unit
def test_ubc_resource():
	pt = PromptTemplate(template="Please find {number} items.")
	assert pt.resource == 'Prompt'
	
@pytest.mark.unit
def test_ubc_type():
    prompt = PromptTemplate()
    assert prompt.type == 'PromptTemplate'

@pytest.mark.unit
def test_serialization():
    prompt = PromptTemplate(prompt='test')
    assert prompt.id == PromptTemplate.model_validate_json(prompt.model_dump_json()).id

@pytest.mark.unit
def test_call():
	pt = PromptTemplate(template="Please find {number} items.")
	assert pt(variables={"number":100}) == "Please find 100 items."
