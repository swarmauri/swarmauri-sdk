import logging
import os

import pytest
from dotenv import load_dotenv

from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.LLM import LLM
from swarmauri_standard.messages.HumanMessage import HumanMessage
from swarmauri_standard.utils.timeout_wrapper import timeout

load_dotenv()

# API keys for different providers
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

BASE_URL_CONFIG = [
    (
        "OPENAI",
        "https://api.openai.com/v1/chat/completions",
        OPENAI_API_KEY,
        "gpt-3.5-turbo",
    ),
    (
        "Groq",
        "https://api.groq.com/openai/v1/chat/completions",
        GROQ_API_KEY,
        "llama3-8b-8192",
    ),
    (
        "Anthropic",
        "https://api.anthropic.com/v1/messages",
        ANTHROPIC_API_KEY,
        "claude-3-haiku-20240307",
    ),
]

# Filter out configurations with missing API keys
VALID_CONFIGS = [
    (name, url, key, model) for name, url, key, model in BASE_URL_CONFIG if key
]


@pytest.fixture(scope="module", params=VALID_CONFIGS)
def llm_config(request):
    """Fixture that provides different LLM configurations based on provider."""
    provider_name, base_url, api_key, default_model = request.param

    # Skip if API key is not available
    if not api_key:
        pytest.skip(f"Skipping {provider_name} tests due to missing API key")

    llm = LLM(
        api_key=api_key,
        BASE_URL=base_url,
        name=default_model,
        allowed_models=["gpt-3.5-turbo", "llama3-8b-8192", "claude-3-haiku-20240307"],
    )

    return {
        "llm": llm,
        "provider": provider_name,
        "base_url": base_url,
        "model": default_model,
    }


@pytest.fixture(scope="module")
def conversation():
    """Fixture that provides a conversation with an initial human message."""
    conversation = Conversation()
    input_data = "What is the capital of France?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)
    return conversation


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(llm_config):
    assert llm_config["llm"].resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(llm_config):
    assert llm_config["llm"].type == "LLM"


@timeout(5)
@pytest.mark.unit
def test_serialization(llm_config):
    llm = llm_config["llm"]
    assert llm.id == LLM.model_validate_json(llm.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_base_url(llm_config):
    """Test that the BASE_URL is correctly set."""
    assert llm_config["llm"].BASE_URL == llm_config["base_url"]


@timeout(5)
@pytest.mark.unit
def test_allowed_models(llm_config):
    """Test that allowed_models are correctly populated."""
    llm = llm_config["llm"]
    assert len(llm.allowed_models) > 0
    assert llm.name in llm.allowed_models


@timeout(5)
@pytest.mark.unit
def test_format_messages(llm_config, conversation):
    """Test message formatting function."""
    llm = llm_config["llm"]
    formatted = llm._format_messages(conversation.history)

    assert isinstance(formatted, list)
    assert len(formatted) == len(conversation.history)
    assert "content" in formatted[0]
    assert "role" in formatted[0]


@timeout(15)
@pytest.mark.unit
def test_predict(llm_config, conversation):
    """Test the predict method with different providers."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    logging.info(f"Testing predict with provider: {provider}")

    result_conv = llm.predict(conversation=conversation.model_copy())
    response = result_conv.get_last().content

    logging.info(f"Provider {provider} response: {response}")
    assert isinstance(response, str)
    assert "Paris" in response, f"Expected 'Paris' in response from {provider}"


@timeout(15)
@pytest.mark.unit
def test_stream(llm_config, conversation):
    """Test the stream method with different providers."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    logging.info(f"Testing stream with provider: {provider}")

    collected_tokens = []
    for token in llm.stream(conversation=conversation.model_copy()):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0, f"Got empty stream response from {provider}"
    assert "Paris" in full_response, (
        f"Expected 'Paris' in stream response from {provider}"
    )


@timeout(15)
@pytest.mark.unit
def test_batch(llm_config):
    """Test the batch method with different providers."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    logging.info(f"Testing batch with provider: {provider}")

    conversations = []
    prompts = [
        "What is the capital of France?",
        "What is the capital of Italy?",
        "What is the capital of Germany?",
    ]
    expected_answers = ["Paris", "Rome", "Berlin"]

    for prompt in prompts:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = llm.batch(conversations=conversations)

    assert len(results) == len(conversations)
    for i, result in enumerate(results):
        response = result.get_last().content
        assert isinstance(response, str)
        assert expected_answers[i] in response, (
            f"Expected {expected_answers[i]} in batch response #{i + 1} from {provider}"
        )
        logging.info(
            f"Provider {provider}, prompt '{prompts[i]}', response: {response}"
        )


@timeout(15)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_apredict(llm_config, conversation):
    """Test async prediction with different providers."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    logging.info(f"Testing apredict with provider: {provider}")

    result = await llm.apredict(conversation=conversation.model_copy())
    prediction = result.get_last().content

    assert isinstance(prediction, str)
    assert "Paris" in prediction, f"Expected 'Paris' in async response from {provider}"
    logging.info(f"Provider {provider} async response: {prediction}")


@timeout(15)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_astream(llm_config, conversation):
    """Test async streaming with different providers."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    logging.info(f"Testing astream with provider: {provider}")

    collected_tokens = []
    async for token in llm.astream(conversation=conversation.model_copy()):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0, f"Got empty async stream from {provider}"
    assert "Paris" in full_response, f"Expected 'Paris' in async stream from {provider}"


@timeout(20)
@pytest.mark.unit
@pytest.mark.asyncio
async def test_abatch(llm_config):
    """Test async batch processing with different providers."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    logging.info(f"Testing abatch with provider: {provider}")

    conversations = []
    prompts = [
        "What is the capital of France?",
        "What is the capital of Italy?",
        "What is the capital of Germany?",
    ]
    expected_answers = ["Paris", "Rome", "Berlin"]

    for prompt in prompts:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await llm.abatch(conversations=conversations)

    assert len(results) == len(conversations)
    for i, result in enumerate(results):
        response = result.get_last().content
        assert isinstance(response, str)
        assert expected_answers[i] in response, (
            f"Expected {expected_answers[i]} in async batch response #{i + 1} from {provider}"
        )


@timeout(5)
@pytest.mark.unit
def test_usage_data(llm_config, conversation):
    """Test that usage data is correctly returned."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    # Ensure usage data is included
    llm.include_usage = True

    result_conv = llm.predict(conversation=conversation.model_copy())
    last_message = result_conv.get_last()

    assert hasattr(last_message, "usage")
    usage = last_message.usage
    assert usage is not None

    # Check that usage data contains expected fields
    assert hasattr(usage, "prompt_tokens")
    assert hasattr(usage, "completion_tokens")
    assert hasattr(usage, "total_tokens")
    assert hasattr(usage, "prompt_time")

    logging.info(f"Provider {provider} usage data: {usage}")


@timeout(5)
@pytest.mark.unit
def test_json_response_format(llm_config):
    """Test that JSON response format works correctly."""
    llm = llm_config["llm"]
    provider = llm_config["provider"]

    # Skip this test for providers that don't support JSON response format
    if provider == "Anthropic":
        pytest.skip("Anthropic doesn't support JSON response format in the same way")

    conv = Conversation()
    conv.add_message(
        HumanMessage(
            content="Return a JSON object with keys 'name' and 'capital' for France"
        )
    )

    result_conv = llm.predict(conv, enable_json=True)
    response = result_conv.get_last().content

    assert "{" in response and "}" in response, (
        f"Expected JSON response from {provider}"
    )
    assert "name" in response.lower(), (
        f"Expected 'name' key in JSON response from {provider}"
    )
    assert "capital" in response.lower(), (
        f"Expected 'capital' key in JSON response from {provider}"
    )
    assert "france" in response.lower(), (
        f"Expected 'France' in JSON response from {provider}"
    )
    assert "paris" in response.lower(), (
        f"Expected 'Paris' in JSON response from {provider}"
    )


@timeout(5)
@pytest.mark.unit
def test_add_remove_allowed_models(llm_config):
    """Test adding and removing allowed models."""
    llm = llm_config["llm"]

    # Add a new model
    new_model = "test-model-123"
    llm.add_allowed_model(new_model)
    assert new_model in llm.allowed_models

    # Try adding the same model (should raise ValueError)
    with pytest.raises(ValueError):
        llm.add_allowed_model(new_model)

    # Remove the model
    llm.remove_allowed_model(new_model)
    assert new_model not in llm.allowed_models

    # Try removing a model that doesn't exist (should raise ValueError)
    with pytest.raises(ValueError):
        llm.remove_allowed_model(new_model)
