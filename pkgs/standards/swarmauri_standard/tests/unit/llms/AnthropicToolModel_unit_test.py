import logging
import pytest
import os
from swarmauri.llms.concrete.AnthropicToolModel import AnthropicToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete import HumanMessage
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent
from dotenv import load_dotenv
from swarmauri.utils.timeout_wrapper import timeout


load_dotenv()

API_KEY = os.getenv("ANTHROPIC_API_KEY")


@pytest.fixture(scope="module")
def anthropic_tool_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)

    failing_llms = ["claude-3-haiku-20240307", "claude-3-5-sonnet-20240620"]

    allowed_models = [
        model for model in llm.allowed_models if model not in failing_llms
    ]

    return allowed_models


@pytest.fixture(scope="module")
def toolkit():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)
    return toolkit


@pytest.fixture(scope="module")
def conversation():
    conversation = Conversation()
    input_data = {"type": "text", "text": "Add 512+671"}
    human_message = HumanMessage(content=[input_data])
    conversation.add_message(human_message)
    return conversation


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(anthropic_tool_model):
    assert anthropic_tool_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(anthropic_tool_model):
    assert anthropic_tool_model.type == "AnthropicToolModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(anthropic_tool_model):
    assert (
        anthropic_tool_model.id
        == LLM.model_validate_json(anthropic_tool_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(anthropic_tool_model):
    assert anthropic_tool_model.name == "claude-3-sonnet-20240229"


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_agent_exec(anthropic_tool_model, toolkit, conversation, model_name):
    anthropic_tool_model.name = model_name
    agent = ToolAgent(
        llm=anthropic_tool_model, conversation=conversation, toolkit=toolkit
    )
    result = agent.exec("Add 512+671")
    assert isinstance(result, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_predict(anthropic_tool_model, toolkit, conversation, model_name):
    anthropic_tool_model.name = model_name
    conversation = anthropic_tool_model.predict(
        conversation=conversation, toolkit=toolkit
    )
    logging.info(conversation.get_last().content)
    assert isinstance(conversation.get_last().content, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.parametrize("model_name", get_allowed_models())
def test_batch(anthropic_tool_model, toolkit, model_name):
    anthropic_tool_model.name = model_name
    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=[{"type": "text", "text": prompt}]))
        conversations.append(conv)
    results = anthropic_tool_model.batch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_apredict(anthropic_tool_model, toolkit, conversation, model_name):
    anthropic_tool_model.name = model_name
    result = await anthropic_tool_model.apredict(
        conversation=conversation, toolkit=toolkit
    )
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@timeout(5)
@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
async def test_abatch(anthropic_tool_model, toolkit, model_name):
    anthropic_tool_model.name = model_name
    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=[{"type": "text", "text": prompt}]))
        conversations.append(conv)
    results = await anthropic_tool_model.abatch(
        conversations=conversations, toolkit=toolkit
    )
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
