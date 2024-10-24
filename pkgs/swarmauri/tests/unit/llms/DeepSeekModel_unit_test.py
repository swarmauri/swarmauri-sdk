import pytest
import os
from swarmauri.llms.concrete.DeepSeekModel import DeepSeekModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

from swarmauri.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("DEEPSEEK_API_KEY")


@pytest.fixture(scope="module")
def deepseek_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)
    return llm.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(deepseek_model):
    assert deepseek_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(deepseek_model):
    assert deepseek_model.type == "DeepSeekModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(deepseek_model):
    assert (
        deepseek_model.id
        == LLM.model_validate_json(deepseek_model.model_dump_json()).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_name(deepseek_model):
    assert deepseek_model.name == "deepseek-chat"


@timeout(5)
@pytest.mark.unit
def test_no_system_context(deepseek_model):
    model = deepseek_model
    conversation = Conversation()

    input_data = "Hello"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str


@timeout(5)
@pytest.mark.unit
def test_preamble_system_context(deepseek_model):
    model = deepseek_model
    conversation = Conversation()

    system_context = "Jane knows Martin."
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Who does Jane know?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert type(prediction) == str
    assert "martin" in prediction.lower()


# New tests for streaming
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_stream(deepseek_model, model_name):
    model = deepseek_model
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
async def test_apredict(deepseek_model, model_name):
    model = deepseek_model
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
async def test_astream(deepseek_model, model_name):
    model = deepseek_model
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
def test_batch(deepseek_model, model_name):
    model = deepseek_model
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
async def test_abatch(deepseek_model, model_name):
    model = deepseek_model
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
