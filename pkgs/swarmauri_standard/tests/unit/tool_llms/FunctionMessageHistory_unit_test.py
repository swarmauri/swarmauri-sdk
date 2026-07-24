import pytest

from swarmauri_standard.messages.AgentMessage import AgentMessage
from swarmauri_standard.messages.FunctionMessage import FunctionMessage
from swarmauri_standard.tool_llms.GeminiToolModel import GeminiToolModel
from swarmauri_standard.tool_llms.ToolLLM import ToolLLM
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.AdditionTool import AdditionTool


@pytest.mark.unit
def test_tool_results_become_function_messages():
    model = ToolLLM(
        api_key="test-key",
        name="test-model",
        allowed_models=["test-model"],
    )
    toolkit = Toolkit()
    toolkit.add_tool(AdditionTool())
    tool_calls = [
        {
            "id": "call-1",
            "function": {
                "name": "AdditionTool",
                "arguments": '{"x": 1, "y": 2}',
            },
        }
    ]

    provider_messages = model._process_tool_calls(tool_calls, toolkit, [])
    function_messages = model._get_function_messages(provider_messages)

    assert len(function_messages) == 1
    assert isinstance(function_messages[0], FunctionMessage)
    assert function_messages[0].name == "AdditionTool"
    assert function_messages[0].content == '{"sum": "3"}'
    assert function_messages[0].tool_call_id == "call-1"


@pytest.mark.unit
def test_openai_compatible_history_keeps_tool_call_and_result_together():
    model = ToolLLM(
        api_key="test-key",
        name="test-model",
        allowed_models=["test-model"],
    )
    tool_calls = [{"id": "call-1", "function": {"name": "AdditionTool"}}]

    formatted_messages = model._format_messages(
        [
            AgentMessage(content=None, tool_calls=tool_calls),
            FunctionMessage(
                name="AdditionTool",
                content='{"sum": "3"}',
                tool_call_id="call-1",
            ),
        ]
    )

    assert formatted_messages[0]["tool_calls"] == tool_calls
    assert formatted_messages[1]["role"] == "tool"
    assert formatted_messages[1]["tool_call_id"] == "call-1"


@pytest.mark.unit
def test_gemini_tool_results_receive_a_correlation_id():
    model = GeminiToolModel(api_key="test-key")
    toolkit = Toolkit()
    toolkit.add_tool(AdditionTool())

    _, function_messages = model._process_tool_calls(
        [
            {
                "functionCall": {
                    "name": "AdditionTool",
                    "args": {"x": 1, "y": 2},
                }
            }
        ],
        toolkit,
        [],
    )

    assert len(function_messages) == 1
    assert function_messages[0].tool_call_id.startswith("gemini-")
