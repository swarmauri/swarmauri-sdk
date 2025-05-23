import pytest
from swarmauri_core.llms.IPredict import IPredict


@pytest.mark.unit
def test_ipredict_methods_are_abstract():
    for name in [
        "predict",
        "apredict",
        "stream",
        "astream",
        "batch",
        "abatch",
    ]:
        assert hasattr(IPredict, name)
        method = getattr(IPredict, name)
        assert getattr(method, "__isabstractmethod__", False)


class DummyPredict(IPredict):
    def predict(self, *args, **kwargs):
        return None

    async def apredict(self, *args, **kwargs):
        return None

    def stream(self, *args, **kwargs):
        return None

    async def astream(self, *args, **kwargs):
        return None

    def batch(self, *args, **kwargs):
        return []

    async def abatch(self, *args, **kwargs):
        return []


@pytest.mark.unit
def test_ipredict_can_be_subclassed():
    dummy = DummyPredict()
    assert isinstance(dummy, IPredict)
