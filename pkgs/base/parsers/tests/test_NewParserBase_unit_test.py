import pytest
import NewParserBase


def test_resource():
    assert NewParserBase.resource == parsers

def test_type():
    assert NewParserBase.type == NewParserBase

def test_serialization():
    assert NewParserBase.id == NewParserBase.model_validate_json()