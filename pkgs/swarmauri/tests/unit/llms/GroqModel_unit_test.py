import asyncio
import json
import logging
import pytest
import os
from swarmauri.llms.concrete.GroqModel import GroqModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation

from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
# image_path = "/home/michaeldecent/Downloads/carbon.png"
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

@pytest.fixture(scope="module")
def groq_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY, stream=True)
    return llm


@pytest.fixture(scope="module")
def llama_guard_model():
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = LLM(api_key=API_KEY)
    llm.name = "llama-guard-3-8b"
    return llm


def get_allowed_models():
    if not API_KEY:
        return []
    llm = LLM(api_key=API_KEY)

    # not consistent with their results
    failing_llms = [
        "llama3-70b-8192",
        "llama-3.2-90b-text-preview",
        "mixtral-8x7b-32768",
        "llava-v1.5-7b-4096-preview",
        "llama-guard-3-8b",
    ]

    # multimodal models
    multimodal_models = ["llama-3.2-11b-vision-preview"]

    # Filter out the failing models
    allowed_models = [
        model
        for model in llm.allowed_models
        if model not in failing_llms and model not in multimodal_models
    ]

    return allowed_models


@pytest.mark.unit
def test_ubc_resource(groq_model):
    assert groq_model.resource == "LLM"


@pytest.mark.unit
def test_ubc_type(groq_model):
    assert groq_model.type == "GroqModel"


@pytest.mark.unit
def test_serialization(groq_model):
    assert groq_model.id == LLM.model_validate_json(groq_model.model_dump_json()).id


@pytest.mark.unit
def test_default_name(groq_model):
    assert groq_model.name == "gemma-7b-it"


# @pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.asyncio
@pytest.mark.unit
async def test_no_system_context(groq_model):
    # groq_model.name = model_name
    conversation = Conversation()

    input_data = "Hello"

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)
    #
    # if groq_model.stream:
    #     async for chunk in groq_model.predict(conversation):
    #         assert isinstance(chunk.choices[0].delta.content, str),  f"instead i got this data type {type(chunk.choices[0].delta.content)}"
    #
    # else:
    result = groq_model.predict(conversation=conversation)
    if groq_model.stream:
        async for chunk in result:
            logging.info(chunk)
            assert isinstance(conversation.get_last().content, str),  f"instead i got this data type {type(chunk)}"
    else:

        prediction = conversation.get_last().content
        logging.info(prediction)
        assert isinstance(prediction, str)

@pytest.mark.parametrize("model_name", get_allowed_models())
@pytest.mark.unit
def test_preamble_system_context(groq_model, model_name):
    model = groq_model
    model.name = model_name
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    human_message = SystemMessage(content=system_context)
    conversation.add_message(human_message)

    input_data = "Hi"

    human_message = HumanMessage(content=json.dumps(input_data))
    conversation.add_message(human_message)

    model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    logging.info(prediction)
    assert type(prediction) == str
    assert "Jeff" in prediction


@pytest.mark.unit
def test_llama_guard_3_8b_no_system_context(llama_guard_model):
    """
    Test case specifically for the llama-guard-3-8b model.
    This model is designed to classify inputs as safe or unsafe.

    Reference: https://www.llama.com/docs/model-cards-and-prompt-formats/llama-guard-3/
    """
    conversation = Conversation()

    input_data = "Hello, how are you?"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    llama_guard_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    assert isinstance(prediction, str)
    assert "safe" in prediction.lower()


@pytest.mark.parametrize(
    "model_name, input_data",
    [
        (
            "llama-3.2-11b-vision-preview",
            [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"{image_url}",
                    },
                },
            ],
        ),
    ],
)
@pytest.mark.unit
def test_multimodal_models_no_system_context(groq_model, model_name, input_data):
    """
    Test case specifically for the multimodal models.
    This models are designed process a wide variety of inputs, including text, images, and audio,
    as prompts and convert those prompts into various outputs, not just the source type.

    """
    conversation = Conversation()
    groq_model.name = model_name

    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    groq_model.predict(conversation=conversation)
    prediction = conversation.get_last().content
    logging.info(prediction)
    assert isinstance(prediction, str)
