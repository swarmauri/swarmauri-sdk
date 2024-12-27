import pytest
import os
from swarmauri.llms.concrete.DeepInfraModel import DeepInfraModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("DEEPINFRA_API_KEY")


@pytest.fixture(scope="module")
def deepinfra_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)

    # not consistent with their results
    failing_llms = [
        "Gryphe/MythoMax-L2-13b",
        "lizpreciatior/lzlv_70b_fp16_hf",
        "openchat/openchat_3.5",
    ]

    # Filter out the failing models
    allowed_models = [
        model for model in llm.allowed_models if model not in failing_llms
    ]

    return allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(deepinfra_model):
    assert deepinfra_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(deepinfra_model):
    assert deepinfra_model.type == "DeepInfraModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(deepinfra_model):
    assert (
        deepinfra_model.id
        == LLM.model_validate_json(deepinfra_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(deepinfra_model):
    assert deepinfra_model.name == "Qwen/Qwen2-72B-Instruct"


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_no_system_context(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation, **{"temperature": 0})
    prediction = conversation.get_last().content
    assert type(prediction) is str


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_preamble_system_context(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation, **{"temperature": 0})
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert "Jeff" in prediction


# New tests for streaming
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_stream(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Write a short story about a cat."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    for token in model.stream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


# New tests for async operations
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_apredict(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_astream(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name
    conversation = Conversation()

    input_data = "Write a short story about a dog."
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    async for token in model.astream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


# New tests for batch operations
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_batch(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name

    conversations = []
    for prompt in ["Hello", "Hi there", "Good morning"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = model.batch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)


@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_abatch(deepinfra_model, model_name):
    model = deepinfra_model
    model.name = model_name

    conversations = []
    for prompt in ["Hello", "Hi there", "Good morning"]:
        conv = Conversation()
        conv.add_message(HumanMessage(content=prompt))
        conversations.append(conv)

    results = await model.abatch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
