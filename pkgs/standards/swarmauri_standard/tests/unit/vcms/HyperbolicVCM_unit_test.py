import pytest
import os
from swarmauri_standard.vcms.HyperbolicVCM import HyperbolicVCM
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.messages.HumanMessage import HumanMessage
from dotenv import load_dotenv
from swarmauri_standard.utils.timeout_wrapper import timeout

load_dotenv()

API_KEY = os.getenv("HYPERBOLIC_API_KEY")


@pytest.fixture(scope="module")
def hyperbolic_vision_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = HyperbolicVCM(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = HyperbolicVCM(api_key=API_KEY)
    return model.allowed_models


@timeout(5)
@pytest.mark.unit
def test_ubc_resource(hyperbolic_vision_model):
    assert hyperbolic_vision_model.resource == "VCM"


@timeout(5)
@pytest.mark.unit
def test_ubc_type(hyperbolic_vision_model):
    assert hyperbolic_vision_model.type == "HyperbolicVCM"


@timeout(5)
@pytest.mark.unit
def test_serialization(hyperbolic_vision_model):
    assert (
        hyperbolic_vision_model.id
        == HyperbolicVCM.model_validate_json(
            hyperbolic_vision_model.model_dump_json()
        ).id
    )


@timeout(5)
@pytest.mark.unit
def test_default_model_name(hyperbolic_vision_model):
    assert hyperbolic_vision_model.name == "Qwen/Qwen2-VL-72B-Instruct"


def create_test_conversation(image_url, prompt):
    conversation = Conversation()
    conversation.add_message(
        HumanMessage(
            content=[
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ]
        )
    )
    return conversation


@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
def test_predict_vision(hyperbolic_vision_model, model_name):
    model = hyperbolic_vision_model
    model.name = model_name

    image_url = "https://llava-vl.github.io/static/images/monalisa.jpg"
    prompt = "Who painted this artwork?"
    conversation = create_test_conversation(image_url, prompt)

    result = model.predict_vision(conversation)

    assert result.history[-1].content is not None
    assert isinstance(result.history[-1].content, str)
    assert len(result.history[-1].content) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@timeout(5)
@pytest.mark.unit
async def test_apredict_vision(hyperbolic_vision_model, model_name):
    model = hyperbolic_vision_model
    model.name = model_name

    image_url = "https://llava-vl.github.io/static/images/monalisa.jpg"
    prompt = "Describe the woman in the painting."
    conversation = create_test_conversation(image_url, prompt)

    result = await model.apredict_vision(conversation)

    assert result.history[-1].content is not None
    assert isinstance(result.history[-1].content, str)
    assert len(result.history[-1].content) > 0


@timeout(5)
@pytest.mark.unit
def test_batch(hyperbolic_vision_model):
    image_urls = [
        "https://llava-vl.github.io/static/images/monalisa.jpg",
        "https://llava-vl.github.io/static/images/monalisa.jpg",
    ]
    prompts = [
        "Who painted this artwork?",
        "Describe the woman in the painting.",
    ]

    conversations = [
        create_test_conversation(image_url, prompt)
        for image_url, prompt in zip(image_urls, prompts)
    ]

    results = hyperbolic_vision_model.batch(conversations)

    assert len(results) == len(image_urls)
    for result in results:
        assert result.history[-1].content is not None
        assert isinstance(result.history[-1].content, str)
        assert len(result.history[-1].content) > 0


@pytest.mark.asyncio
@timeout(5)
@pytest.mark.unit
async def test_abatch(hyperbolic_vision_model):
    image_urls = [
        "https://llava-vl.github.io/static/images/monalisa.jpg",
        "https://llava-vl.github.io/static/images/monalisa.jpg",
    ]
    prompts = [
        "Who painted this artwork?",
        "Describe the woman in the painting.",
    ]

    conversations = [
        create_test_conversation(image_url, prompt)
        for image_url, prompt in zip(image_urls, prompts)
    ]

    results = await hyperbolic_vision_model.abatch(conversations)

    assert len(results) == len(image_urls)
    for result in results:
        assert result.history[-1].content is not None
        assert isinstance(result.history[-1].content, str)
        assert len(result.history[-1].content) > 0
