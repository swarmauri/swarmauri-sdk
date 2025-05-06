import pytest
from swarmauri_standard.parsers.URLExtractorParser import URLExtractorParser as Parser


@pytest.mark.unit
def test_ubc_resource():
    parser = Parser()
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type():
    parser = Parser()
    assert parser.type == "URLExtractorParser"


@pytest.mark.unit
def test_serialization():
    parser = Parser()
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse():
    documents = Parser().parse(
        "https://www.swarmauri_standard.com, swarmauri_standard.app, and swarmauri_standard agents."
    )
    assert len(documents) == 1
    assert documents[0].resource == "Document"
    assert documents[0].content == "https://www.swarmauri_standard.com"
    assert documents[0].metadata["source"] == "URLExtractor"
