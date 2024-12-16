import pytest
from unittest.mock import MagicMock, patch
from swarmauri.control_panels.concrete.ControlPanel import ControlPanel


@pytest.fixture
def control_panel():
    agent_factory = MagicMock()
    service_registry = MagicMock()
    task_strategy = MagicMock()
    transport = MagicMock()
    return ControlPanel(agent_factory, service_registry, task_strategy, transport)


def test_create_agent(control_panel):
    control_panel.agent_factory.create_agent.return_value = "agent1"
    name = "agent1"
    role = "role1"

    result = control_panel.create_agent(name, role)

    control_panel.agent_factory.create_agent.assert_called_with(name, role)
    control_panel.service_registry.register_service.assert_called_with(
        name, {"role": role, "status": "active"}
    )
    assert result == "agent1"


def test_distribute_tasks(control_panel):
    task = "task1"

    control_panel.distribute_tasks(task)

    control_panel.task_strategy.assign_task.assert_called_with(
        task, control_panel.agent_factory, control_panel.service_registry
    )


def test_orchestrate_agents(control_panel):
    task = "task1"

    control_panel.orchestrate_agents(task)

    with patch.object(control_panel, "manage_agents") as mock_manage_agents:
        mock_manage_agents.assert_called_once()
    control_panel.distribute_tasks.assert_called_with(task)


def test_remove_agent_success(control_panel):
    # Arrange
    name = "agent1"
    agent = MagicMock()
    control_panel.agent_factory.get_agent_by_name.return_value = agent

    control_panel.remove_agent(name)

    control_panel.service_registry.unregister_service.assert_called_with(name)
    control_panel.agent_factory.delete_agent.assert_called_with(name)


def test_remove_agent_not_found(control_panel):
    # Arrange
    name = "agent1"
    control_panel.agent_factory.get_agent_by_name.return_value = None

    # Act & Assert
    with pytest.raises(ValueError) as excinfo:
        control_panel.remove_agent(name)
    assert str(excinfo.value) == f"Agent {name} not found."


def test_list_active_agents(control_panel):
    # Arrange
    agent1 = MagicMock()
    agent1.name = "agent1"
    agent2 = MagicMock()
    agent2.name = "agent2"
    control_panel.agent_factory.get_agents.return_value = [agent1, agent2]

    result = control_panel.list_active_agents()

    control_panel.agent_factory.get_agents.assert_called_once()
    assert result == ["agent1", "agent2"]
