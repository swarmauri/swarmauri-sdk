import pytest
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix

@pytest.mark.unit
def test_ubc_resource():
    def test():
    	prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
    	assert prompt_matrix.resource == 'Prompt'
    test()

@pytest.mark.unit
def shape_interface_test():
	def test():
		prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
		assert prompt_matrix.shape == (2,2)
	test()

@pytest.mark.unit
def show_matrix_test():
	def test():
		prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
		assert prompt_matrix.show() == [['1','2'], ['3','4']]
	test()






