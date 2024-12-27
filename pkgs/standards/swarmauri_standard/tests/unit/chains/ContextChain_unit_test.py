import pytest
from pydantic import BaseModel
from swarmauri.chains.concrete.ContextChain import ContextChain
from swarmauri.tools.concrete.AdditionTool import AdditionTool


@pytest.mark.unit
def test_ubc_resource():
    # declare chain, args, kwargs
    chain = ContextChain()
    assert chain.resource == "Chain"


@pytest.mark.unit
def test_ubc_type():
    chain = ContextChain()
    assert chain.type == "ContextChain"


@pytest.mark.unit
def test_chain_execute_return_value():
    # declare chain, args, kwargs
    chain = ContextChain()
    ref = "test_result"
    args = (1, 2)
    kwargs = {}

    tool = AdditionTool()

    # operate
    chain.add_step(key="key_1", method=tool, args=args, kwargs=kwargs, ref=ref)
    result = chain.execute()

    # assert
    assert isinstance(result, dict)
    assert "test_result" in result
    assert result["test_result"] == {"sum": "3"}


@pytest.mark.unit
def test_chain_execute_return_state():
    # declare chain, args, kwargs
    chain = ContextChain()
    ref = "test_result"
    args = (1, 2)
    kwargs = {}

    tool = AdditionTool()
    chain.add_step(key="key_1", method=tool, args=args, kwargs=kwargs, ref=ref)
    chain.execute()

    # assert
    assert "test_result" in chain.context
    assert chain.context["test_result"] == {"sum": "3"}


@pytest.mark.unit
def test_serialization():
    # Declare vars
    ref = "test_result"
    args = (1, 2)
    kwargs = {}

    tool = AdditionTool(name="AdditionTool")

    # Initialize ContextChain, Add Step, and Execute
    chain = ContextChain()
    chain.add_step(key="key_1", method=tool, args=args, kwargs=kwargs, ref=ref)
    chain.execute()

    # Assert
    assert "test_result" in chain.context
    assert chain.context["test_result"] == {"sum": "3"}
