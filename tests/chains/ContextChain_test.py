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
        def func(*args, **kwargs):
            return ('test_response', args, kwargs)

        chain = ContextChain()
        chain.add_step(key='key_1', method=func, args=[1,2,3], kwargs={"test":123123123}, ref="test_result")
        result = chain.execute()
        assert result[0] == 'test_response'
        assert result[1] == [1,2,3]
        assert result[2] == {"test":123123123}
    test()

@pytest.mark.unit
def test_chain_execute_state():
    def test():
        ref = "test_result"
        args = [1,2,3]
        kwargs = {"test":123123123}
        def func(*args, **kwargs):
            return ('test_response', args, kwargs)

        chain = ContextChain()
        chain.add_step(key='key_1', method=func, args=args, kwargs=kwargs, ref=ref)
        chain.execute()
        assert chain.context['test_result'] == 'test_response'
        assert chain.context['test_result'] == args
        assert chain.context['test_result'] == kwargs
    test()

@pytest.mark.unit
def test_chain_json():
    def test():
        ref = "test_result"
        args = [1,2,3]
        kwargs = {"test":123123123}

        # Importing BaseModel makes the function serializable by pydantic
        class func(BaseModel):
            def __call__(*args, **kwargs):
                return ('test_response', args, kwargs)

        chain = ContextChain()
        # We must initialize the class
        chain.add_step(key='key_1', method=func(), args=args, kwargs=kwargs, ref=ref)
        chain.execute()
        assert chain.context['test_result'] == 'test_response'
        assert chain.context['test_result'] == args
        assert chain.context['test_result'] == kwargs
        assert chain.id == ContextChain.parse_raw(chain.json()).id
    test()