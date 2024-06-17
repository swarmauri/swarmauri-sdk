import pytest
from swarmauri.standard.prompts.concrete.PromptTemplate import PromptTemplate

@pytest.mark.unit
def test_ubc_resource():
    def test():
    	pt = PromptTemplate(template="Please find {number} items.")
    	assert pt.resource == 'Prompt'
    test()


@pytest.mark.unit
def test_call():
	def test():
		pt = PromptTemplate(template="Please find {number} items.")
		assert pt(variables={"number":100}) == "Please find 100 items."
	test()