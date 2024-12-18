import logging
import os
import pytest
from swarmauri.control_panels.concrete.ControlPanel import ControlPanel
from swarmauri.factories.concrete.AgentFactory import AgentFactory
from swarmauri.service_registries.concrete.ServiceRegistry import ServiceRegistry
from swarmauri.task_mgt_strategies.concrete.RoundRobinStrategy import RoundRobinStrategy
from swarmauri.transports.concrete.PubSubTransport import PubSubTransport
from swarmauri.agents.concrete.QAAgent import QAAgent
from swarmauri.llms.concrete.GroqModel import GroqModel
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def groq_model():
    API_KEY = os.getenv("GROQ_API_KEY")
    if not API_KEY:
        pytest.skip("Skipping due to environment variable not set")
    llm = GroqModel(api_key=API_KEY)
    return llm


@pytest.fixture
def agent_factory():
    """Fixture to create a fully mocked AgentFactory instance with serializable mocks."""
    return AgentFactory()


@pytest.fixture
def service_registry():
    """Fixture to create a fully mocked ServiceRegistry instance with serializable mocks."""
    return ServiceRegistry()


@pytest.fixture
def task_mgt_strategy():
    """Fixture to create a fully mocked TaskMgtStrategy instance with serializable mocks."""
    return RoundRobinStrategy()


@pytest.fixture
def transport():
    """Fixture to create a fully mocked Transport instance with serializable mocks."""
    return PubSubTransport()


@pytest.fixture
def control_panel(agent_factory, service_registry, task_mgt_strategy, transport):
    """Fixture to create a fully mocked ControlPanel instance with serializable mocks."""

    # Return the ControlPanel instance with mocked dependencies
    return ControlPanel(
        agent_factory=agent_factory,
        service_registry=service_registry,
        task_mgt_strategy=task_mgt_strategy,
        transport=transport,
    )


@pytest.mark.unit
def test_ubc_resource(control_panel):
    assert control_panel.resource == "ControlPanel"


@pytest.mark.unit
def test_ubc_type(control_panel):
    assert control_panel.type == "ControlPanel"


@pytest.mark.unit
def test_serialization(control_panel):
    assert (
        control_panel.id
        == ControlPanel.model_validate_json(control_panel.model_dump_json()).id
    )


@pytest.mark.unit
def test_create_agent(
    control_panel,
    agent_factory,
    groq_model,
):
    """Test the create_agent method."""

    agent_factory.register("QAAgent", QAAgent)

    # Call the method
    agent = control_panel.create_agent(name="QAAgent", llm=groq_model, role="Agent1")

    assert agent.type == "QAAgent"
    assert agent.type in agent_factory.get()


@pytest.mark.unit
def test_remove_agent(control_panel, agent_factory, groq_model):
    """Test the remove_agent method."""

    agent_factory.register("QAAgent", QAAgent)
    control_panel.create_agent(name="QAAgent", llm=groq_model, role="Agent1")

    control_panel.remove_agent("QAAgent")
    assert "QAAgent" not in control_panel.agent_factory.get()


@pytest.mark.unit
def test_remove_agent_not_found(control_panel):
    """Test remove_agent when the agent is not found."""

    # Call the method and expect a ValueError
    with pytest.raises(ValueError) as exc_info:
        control_panel.remove_agent("QAAgent")
    assert str(exc_info.value) == "Type 'QAAgent' is not registered."


@pytest.mark.unit
def test_list_active_agents(control_panel, agent_factory, groq_model):
    """Test the list_active_agents method."""

    agent_factory.register("QAAgent", QAAgent)
    control_panel.create_agent(name="QAAgent", llm=groq_model, role="Agent1")

    # Call the method
    result = control_panel.list_active_agents()

    assert isinstance(result.get("QAAgent"), QAAgent)


@pytest.mark.unit
def test_submit_tasks(control_panel, task_mgt_strategy):
    """Test the submit_tasks method."""
    task1 = {"task_id": "task1"}
    task2 = {"task_id": "task2"}
    tasks = [task1, task2]

    # Call the method
    control_panel.submit_tasks(tasks)

    assert len(tasks) == len(task_mgt_strategy.get_tasks())


@pytest.mark.unit
def test_submit_and_process_tasks(control_panel, agent_factory, groq_model):
    """Test the process_tasks method."""

    agent_factory.register("QAAgent", QAAgent)
    control_panel.create_agent(name="QAAgent", llm=groq_model, role="Agent1")

    task1 = {"task_id": "task1"}
    task2 = {"task_id": "task2"}
    tasks = [task1, task2]

    control_panel.submit_tasks(tasks)

    with pytest.raises(ValueError) as exc_info:
        control_panel.process_tasks()

    assert (
        str(exc_info.value)
        == "Error processing tasks: Direct send not supported in Pub/Sub model."
    )


@pytest.mark.unit
def test_distribute_tasks(control_panel, agent_factory, groq_model):
    """Test the distribute_tasks method."""

    agent_factory.register("QAAgent", QAAgent)
    control_panel.create_agent(name="QAAgent", llm=groq_model, role="Agent1")

    task = {"task_id": "task1"}

    # Call the method
    service = control_panel.distribute_tasks(task)

    assert isinstance(service, QAAgent)


@pytest.mark.unit
def test_orchestrate_agents(control_panel, agent_factory, groq_model):
    """Test the orchestrate_agents method."""
    agent_factory.register("QAAgent", QAAgent)
    control_panel.create_agent(name="QAAgent", llm=groq_model, role="Agent1")

    tasks = [{"task_id": "task1"}, {"task_id": "task2"}]

    with pytest.raises(ValueError) as exc_info:
        control_panel.orchestrate_agents(tasks)

    assert (
        str(exc_info.value)
        == "Error processing tasks: Direct send not supported in Pub/Sub model."
    )
