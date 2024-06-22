import pytest
from swarmauri.core.typing import SubclassUnion
from swarmauri.core.ComponentBase import ComponentBase

@pytest.mark.unit
def test_type():
	assert type(SubclassUnion) == type

@pytest.mark.unit
def test_():
	assert type(SubclassUnion[ComponentBase])

    