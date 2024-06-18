import pytest
from swarmauri.standard.chains.concrete.ChainStep import ChainStep


@pytest.mark.unit
def test_ubc_resource():
    def test():
        def func(*args, **kwargs):
            return (args, kwargs)
        step = ChainStep(key='test', method=func, args=[1,2], kwargs={"item": "value"}, ref=None)
        assert step.resource == 'ChainStep'
    test()

@pytest.mark.unit
def test_method_call():
    def test():
        def func(*args, **kwargs):
            return (args, kwargs)
        args = [1,2]
        kwargs={"item": "value"}
        step = ChainStep(key='test', method=func, args=args, kwargs=kwargs, ref=None)
        result = step.method(*step.args, **step.kwargs)
        assert result[0] == args
        assert result[1] == kwargs
    test()
