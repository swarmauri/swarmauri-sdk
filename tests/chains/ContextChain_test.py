import pytest
from pydantic import BaseModel
from swarmauri.standard.chains.concrete.ContextChain import ContextChain


@pytest.mark.unit
def test_ubc_resource():
    def test():
        def func(*args, **kwargs):
            return ('test_response', args, kwargs)

        chain = ContextChain()
        assert chain.resource == 'Chain'
    test()

@pytest.mark.unit
def test_chain_execute_return_value():
    def test():
        # define func
        def func(*args, **kwargs):
            return ('test_response', args, kwargs)

        # declare chain, args, kwargs
        chain = ContextChain()
        args = (1,2,3)
        kwargs = {"test":123123123}
        
        # operate
        chain.add_step(key='key_1', method=func, args=args, kwargs=kwargs, ref="test_result")
        result = chain.execute()

        # assert
        assert result['test_result'][0] == 'test_response'
        assert result['test_result'][1] == args
        assert result['test_result'][2] == kwargs
    test()

@pytest.mark.unit
def test_chain_execute_return_state():
    def test():
        ref = "test_result"
        args = (1,2,3)
        kwargs = {"test":123123123}
        def func(*args, **kwargs):
            return ('test_response', args, kwargs)

        chain = ContextChain()
        chain.add_step(key='key_1', method=func, args=args, kwargs=kwargs, ref=ref)
        chain.execute()
        assert chain.context['test_result'][0] == 'test_response'
        assert chain.context['test_result'][1] == args
        assert chain.context['test_result'][2] == kwargs
    test()

@pytest.mark.unit
def test_chain_json():
    def test():
        # Declare vars
        ref = "test_result"
        args = (1,2,3)
        kwargs = {"test":123123123}

        # Declare test func
        def func(*args, **kwargs):
            return ('test_response', args[1:], kwargs)

        # Initialize ContextChain, Add Step, and Execute
        chain = ContextChain()
        chain.add_step(key='key_1', method=func, args=args, kwargs=kwargs, ref=ref)
        chain.execute()

        # Assert
        assert chain.context['test_result'][0] == 'test_response'
        assert chain.context['test_result'][1] == args
        assert chain.context['test_result'][2] == kwargs
        assert chain.id == ContextChain.model_validate_json(chain.json()).id
    test()