import pytest
from swarmauri.standard.parsers.concrete.MarkdownParser import MarkdownParser

@pytest.mark.unit
def test_ubc_resource():
    def test():
        parser = MarkdownParser()
        assert parser.resource == 'Parser'
    test()

@pytest.mark.unit
def test_parse():
    def test():
        string_to_parse = '''# test \n\n # TEST ## teset \n ## sdfsdf # dsf \n # test \n # TEST ## teset \n ## sdfsdf # dsf'''
        assert MarkdownParser().parse(string_to_parse)[0].resource == 'Document'
        assert MarkdownParser().parse(string_to_parse)[0].content == '<h1>test </h1><p> <h1>TEST <h2>teset </h2></h1><br> <h2>sdfsdf <h1>dsf </h2></h1><br> <h1>test </h1><br> <h1>TEST <h2>teset </h2></h1><br> <h2>sdfsdf <h1>dsf</h2></h1>'
    test()
