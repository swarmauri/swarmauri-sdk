import logging

import pytest
import os
from swarmauri.llms.concrete.GroqToolModel import GroqToolModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete import HumanMessage
from swarmauri.tools.concrete.AdditionTool import AdditionTool
from swarmauri.toolkits.concrete.Toolkit import Toolkit
from swarmauri.agents.concrete.ToolAgent import ToolAgent
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def groq_tool_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def toolkit():
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)

    return toolkit


@pytest.fixture(scope="module")
def conversation():
    conversation = Conversation()

    input_data = "Add 512+671"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    return conversation


@pytest.mark.unit
def test_ubc_resource(groq_tool_model):
    assert groq_tool_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(groq_tool_model):
    assert groq_tool_model.type == "GroqToolModel"


@pytest.mark.unit
def test_serialization(groq_tool_model):
    assert (
        groq_tool_model.id
        == LLM.model_validate_json(groq_tool_model.model_dump_json()).id
    )


@pytest.mark.unit
def test_default_name(groq_tool_model):
    assert groq_tool_model.name == "llama3-groq-70b-8192-tool-use-preview"


@pytest.mark.unit
def test_agent_exec(groq_tool_model, toolkit, conversation):
    # Use groq_tool_model from the fixture
    agent = ToolAgent(llm=groq_tool_model, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")
    assert type(result) == str


@pytest.mark.unit
def test_predict(groq_tool_model, toolkit, conversation):

    conversation = groq_tool_model.predict(conversation=conversation, toolkit=toolkit)
    logging.info(conversation.get_last().content)

    assert type(conversation.get_last().content) == str


@pytest.mark.unit
def test_stream(groq_tool_model, toolkit, conversation):
    collected_tokens = []
    for token in groq_tool_model.stream(conversation=conversation, toolkit=toolkit):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.unit
def test_batch(groq_tool_model, toolkit):

    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = groq_tool_model.batch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
async def test_apredict(groq_tool_model, toolkit, conversation):

    result = await groq_tool_model.apredict(conversation=conversation, toolkit=toolkit)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
async def test_astream(groq_tool_model, toolkit, conversation):

    collected_tokens = []
    async for token in groq_tool_model.astream(
        conversation=conversation, toolkit=toolkit
    ):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@pytest.mark.unit
@pytest.mark.asyncio(loop_scope="session")
async def test_abatch(groq_tool_model, toolkit):
    conversations = []
    for prompt in ["20+20", "100+50", "500+500"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await groq_tool_model.abatch(conversations=conversations, toolkit=toolkit)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
