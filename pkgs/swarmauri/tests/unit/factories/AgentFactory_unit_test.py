import logging
import pytest
from swarmauri.factories.concrete.AgentFactory import AgentFactory
import os
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.agents.concrete import QAAgent
from dotenv import load_dotenv

load_dotenv()


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

    agent_factory.register(type="QAAgent", resource_class=QAAgent)

    # Create an instance
    instance = agent_factory.create(type="QAAgent", llm=groq_model)
    assert isinstance(instance, QAAgent)
    assert instance.type == "QAAgent"
    logging.info(instance.resource)


@pytest.mark.unit
def test_agent_factory_duplicate_register(agent_factory):

    # Attempt to register the same type again
    with pytest.raises(ValueError, match="Type 'QAAgent' is already registered."):
        agent_factory.register(type="QAAgent", resource_class=QAAgent)


@pytest.mark.unit
def test_agent_factory_create_unregistered_type(agent_factory):

    # Attempt to create an unregistered type
    with pytest.raises(ValueError, match="Type 'UnregisteredType' is not registered."):
        agent_factory.create(type="UnregisteredType")