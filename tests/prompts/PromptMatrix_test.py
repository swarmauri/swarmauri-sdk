import pytest
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix

@pytest.mark.unit
def test_ubc_resource():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.resource == 'Prompt'

@pytest.mark.unit
def test_ubc_type():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.type == 'PromptMatrix'

@pytest.mark.unit
def test_serialization():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.id == PromptMatrix.model_validate_json(prompt_matrix.model_dump()).id

@pytest.mark.unit
def shape_interface_test():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.shape == (2,2)

@pytest.mark.unit
def show_matrix_test():
	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
	assert prompt_matrix.show() == [['1','2'], ['3','4']]






