import pytest
from unittest.mock import MagicMock
from swarmauri.control_panels.concrete.ControlPanel import ControlPanel
from swarmauri.factories.base.FactoryBase import FactoryBase
from swarmauri.service_registries.base.ServiceRegistryBase import ServiceRegistryBase
from swarmauri.task_mgt_strategies.base.TaskMgtStrategyBase import TaskMgtStrategyBase
from swarmauri.transports.base.TransportBase import TransportBase


@pytest.fixture
def control_panel():
    """Fixture to create a ControlPanel instance with mocked dependencies."""
    agent_factory = MagicMock(spec=FactoryBase)
    service_registry = MagicMock(spec=ServiceRegistryBase)
    task_mgt_strategy = MagicMock(spec=TaskMgtStrategyBase)
    transport = MagicMock(spec=TransportBase)

    return ControlPanel(
        agent_factory=agent_factory,
        service_registry=service_registry,
        task_mgt_strategy=task_mgt_strategy,
        transport=transport,
    )


def test_create_agent(control_panel):
    """Test the create_agent method."""
    agent_name = "agent1"
    agent_role = "worker"
    agent = MagicMock()

    # Configure mocks
    control_panel.agent_factory.create_agent.return_value = agent

    # Call the method
    result = control_panel.create_agent(agent_name, agent_role)

    # Assertions
    control_panel.agent_factory.create_agent.assert_called_once_with(
        agent_name, agent_role
    )
    control_panel.service_registry.register_service.assert_called_once_with(
        agent_name, {"role": agent_role, "status": "active"}
    )
    assert result == agent


def test_remove_agent(control_panel):
    """Test the remove_agent method."""
    agent_name = "agent1"
    agent = MagicMock()

    # Configure mocks
    control_panel.agent_factory.get_agent_by_name.return_value = agent

    # Call the method
    control_panel.remove_agent(agent_name)

    # Assertions
    control_panel.agent_factory.get_agent_by_name.assert_called_once_with(agent_name)
    control_panel.service_registry.unregister_service.assert_called_once_with(
        agent_name
    )
    control_panel.agent_factory.delete_agent.assert_called_once_with(agent_name)


def test_remove_agent_not_found(control_panel):
    """Test remove_agent when the agent is not found."""
    agent_name = "agent1"

    # Configure mocks
    control_panel.agent_factory.get_agent_by_name.return_value = None

    # Call the method and expect a ValueError
    with pytest.raises(ValueError) as exc_info:
        control_panel.remove_agent(agent_name)
    assert str(exc_info.value) == f"Agent '{agent_name}' not found."


def test_list_active_agents(control_panel):
    """Test the list_active_agents method."""
    agent1 = MagicMock()
    agent1.name = "agent1"
    agent2 = MagicMock()
    agent2.name = "agent2"
    agents = [agent1, agent2]

    # Configure mocks
    control_panel.agent_factory.get_agents.return_value = agents

    # Call the method
    result = control_panel.list_active_agents()

    # Assertions
    control_panel.agent_factory.get_agents.assert_called_once()
    assert result == ["agent1", "agent2"]


def test_submit_tasks(control_panel):
    """Test the submit_tasks method."""
    task1 = {"task_id": "task1"}
    task2 = {"task_id": "task2"}
    tasks = [task1, task2]

    # Call the method
    control_panel.submit_tasks(tasks)

    # Assertions
    calls = [((task1,),), ((task2,),)]
    control_panel.task_mgt_strategy.add_task.assert_has_calls(calls)
    assert control_panel.task_mgt_strategy.add_task.call_count == 2


def test_process_tasks(control_panel):
    """Test the process_tasks method."""
    # Call the method
    control_panel.process_tasks()

    # Assertions
    control_panel.task_mgt_strategy.process_tasks.assert_called_once_with(
        control_panel.service_registry.get_services, control_panel.transport
    )


def test_process_tasks_exception(control_panel, caplog):
    """Test process_tasks when an exception occurs."""
    # Configure mocks
    control_panel.task_mgt_strategy.process_tasks.side_effect = Exception("Test error")

    # Call the method
    control_panel.process_tasks()

    # Assertions
    control_panel.task_mgt_strategy.process_tasks.assert_called_once_with(
        control_panel.service_registry.get_services, control_panel.transport
    )
    assert "Error while processing tasks: Test error" in caplog.text


def test_distribute_tasks(control_panel):
    """Test the distribute_tasks method."""
    task = {"task_id": "task1"}

    # Call the method
    control_panel.distribute_tasks(task)

    # Assertions
    control_panel.task_mgt_strategy.assign_task.assert_called_once_with(
        task, control_panel.service_registry.get_services
    )


def test_orchestrate_agents(control_panel):
    """Test the orchestrate_agents method."""
    tasks = [{"task_id": "task1"}, {"task_id": "task2"}]

    # Configure mocks
    control_panel.submit_tasks = MagicMock()
    control_panel.process_tasks = MagicMock()

    # Call the method
    control_panel.orchestrate_agents(tasks)

    # Assertions
    control_panel.submit_tasks.assert_called_once_with(tasks)
    control_panel.process_tasks.assert_called_once()
