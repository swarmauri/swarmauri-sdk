import pytest
from swarmauri.parsers.concrete.Md2HtmlParser import Md2HtmlParser as Parser

@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == 'Parser'

@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == 'Md2HtmlParser'

@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse():
    string_to_parse = '''# test \n\n # TEST ## teset \n ## sdfsdf # dsf \n # test \n # TEST ## teset \n ## sdfsdf # dsf'''
    assert Parser().parse(string_to_parse)[0].resource == 'Document'
    assert Parser().parse(string_to_parse)[0].content == '<h1>test </h1><p> <h1>TEST <h2>teset </h2></h1><br> <h2>sdfsdf <h1>dsf </h2></h1><br> <h1>test </h1><br> <h1>TEST <h2>teset </h2></h1><br> <h2>sdfsdf <h1>dsf</h2></h1>'
