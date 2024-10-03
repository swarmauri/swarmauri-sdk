import pytest
from swarmauri.chains.concrete.ChainStep import ChainStep
from swarmauri.tools.concrete import AdditionTool


@pytest.mark.unit
def test_ubc_resource():
    tool = AdditionTool()
    step = ChainStep(key="test", method=tool, args=(1, 2), kwargs={}, ref=None)
    assert step.resource == "ChainStep"


@pytest.mark.unit
def test_ubc_type():
    tool = AdditionTool()
    step = ChainStep(key="test", method=tool, args=(1, 2), kwargs={}, ref=None)
    assert step.type == "ChainStep"


@pytest.mark.unit
def test_method_args_only_call():
    tool = AdditionTool()
    args = (1, 2)
    kwargs = {}
    step = ChainStep(key="test", method=tool, args=args, kwargs=kwargs, ref=None)
    result = step.method(*step.args, **step.kwargs)

    assert isinstance(result, dict)
    assert "sum" in result
    assert result["sum"] == "3"


@pytest.mark.unit
def test_serialization():
    tool = AdditionTool()
    args = (1, 2)
    kwargs = {}
    step = ChainStep(key="test", method=tool, args=args, kwargs=kwargs, ref=None)

    # Serialize and deserialize
    serialized_step = step.model_dump_json()
    deserialized_step = ChainStep.model_validate_json(serialized_step)

    # Assert that the method (tool) remains the same after serialization and deserialization
    assert isinstance(deserialized_step.method, AdditionTool)
