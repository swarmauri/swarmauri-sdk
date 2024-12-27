import pytest
import os
from swarmauri.llms.concrete.GroqVisionModel import GroqVisionModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from dotenv import load_dotenv

from swarmauri.messages.concrete.AgentMessage import UsageData
from swarmauri.utils.timeout_wrapper import timeout


load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"


@pytest.fixture(scope="module")
def groq_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def input_data():
    return [
        {"type": "text", "text": "What’s in this image?"},
        {
            "type": "image_url",
            "image_url": {
                "url": f"{image_url}",
            },
        },
    ]


@timeout(5)
def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)

    allowed_models = [model for model in llm.allowed_models]

    return allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(groq_model):
    assert groq_model.resource == "LLM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(groq_model):
    assert groq_model.type == "GroqVisionModel"


@timeout(5)
@pytest.mark.unit
def test_serialization(groq_model):
    assert groq_model.id == LLM.model_validate_json(groq_model.model_dump_json()).id


@timeout(5)
@pytest.mark.unit
def test_default_name(groq_model):
    assert groq_model.name == "llama-3.2-11b-vision-preview"


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_predict(groq_model, model_name, input_data):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    usage_data = conversation.get_last().usage
    assert type(prediction) is str
    assert isinstance(usage_data, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_stream(groq_model, model_name, input_data):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    for token in model.stream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_batch(groq_model, model_name, input_data):
    model = groq_model
    model.name = model_name

    conversations = []
    conv = Conversation()
    conv.add_message(HumanMessage(content=input_data))
    conversations.append(conv)

    results = model.batch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
        assert isinstance(result.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_apredict(groq_model, model_name, input_data):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    result = await model.apredict(conversation=conversation)
    prediction = result.get_last().content
    assert isinstance(prediction, str)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_astream(groq_model, model_name, input_data):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    collected_tokens = []
    async for token in model.astream(conversation=conversation):
        assert isinstance(token, str)
        collected_tokens.append(token)

    full_response = "".join(collected_tokens)
    assert len(full_response) > 0
    assert conversation.get_last().content == full_response
    # assert isinstance(conversation.get_last().usage, UsageData)


@timeout(5)
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio(loop_scope="session")
@pytest.mark.unit
async def test_abatch(groq_model, model_name, input_data):
    model = groq_model
    model.name = model_name

    conversations = []
    conv = Conversation()
    conv.add_message(HumanMessage(content=input_data))
    conversations.append(conv)

    results = await model.abatch(conversations=conversations)
    assert len(results) == len(conversations)
    for result in results:
        assert isinstance(result.get_last().content, str)
        assert isinstance(result.get_last().usage, UsageData)
