import os

import pytest
from dotenv import load_dotenv
from swarmauri_standard.conversations.Conversation import Conversation
from swarmauri_standard.llms.HyperbolicVisionModel import HyperbolicVisionModel
from swarmauri_standard.messages.HumanMessage import HumanMessage


load_dotenv()

API_KEY = os.getenv("HYPERBOLIC_API_KEY")


@pytest.fixture(scope="module")
def hyperbolic_vision_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = HyperbolicVisionModel(api_key=API_KEY)
    return model


def get_allowed_models():
    if not API_KEY:
        return []
    model = HyperbolicVisionModel(api_key=API_KEY)
    return model.allowed_models


@pytest.fixture(scope="module")
def conversation():
    image_url = "https://llava-vl.github.io/static/images/monalisa.jpg"
    prompt = "Who painted this artwork?"

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


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_ubc_resource(hyperbolic_vision_model):
    assert hyperbolic_vision_model.resource == "LLM"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_ubc_type(hyperbolic_vision_model):
    assert hyperbolic_vision_model.type == "HyperbolicVisionModel"


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_serialization(hyperbolic_vision_model):
    assert (
        hyperbolic_vision_model.id
        == HyperbolicVisionModel.model_validate_json(
            hyperbolic_vision_model.model_dump_json()
        ).id
    )


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_default_model_name(hyperbolic_vision_model):
    assert hyperbolic_vision_model.name == hyperbolic_vision_model.allowed_models[0]


@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.timeout(5)
@pytest.mark.unit
def test_predict(hyperbolic_vision_model, model_name, conversation):
    model = hyperbolic_vision_model
    model.name = model_name

    result = model.predict(conversation)

    assert result.history[-1].content is not None
    assert isinstance(result.history[-1].content, str)
    assert len(result.history[-1].content) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.timeout(5)
@pytest.mark.unit
async def test_apredict(hyperbolic_vision_model, model_name, conversation):
    model = hyperbolic_vision_model
    model.name = model_name

    result = await model.apredict(conversation)

    assert result.history[-1].content is not None
    assert isinstance(result.history[-1].content, str)
    assert len(result.history[-1].content) > 0


@pytest.mark.timeout(5)
@pytest.mark.unit
def test_batch(hyperbolic_vision_model):
    image_prompt = {
        "Who painted this artwork?": "https://llava-vl.github.io/static/images/monalisa.jpg",
        "Describe the woman in the painting.": "https://llava-vl.github.io/static/images/monalisa.jpg",
    }
    conversations = []
    for prompt, image_url in image_prompt.items():
        conversation = Conversation()
        conversation.add_message(
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
        )
        conversations.append(conversation)

    results = hyperbolic_vision_model.batch(conversations)

    assert len(results) == len(image_prompt.keys())
    for result in results:
        assert result.history[-1].content is not None
        assert isinstance(result.history[-1].content, str)
        assert len(result.history[-1].content) > 0


@pytest.mark.asyncio
@pytest.mark.timeout(5)
@pytest.mark.unit
async def test_abatch(hyperbolic_vision_model):
    image_prompt = {
        "Who painted this artwork?": "https://llava-vl.github.io/static/images/monalisa.jpg",
        "Describe the woman in the painting.": "https://llava-vl.github.io/static/images/monalisa.jpg",
    }
    conversations = []
    for prompt, image_url in image_prompt.items():
        conversation = Conversation()
        conversation.add_message(
            HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ]
            )
        )
        conversations.append(conversation)

    results = await hyperbolic_vision_model.abatch(conversations)

    assert len(results) == len(image_prompt.keys())
    for result in results:
        assert result.history[-1].content is not None
        assert isinstance(result.history[-1].content, str)
        assert len(result.history[-1].content) > 0
