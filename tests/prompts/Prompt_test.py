import pytest
from swarmauri.standard.prompts.concrete.Prompt import Prompt

@pytest.mark.unit
def test_ubc_resource():
    def test():
        assert Prompt().resource == 'Prompt'
    test()


@pytest.mark.unit
def test_call():
	def test():
		assert Prompt(prompt='test')() == 'test'
	test()
