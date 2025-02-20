import pytest
from swarmauri_core.ComponentBase import ComponentBase, SubclassUnion


@pytest.mark.unit
def test_type():
    assert type(SubclassUnion) is type


@pytest.mark.unit
def test_subclasses():
    assert type(SubclassUnion[ComponentBase])
