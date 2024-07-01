import pytest
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix

@pytest.mark.unit
def test_ubc_resource():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.resource == 'Prompt'

@pytest.mark.unit
def test_ubc_type():
    prompt = Prompt()
    assert prompt.type == 'Prompt'

@pytest.mark.unit
def test_serialization():
    prompt = Prompt(prompt='test')
    assert prompt.id == Prompt.model_validate_json(prompt.model_dump()).id

@pytest.mark.unit
def shape_interface_test():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.shape == (2,2)

@pytest.mark.unit
def show_matrix_test():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.show() == [['1','2'], ['3','4']]






