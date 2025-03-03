import pytest
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion

@pytest.mark.xfail
def test_type():
    assert type(SubclassUnion) is type

@pytest.mark.unit
def test_subclasses():
    assert type(SubclassUnion[ComponentBase])
