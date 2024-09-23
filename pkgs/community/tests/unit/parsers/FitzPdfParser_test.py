import pytest
from swarmauri_community.parsers.FitzPdfParser import PDFtoTextParser as Parser


@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == "FitzPdfParser"


@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse():
    documents = Parser().parse(r"resources/demo.pdf")
    assert documents[0].resource == "Document"
    assert documents[0].content == "This is a demo pdf \n"
    assert documents[0].metadata["source"] == r"resources/demo.pdf"
