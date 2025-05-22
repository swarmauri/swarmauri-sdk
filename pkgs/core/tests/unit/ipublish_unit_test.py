import inspect
import pytest
from swarmauri_core.publishers.IPublish import IPublish


@pytest.mark.unit
def test_ipublish_is_abstract():
    assert hasattr(IPublish, "publish")
    assert inspect.isfunction(IPublish.publish)
    assert getattr(IPublish.publish, "__isabstractmethod__", False)
