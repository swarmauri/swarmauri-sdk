import os
import pytest
from swarmauri.service_registries.concrete.ServiceRegistry import ServiceRegistry
from swarmauri.factories.concrete.AgentFactory import AgentFactory
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.llms.concrete.OpenAIModel import OpenAIModel
from swarmauri.agents.concrete.QAAgent import QAAgent
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
def openai_model():
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = OpenAIModel(api_key=API_KEY)
    return llm


@pytest.fixture(scope="module")
def created_agent(groq_model):
    agent = AgentFactory()
    agent.register(type="QAAgent", resource_class=QAAgent)
    return agent.create(type="QAAgent", llm=groq_model)


@pytest.fixture(scope="module")
def service_registry():
    return ServiceRegistry()


@pytest.mark.unit
def test_ubc_resource(service_registry):
    assert service_registry.resource == "ServiceRegistry"


@pytest.mark.unit
def test_ubc_type(service_registry):
    assert service_registry.type == "ServiceRegistry"


@pytest.mark.unit
def test_serialization(service_registry):
    assert (
        service_registry.id
        == ServiceRegistry.model_validate_json(service_registry.model_dump_json()).id
    )


@pytest.mark.unit
def test_register_service(service_registry, created_agent):
    service_registry.register_service(service=created_agent, name="QAAgent")
    assert isinstance(service_registry.services["QAAgent"], QAAgent)


@pytest.mark.unit
def test_get_service(service_registry, created_agent):
    service_registry.register_service(service=created_agent, name="QAAgent")
    service = service_registry.get_service("QAAgent")
    assert isinstance(service, QAAgent)
    assert service_registry.get_service("nonexistent") is None


@pytest.mark.unit
def test_unregister_service(service_registry, created_agent):
    service_registry.register_service(service=created_agent, name="QAAgent")
    service_registry.unregister_service("QAAgent")
    assert "QAAgent" not in service_registry.services


@pytest.mark.unit
def test_unregister_service_nonexistent(service_registry):
    with pytest.raises(ValueError) as exc_info:
        service_registry.unregister_service("nonexistent")
    assert str(exc_info.value) == "Service nonexistent not found."


@pytest.mark.unit
def test_update_service(service_registry, created_agent):
    service_registry.register_service(service=created_agent, name="QAAgent")
    service_registry.update_service("QAAgent", llm=openai_model)
    assert service_registry.services["QAAgent"].llm == openai_model


@pytest.mark.unit
def test_update_service_nonexistent(service_registry):
    with pytest.raises(ValueError) as exc_info:
        service_registry.update_service("nonexistent")
    assert str(exc_info.value) == "Service nonexistent not found."
