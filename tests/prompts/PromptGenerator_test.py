import pytest
from swarmauri.standard.prompts.concrete.PromptGenerator import PromptGenerator


@pytest.mark.unit
def ubc_initialization_test():
    def test():
		variables_list = [{"number": 100}, {"number": 200}, {"number": -1}]
		pg = PromptGenerator(template="We have {number} items", variables=variables_list)
        assert pg.resource == 'Prompt'
    test()

@pytest.mark.unit
def test_1():
	def test():
		variables_list = [{"number": 100}, {"number": 200}, {"number": -1}]
		pg = PromptGenerator(template="We have {number} items", variables=variables_list)
		pg_generator = pg()

		generated_list = [next(pg_generator) for _ in range(len(pg.variables))]
		assert generated_list == ['We have 100 items', 'We have 200 items', 'We have -1 items']
	test()