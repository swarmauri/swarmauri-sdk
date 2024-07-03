import pytest
from pydantic import BaseModel
from swarmauri.standard.chains.concrete.ContextChain import ContextChain
from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool

@pytest.mark.unit
def test_ubc_resource():
    # declare chain, args, kwargs
    chain = ContextChain()
    assert chain.resource == 'Chain'

@pytest.mark.unit
def test_ubc_type():
    chain = ContextChain()
    assert chain.type == 'ContextChain'

@pytest.mark.unit
def test_chain_execute_return_value():
    # declare chain, args, kwargs
    chain = ContextChain()
    ref = "test_result"
    args = (1,2)
    kwargs = {}

    tool = AdditionTool()

    # operate
    chain.add_step(key='key_1', method=tool, args=args, kwargs=kwargs, ref="test_result")
    result = chain.execute()
    
    # assert
    assert result['test_result'] == '3'

@pytest.mark.unit
def test_chain_execute_return_state():
    # declare chain, args, kwargs
    chain = ContextChain()
    ref = "test_result"
    args = (1,2)
    kwargs = {}

    tool = AdditionTool()
    chain.add_step(key='key_1', method=tool, args=args, kwargs=kwargs, ref=ref)
    chain.execute()
    assert chain.context['test_result'] == '3'


@pytest.mark.unit
def test_serialization():
    # Declare vars
    ref = "test_result"
    args = (1,2)
    kwargs = {}

    tool = AdditionTool(name='AdditionTool')

    # Initialize ContextChain, Add Step, and Execute
    chain = ContextChain()
    chain.add_step(key='key_1', method=tool, args=args, kwargs=kwargs, ref=ref)
    chain.execute()

    # Assert
    assert chain.context['test_result'] == '3'
    assert chain.id == ContextChain.model_validate_json(chain.model_dump_json()).id