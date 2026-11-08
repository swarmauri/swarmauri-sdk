import pytest
from swarmauri_tool_askuser import AskUserTool


@pytest.mark.unit
def test_standalone_answer():
    tool = AskUserTool(input_handler=lambda question: question.choices[0])
    assert tool("Which package?", choices=["core"]).answer == "core"
