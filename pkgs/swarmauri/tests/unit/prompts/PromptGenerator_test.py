import pytest
from swarmauri.prompts.concrete.PromptGenerator import PromptGenerator

@pytest.mark.unit
def test_ubc_resource():
	variables_list = [{"number": 100}, {"number": 200}, {"number": -1}]
	pg = PromptGenerator(template="We have {number} items", variables=variables_list)
	assert pg.resource == 'Prompt'

@pytest.mark.unit
def test_ubc_type():
	variables_list = [{"number": 100}, {"number": 200}, {"number": -1}]
	pg = PromptGenerator(template="We have {number} items", variables=variables_list)
	assert pg.type == 'PromptGenerator'

@pytest.mark.unit
def test_serialization():
	variables_list = [{"number": 100}, {"number": 200}, {"number": -1}]
	pg = PromptGenerator(template="We have {number} items", variables=variables_list)
	assert pg.id == PromptGenerator.model_validate_json(pg.model_dump_json()).id
	assert pg.variables == variables_list

@pytest.mark.unit
def test_calls():
	variables_list = [{"number": 100}, {"number": 200}, {"number": -1}]
	pg = PromptGenerator(template="We have {number} items", variables=variables_list)
	pg_generator = pg()
	generated_list = [next(pg_generator) for _ in range(len(pg.variables))]
	assert generated_list == ['We have 100 items', 'We have 200 items', 'We have -1 items']
