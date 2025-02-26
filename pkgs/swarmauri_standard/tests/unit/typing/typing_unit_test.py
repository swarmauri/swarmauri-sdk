import warnings
import pytest
from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@pytest.mark.unit
def test_type():
    assert type(SubclassUnion) is type


@pytest.mark.unit
def test_subclasses():
    assert type(SubclassUnion[ComponentBase])
