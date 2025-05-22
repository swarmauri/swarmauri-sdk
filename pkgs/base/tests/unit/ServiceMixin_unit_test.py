import pytest
from swarmauri_base.ServiceMixin import ServiceMixin


class DummyService(ServiceMixin):
    pass


@pytest.mark.unit
def test_service_mixin_defaults():
    first = DummyService()
    second = DummyService()
    assert isinstance(first.id, str) and first.id
    assert first.members is None
    assert first.owners is None
    assert first.host is None
    # ids should be unique
    assert first.id != second.id
