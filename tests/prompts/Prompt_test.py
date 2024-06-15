import pytest
from swarmauri.standard.prompts.concrete.Prompt import Prompt

@pytest.mark.unit
def test_1():
	def test():
		assert Prompt(prompt='test')() == 'test'
	test()
