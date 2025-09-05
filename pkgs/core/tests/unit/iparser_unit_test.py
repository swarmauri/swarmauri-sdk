import pytest
from swarmauri_core.parsers.IParser import IParser


@pytest.mark.unit
def test_iparser_methods_are_abstract():
    assert hasattr(IParser, "parse")
    assert getattr(IParser.parse, "__isabstractmethod__", False)
