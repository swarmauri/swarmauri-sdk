import os
import pytest
from swarmauri.control_panels.concrete import ControlPanel
from swarmauri.llms.concrete.GroqModel import GroqModel
from swarmauri.mas.concrete.CentralizedMas import CentralizedMas
from swarmauri.transports.concrete.PubSubTransport import PubSubTransport
from swarmauri.task_mgt_strategies.concrete.RoundRobinStrategy import RoundRobinStrategy
from swarmauri.factories.concrete.AgentFactory import AgentFactory
from swarmauri.agents.concrete.QAAgent import QAAgent
from swarmauri.agents.concrete.SimpleConversationAgent import SimpleConversationAgent
from swarmauri.service_registries.concrete.ServiceRegistry import ServiceRegistry
from swarmauri.conversations.concrete.MaxSystemContextConversation import (
    MaxSystemContextConversation,
)

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
def centralized_mas():

    transport = PubSubTransport()
    agent_factory = AgentFactory()
    task_mgt_strategy = RoundRobinStrategy()
    service_registry = ServiceRegistry()

    return CentralizedMas(
        transport=transport,
        agent_factory=agent_factory,
        task_mgt_strategy=task_mgt_strategy,
        control_panel=ControlPanel(
            transport=transport,
            agent_factory=agent_factory,
            task_mgt_strategy=task_mgt_strategy,
            service_registry=service_registry,
        ),
    )


@pytest.mark.unit
def test_ubc_resource(centralized_mas):
    assert centralized_mas.resource == "Mas"


@pytest.mark.unit
def test_ubc_type(centralized_mas):
    assert centralized_mas.type == "CentralizedMas"


@pytest.mark.unit
def test_serialization(centralized_mas):
    assert (
        centralized_mas.id
        == CentralizedMas.model_validate_json(centralized_mas.model_dump_json()).id
    )


def test_add_agent(centralized_mas, groq_model):
    # Act
    name = "QAAgent"
    centralized_mas.add_agent(name, QAAgent, llm=groq_model)

    # Assert
    assert name in centralized_mas.agent_factory.get()
    assert isinstance(centralized_mas.control_panel.list_active_agents()[name], QAAgent)


def test_remove_agent(centralized_mas, groq_model):
    # Arrange
    name = "QAAgent"
    # Act
    centralized_mas.remove_agent(name)

    # Assert
    assert name not in centralized_mas.agent_factory.get()


def test_broadcast(centralized_mas, groq_model):
    # Arrange
    agents = {"agent1": QAAgent, "agent2": SimpleConversationAgent}
    message = "test_message"

    for name, agent in agents.items():
        centralized_mas.add_agent(
            name, agent, llm=groq_model, conversation=MaxSystemContextConversation()
        )

    # Act
    centralized_mas.broadcast(message)

    # Assert
    assert len(centralized_mas.control_panel.list_active_agents().keys()) == 2
    # Additional assertions based on transport behavior


def test_multicast(centralized_mas, groq_model):
    # Arrange
    recipient_ids = ["agent1", "agent2"]
    message = "test_message"

    # Act
    centralized_mas.multicast(message, recipient_ids)

    # Assert
    assert len(centralized_mas.agent_factory.get()) == 2
    # Additional assertions based on transport behavior


def test_unicast(centralized_mas, groq_model):
    # Arrange
    name = "agent1"
    message = "test_message"

    # Act
    centralized_mas.unicast(message, name)

    # Assert
    assert name in centralized_mas.agent_factory.get()
    # Additional assertions based on transport behavior


def test_dispatch_task(centralized_mas, groq_model):
    # Arrange
    name = "agent1"
    task = {"task_id": "task1"}

    # Act
    centralized_mas.dispatch_task(task, name)

    # Assert
    assert name in centralized_mas.agent_factory.get()


def test_dispatch_tasks(centralized_mas, groq_model):
    # Arrange
    agents = {"agent1": QAAgent, "agent2": SimpleConversationAgent}
    tasks = {"task_id": "task1", "task_id2": "task2"}

    centralized_mas.dispatch_tasks(tasks, agents.values())

    # Assert
    assert all(
        agent_id in centralized_mas.agent_factory.get() for agent_id in agents.keys()
    )
