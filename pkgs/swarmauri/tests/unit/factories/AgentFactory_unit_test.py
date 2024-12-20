from typing import Literal
import pytest
from swarmauri.factories.concrete.AgentFactory import AgentFactory
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.utils._get_subclasses import get_classes_from_module

from dotenv import load_dotenv

load_dotenv()


class TestAgent:
    type: Literal["TestAgent"] = "TestAgent"

    def exec(self, **kwargs):
        return "TestAgent execution result"


@pytest.fixture(scope="module")
def groq_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = GroqModel(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def agent_factory():
    return AgentFactory()


@pytest.mark.unit
def test_ubc_resource(agent_factory):
    assert agent_factory.resource == "Factory"


@pytest.mark.unit
def test_ubc_type(agent_factory):
    assert agent_factory.type == "AgentFactory"


@pytest.mark.unit
def test_serialization(agent_factory):
    assert (
        agent_factory.id
        == AgentFactory.model_validate_json(agent_factory.model_dump_json()).id
    )


@pytest.mark.unit
def test_agent_factory_register_and_create(agent_factory, groq_model):

    agent_factory.register(type="TestAgent", resource_class=TestAgent)

    # Create an instance
    instance = agent_factory.create(type="TestAgent")
    assert isinstance(instance, TestAgent)
    assert instance.type == "TestAgent"


@pytest.mark.unit
def test_agent_factory_create_unregistered_type(agent_factory):

    # Attempt to create an unregistered type
    with pytest.raises(ValueError, match="Type 'UnregisteredType' is not registered."):
        agent_factory.create(type="UnregisteredType")


@pytest.mark.unit
def test_agent_factory_get_agents(agent_factory):
    assert len(agent_factory.get()) == len(get_classes_from_module("Agent").keys()) + 1
