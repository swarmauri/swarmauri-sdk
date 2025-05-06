import pytest

from swarmauri_standard.chains.ChainStep import ChainStep
from swarmauri_standard.tools.AdditionTool import AdditionTool


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

    tool_from_dict = AdditionTool.model_validate(deserialized_step.method)

    assert isinstance(tool_from_dict, AdditionTool)

    result = tool_from_dict(*args, **kwargs)
    assert result["sum"] == "3"
