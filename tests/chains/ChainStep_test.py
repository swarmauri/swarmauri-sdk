import pytest
from swarmauri.standard.chains.concrete.ChainStep import ChainStep


@pytest.mark.unit
def ubc_initialization_test():
    def test():
        def func(*args, **kwargs):
            return (args, kwargs)
    	step = ChainStep(key='test', method=func, args=[1,2], kwargs={"item": "value"}, ref=None)
        assert step.resource == 'ChainStep'
    test()

@pytest.mark.unit
def ubc_initialization_test():
    def test():
        args = [1,2]
        kwargs={"item": "value"}
        step = ChainStep(key='test', method=func, args=args, kwargs=kwargs, ref=None)
        result = step.method(*step.args, **step.kwargs)
        assert step.result[0] == args
        assert step.result[1] == kwargs
    test()
