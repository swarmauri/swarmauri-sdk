import pytest
from unittest.mock import Mock, MagicMock
from swarmauri.mas.concrete.CentralizedMas import CentralizedMas
from swarmauri.transports.concrete.PubSubTransport import PubSubTransport
from swarmauri.task_mgt_strategies.concrete.RoundRobinStrategy import RoundRobinStrategy
from swarmauri.factories.concrete.AgentFactory import AgentFactory


@pytest.fixture
def mock_transport():
    return Mock()


@pytest.fixture
def mock_agent_factory():
    return Mock()


@pytest.fixture
def mock_service_registry():
    return Mock()


@pytest.fixture
def mock_task_strategy():
    return Mock()


@pytest.fixture
def centralized_mas():
    mas = CentralizedMas(PubSubTransport, AgentFactory, RoundRobinStrategy)
    return mas


def test_add_agent(centralized_mas):    
    # Act
    centralized_mas.add_agent(agent_id, agent)

    # Assert
    assert centralized_mas._agents[agent_id] == agent
    centralized_mas.control_plane.create_agent.assert_called_once_with(agent_id, agent)


def test_remove_agent(centralized_mas):
    # Arrange
    agent_id = "agent1"
    agent = MagicMock()
    centralized_mas._agents[agent_id] = agent

    # Act
    centralized_mas.remove_agent(agent_id)

    # Assert
    assert agent_id not in centralized_mas._agents
    centralized_mas.service_registry.deregister_agent.assert_called_once_with(agent_id)


def test_broadcast(centralized_mas):
    # Arrange
    message = "test_message"
    agent1, agent2 = MagicMock(), MagicMock()
    centralized_mas._agents = {"agent1": agent1, "agent2": agent2}

    # Act
    centralized_mas.broadcast(message)

    # Assert
    centralized_mas.transport.broadcast.assert_called_once()
    args = centralized_mas.transport.broadcast.call_args[0]
    assert args[0] == message
    assert len(args[1]) == 2


def test_multicast(centralized_mas):
    # Arrange
    message = "test_message"
    recipient_ids = ["agent1", "agent2"]
    agent1, agent2 = MagicMock(), MagicMock()
    centralized_mas._agents = {"agent1": agent1, "agent2": agent2}

    # Act
    centralized_mas.multicast(message, recipient_ids)

    # Assert
    centralized_mas.transport.multicast.assert_called_once()
    args = centralized_mas.transport.multicast.call_args[0]
    assert args[0] == message
    assert len(args[1]) == 2


def test_unicast(centralized_mas):
    # Arrange
    message = "test_message"
    recipient_id = "agent1"
    agent = MagicMock()
    centralized_mas._agents[recipient_id] = agent

    # Act
    centralized_mas.unicast(message, recipient_id)

    # Assert
    centralized_mas.transport.send_message.assert_called_once_with(message, agent)


def test_dispatch_task(centralized_mas):
    # Arrange
    task = "test_task"
    agent_id = "agent1"
    agent = MagicMock()
    centralized_mas._agents[agent_id] = agent

    # Act
    centralized_mas.dispatch_task(task, agent_id)

    # Assert
    agent.perform_task.assert_called_once_with(task)


def test_dispatch_tasks(centralized_mas):
    # Arrange
    tasks = ["task1", "task2"]
    agent_ids = ["agent1", "agent2"]
    agent1, agent2 = MagicMock(), MagicMock()
    centralized_mas._agents = {"agent1": agent1, "agent2": agent2}

    # Act
    centralized_mas.dispatch_tasks(tasks, agent_ids)

    # Assert
    agent1.perform_task.assert_called_once_with("task1")
    agent2.perform_task.assert_called_once_with("task2")
