import logging
import os

import pytest
from dotenv import load_dotenv

from swarmauri_standard.agents.ToolAgent import ToolAgent
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.tool_llms.ToolLLM import ToolLLM as LLM
from swarmauri_standard.toolkits.Toolkit import Toolkit
from swarmauri_standard.tools.AdditionTool import AdditionTool
from swarmauri_standard.utils.timeout_wrapper import timeout

load_dotenv()

# API keys for different providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

BASE_URL_CONFIG = [
    (
        "OPENAI",
        "https://api.openai.com/v1/chat/completions",
        OPENAI_API_KEY,
        "gpt-4o",
    ),
    (
        "Groq",
        "https://api.groq.com/openai/v1/chat/completions",
        GROQ_API_KEY,
        "qwen-2.5-32b",
    ),
    (
        "Mistral",
        "https://api.mistral.ai/v1/chat/completions",
        MISTRAL_API_KEY,
        "mistral-large-latest",
    ),
]

# Filter out configurations with missing API keys
VALID_CONFIGS = [
    (name, url, key, model) for name, url, key, model in BASE_URL_CONFIG if key
]


@pytest.fixture(scope="module", params=VALID_CONFIGS)
def tool_llm_config(request):
    """Fixture that provides different LLM configurations based on provider."""
    provider_name, base_url, api_key, default_model = request.param

    # Skip if API key is not available
    if not api_key:
        pytest.skip(f"Skipping {provider_name} tests due to missing API key")

    llm = LLM(
        api_key=api_key,
        BASE_URL=base_url,
        name=default_model,
        allowed_models=["mistral-large-latest", "gpt-4o", "qwen-2.5-32b"],
    )

    return {
        "llm": llm,
        "provider": provider_name,
        "base_url": base_url,
        "model": default_model,
    }


@pytest.fixture(scope="module")
def toolkit():
    """Fixture that provides a toolkit with an addition tool."""
    toolkit = Toolkit()
    tool = AdditionTool()
    toolkit.add_tool(tool)
    return toolkit


@pytest.fixture(scope="module")
def conversation():
    """Fixture that provides a conversation with an initial human message."""
    conversation = Conversation()
    input_data = "what will the sum of 512 boys and 671 boys"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)
    return conversation


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(tool_llm_config):
    assert tool_llm_config["llm"].resource == "ToolLLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(tool_llm_config):
    assert tool_llm_config["llm"].type == "ToolLLM"


@timeout(5)
@pytest.mark.unit
def test_serialization(tool_llm_config):
    llm = tool_llm_config["llm"]
    assert llm.id == LLM.model_validate_json(llm.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_base_url(tool_llm_config):
    """Test that the BASE_URL is correctly set."""
    assert tool_llm_config["llm"].BASE_URL == tool_llm_config["base_url"]


@timeout(15)
@pytest.mark.unit
def test_agent_exec(tool_llm_config, toolkit, conversation):
    """Test that the agent can execute a tool-using task."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing agent_exec with provider: {provider}")

    agent = ToolAgent(llm=llm, conversation=conversation, toolkit=toolkit)
    result = agent.exec("Add 512+671")

    assert isinstance(result, str)
    assert "1183" in result, (
        f"Expected '1183' in response from {provider}, got: {result}"
    )


@timeout(15)
@pytest.mark.unit
def test_predict(tool_llm_config, toolkit, conversation):
    """Test the predict method with different providers."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing predict with provider: {provider}")

    result_conv = llm.predict(conversation=conversation.model_copy(), toolkit=toolkit)
    response = result_conv.get_last().content

    logging.info(f"Provider {provider} response: {response}")
    assert isinstance(response, str)
    assert response != "", f"Got empty response from {provider}"


@timeout(15)
@pytest.mark.unit
def test_stream(tool_llm_config, toolkit, conversation):
    """Test the stream method with different providers."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing stream with provider: {provider}")

    collected_tokens = []
    for token in llm.stream(conversation=conversation.model_copy(), toolkit=toolkit):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0, f"Got empty stream response from {provider}"


@timeout(15)
@pytest.mark.unit
def test_batch(tool_llm_config, toolkit):
    """Test the batch method with different providers."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing batch with provider: {provider}")

    conversations = []
    prompts = ["what is 20+20?", "what is 100+50?", "calculate 500+500"]

    for prompt in prompts:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = llm.batch(conversations=conversations, toolkit=toolkit)

    assert len(results) == len(conversations)
    for i, result in enumerate(results):
        response = result.get_last().content
        assert isinstance(response, str)
        assert response != "", f"Empty batch response #{i + 1} from {provider}"
        logging.info(
            f"Provider {provider}, prompt '{prompts[i]}', response: {response}"
        )


@timeout(15)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_apredict(tool_llm_config, toolkit, conversation):
    """Test async prediction with different providers."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing apredict with provider: {provider}")

    result = await llm.apredict(conversation=conversation.model_copy(), toolkit=toolkit)
    prediction = result.get_last().content

    assert isinstance(prediction, str)
    assert prediction != "", f"Got empty async response from {provider}"
    logging.info(f"Provider {provider} async response: {prediction}")


@timeout(15)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_astream(tool_llm_config, toolkit, conversation):
    """Test async streaming with different providers."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing astream with provider: {provider}")

    collected_tokens = []
    async for token in llm.astream(conversation=conversation.model_copy(), toolkit=toolkit):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0, f"Got empty async stream from {provider}"


@timeout(20)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_abatch(tool_llm_config, toolkit):
    """Test async batch processing with different providers."""
    llm = tool_llm_config["llm"]
    provider = tool_llm_config["provider"]

    logging.info(f"Testing abatch with provider: {provider}")

    conversations = []
    prompts = ["what is 20+20?", "what is 100+50?", "calculate 500+500"]

    for prompt in prompts:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await llm.abatch(conversations=conversations, toolkit=toolkit)

    assert len(results) == len(conversations)
    for i, result in enumerate(results):
        response = result.get_last().content
        assert isinstance(response, str)
        assert response != "", f"Empty async batch response #{i + 1} from {provider}"
