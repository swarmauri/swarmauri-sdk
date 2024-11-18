import pytest
from swarmauri.parsers.concrete.TextBlobNounParser import TextBlobNounParser as Parser


def setup_module(module):
    """Setup any state specific to the execution of the given module."""
    try:
        # Initialize a parser to trigger NLTK downloads
        Parser()
    except Exception as e:
        pytest.skip(f"Failed to initialize NLTK resources: {str(e)}")


@pytest.fixture(scope="module")
def parser():
    """Fixture to provide a parser instance for tests."""
    return Parser()


@pytest.mark.unit
def test_ubc_resource(parser):
    assert parser.resource == "Parser"


@pytest.mark.unit
def test_ubc_type(parser):
    assert parser.type == "TextBlobNounParser"


@pytest.mark.unit
def test_serialization(parser):
    assert parser.id == Parser.model_validate_json(parser.model_dump_json()).id


@pytest.mark.unit
def test_parse(parser):
    try:
        documents = parser.parse("One more large chapula please.")
        assert documents[0].resource == "Document"
        assert documents[0].content == "One more large chapula please."
        assert documents[0].metadata["noun_phrases"] == ["large chapula"]
    except Exception as e:
        pytest.fail(f"Parser failed with error: {str(e)}")
