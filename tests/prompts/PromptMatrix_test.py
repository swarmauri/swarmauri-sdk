import pytest
from swarmauri.standard.prompts.concrete.PromptMatrix import PromptMatrix

@pytest.mark.unit
def test_1():
	def test():
		prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
		assert prompt_matrix.shape == (2,2)
	test()


@pytest.mark.unit
def test_2():
	def test():
		prompt_matrix = PromptMatrix(matrix=[["1","2"],["3","4"]])
		assert prompt_matrix.show() == [['1','2'], ['3','4']]
	test()






