import pytest
import os
from swarmauri_experimental.llms.OpenRouterModel import OpenRouterModel as LLM
from swarmauri.conversations.concrete.Conversation import Conversation
from swarmauri.messages.concrete.HumanMessage import HumanMessage
from swarmauri.messages.concrete.SystemMessage import SystemMessage
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

# List of models expected to fail
FAILING_MODELS = ["ai21/jamba-1-5-mini", "openai/gpt-4-32k", "ai21/jamba-1-5-large"]


@pytest.fixture(params=FAILING_MODELS)
def failing_model(request):
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    model = LLM(api_key=API_KEY)
    model.name = request.param
    return model


@pytest.mark.xfail(reason="These models are expected to fail")
def test_preamble_system_context_failing_models(failing_model):
    conversation = Conversation()

    system_context = 'You only respond with the following phrase, "Jeff"'
    system_message = SystemMessage(content=system_context)
    conversation.add_message(system_message)

    input_data = "Hi"
    human_message = HumanMessage(content=input_data)
    conversation.add_message(human_message)

    failing_model.predict(conversation=conversation)
    prediction = conversation.get_last().content

    assert isinstance(prediction, str)
    assert "Jeff" in prediction
