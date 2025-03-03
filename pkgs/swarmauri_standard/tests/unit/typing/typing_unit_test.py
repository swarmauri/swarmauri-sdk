import pytest
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.DynamicBase import SubclassUnion


@pytest.mark.unit
def test_type():
    assert type(SubclassUnion) is type


@pytest.mark.unit
def test_subclasses():
    assert type(SubclassUnion[ComponentBase])
