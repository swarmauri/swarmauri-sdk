import pytest
from swarmauri_core.typing import SubclassUnion
from swarmauri_core.ComponentBase import ComponentBase

@pytest.mark.unit
def test_type():
	assert type(SubclassUnion) == type

@pytest.mark.unit
def test_subclasses():
	assert type(SubclassUnion[ComponentBase])

    