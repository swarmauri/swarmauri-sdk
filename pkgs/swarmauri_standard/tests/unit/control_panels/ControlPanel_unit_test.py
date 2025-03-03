import logging
import os
import pytest
from swarmauri_standard.llms.GroqModel import GroqModel
from swarmauri_standard.control_panels.ControlPanel import ControlPanel
from swarmauri_standard.factories.AgentFactory import AgentFactory
from swarmauri_standard.transports.PubSubTransport import PubSubTransport
from swarmauri_standard.task_mgmt_strategies.RoundRobinStrategy import (
    RoundRobinStrategy,
)
from swarmauri_standard.service_registries.ServiceRegistry import ServiceRegistry
from swarmauri_standard.agents.QAAgent import QAAgent
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
def control_panel():
    """Create a control panel with real components."""
    panel = ControlPanel(
        agent_factory=AgentFactory(),
        service_registry=ServiceRegistry(),
        task_mgmt_strategy=RoundRobinStrategy(),
        transport=PubSubTransport(),
    )
    return panel


@pytest.mark.unit
def test_ubc_resource(control_panel):
    """Test resource type."""
    assert control_panel.resource == "ControlPanel"


@pytest.mark.unit
def test_ubc_type(control_panel):
    """Test component type."""
    assert control_panel.type == "ControlPanel"


@pytest.mark.unit
def test_initialization(control_panel):
    """Test initialization with components."""
    assert isinstance(control_panel.agent_factory, AgentFactory)
    assert isinstance(control_panel.service_registry, ServiceRegistry)
    assert isinstance(control_panel.task_mgmt_strategy, RoundRobinStrategy)
    assert isinstance(control_panel.transport, PubSubTransport)


@pytest.mark.unit
def test_serialization(control_panel):
    """Test serialization/deserialization."""
    logging.info(control_panel)
    assert (
        control_panel.id
        == ControlPanel.model_validate_json(control_panel.model_dump_json()).id
    )


@pytest.mark.unit
def test_create_and_list_agents(control_panel, groq_model):
    """Test agent creation and listing."""
    control_panel.create_agent("QAAgent", QAAgent, "Answer Questions", llm=groq_model)
    active_agents = control_panel.list_active_agents()
    assert "QAAgent" in active_agents


@pytest.mark.unit
def test_remove_agent(control_panel, groq_model):
    """Test agent removal."""
    control_panel.create_agent("QAAgent", QAAgent, "QueAns_Agent", llm=groq_model)
    control_panel.remove_agent("QAAgent")
    active_agents = control_panel.list_active_agents()
    assert "QAAgent" not in active_agents


@pytest.mark.unit
def test_submit_and_process_tasks(control_panel, groq_model):
    """Test task submission and processing."""
    control_panel.create_agent("QAAgent", QAAgent, "QueAns_Agent", llm=groq_model)

    task = {"task_id": "task1", "payload": "test"}
    control_panel.submit_tasks([task])
    if isinstance(control_panel.transport, PubSubTransport):
        error_msg = (
            "Error processing tasks: send method is not supported for PubSubTransport"
        )
        with pytest.raises(ValueError, match=error_msg):
            control_panel.process_tasks()
    else:
        control_panel.process_tasks()
        # Verify task was processed by checking strategy queue is empty
        assert control_panel.task_mgmt_strategy.task_queue.empty()


@pytest.mark.unit
def test_distribute_tasks(control_panel, groq_model):
    """Test task distribution."""
    control_panel.create_agent("QAAgent", QAAgent, "Answer Questions", llm=groq_model)
    task = {"task_id": "task2", "payload": "test"}
    control_panel.distribute_tasks(task)
    # Verify task was assigned
    assert task["task_id"] in control_panel.task_mgmt_strategy.task_assignments


@pytest.mark.unit
def test_orchestrate_agents(control_panel, groq_model):
    """Test full orchestration flow."""
    control_panel.create_agent("QAAgent", QAAgent, "Answer Questions", llm=groq_model)
    tasks = [
        {"task_id": "task3", "payload": "test1"},
        {"task_id": "task4", "payload": "test2"},
    ]

    if isinstance(control_panel.transport, PubSubTransport):
        error_msg = (
            "Error processing tasks: send method is not supported for PubSubTransport"
        )

        with pytest.raises(ValueError, match=error_msg):
            control_panel.orchestrate_agents(tasks)

    else:
        control_panel.orchestrate_agents(tasks)
        assert control_panel.task_mgmt_strategy.task_queue.empty()
