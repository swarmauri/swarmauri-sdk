import pytest
from swarmauri.task_mgt_strategies.concrete.RoundRobinStrategy import RoundRobinStrategy
from unittest.mock import MagicMock


@pytest.fixture
def round_robin_strategy():
    """Fixture to create a RoundRobinStrategy instance."""
    return RoundRobinStrategy()


def test_assign_task(round_robin_strategy):
    # Setup
    task = {"task_id": "task1", "payload": "data"}
    service_registry = MagicMock(return_value=["service1", "service2"])

    round_robin_strategy.assign_task(task, service_registry)

    assert round_robin_strategy.task_assignments["task1"] == "service1"
    assert round_robin_strategy.current_index == 1


def test_assign_task_no_services(round_robin_strategy):
    # Setup
    task = {"task_id": "task1", "payload": "data"}
    service_registry = MagicMock(return_value=[])

    # Execute & Verify
    with pytest.raises(ValueError) as exc_info:
        round_robin_strategy.assign_task(task, service_registry)
    assert str(exc_info.value) == "No services available for task assignment."


def test_add_task(round_robin_strategy):
    task = {"task_id": "task1", "payload": "data"}

    round_robin_strategy.add_task(task)

    assert not round_robin_strategy.task_queue.empty()
    queued_task = round_robin_strategy.task_queue.get()
    assert queued_task == task


def test_remove_task(round_robin_strategy):
    task_id = "task1"
    round_robin_strategy.task_assignments[task_id] = "service1"

    round_robin_strategy.remove_task(task_id)

    assert task_id not in round_robin_strategy.task_assignments


def test_remove_task_not_found(round_robin_strategy):
    task_id = "task1"

    with pytest.raises(ValueError) as exc_info:
        round_robin_strategy.remove_task(task_id)
    assert str(exc_info.value) == "Task 'task1' not found in assignments."


def test_get_task(round_robin_strategy):
    task_id = "task1"
    round_robin_strategy.task_assignments[task_id] = "service1"

    result = round_robin_strategy.get_task(task_id)

    assert result == {"task_id": task_id, "assigned_service": "service1"}


def test_get_task_not_found(round_robin_strategy):
    task_id = "task1"

    with pytest.raises(ValueError) as exc_info:
        round_robin_strategy.get_task(task_id)
    assert str(exc_info.value) == "Task 'task1' not found in assignments."


def test_process_tasks(round_robin_strategy):
    service_registry = MagicMock(return_value=["service1", "service2"])
    tasks = [
        {"task_id": "task1", "payload": "data1"},
        {"task_id": "task2", "payload": "data2"},
        {"task_id": "task3", "payload": "data3"},
    ]
    for task in tasks:
        round_robin_strategy.add_task(task)

    round_robin_strategy.process_tasks(service_registry)

    assert round_robin_strategy.task_assignments["task1"] == "service1"
    assert round_robin_strategy.task_assignments["task2"] == "service2"
    assert round_robin_strategy.task_assignments["task3"] == "service1"
    assert round_robin_strategy.current_index == 3
