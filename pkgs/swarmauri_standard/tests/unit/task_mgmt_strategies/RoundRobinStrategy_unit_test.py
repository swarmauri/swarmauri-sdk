import pytest
from unittest.mock import MagicMock
from swarmauri_standard.task_mgmt_strategies.RoundRobinStrategy import (
    RoundRobinStrategy,
)


@pytest.fixture
def round_robin_strategy():
    """Fixture to create a RoundRobinStrategy instance."""
    return RoundRobinStrategy()


@pytest.mark.unit
def test_ubc_resource(round_robin_strategy):
    assert round_robin_strategy.resource == "TaskMgmtStrategy"


@pytest.mark.unit
def test_ubc_type(round_robin_strategy):
    assert round_robin_strategy.type == "RoundRobinStrategy"


@pytest.mark.unit
def test_serialization(round_robin_strategy):
    round_robin_strategy.model_dump_json()
    assert (
        round_robin_strategy.id
        == RoundRobinStrategy.model_validate_json(
            round_robin_strategy.model_dump_json()
        ).id
    )


def test_assign_task(round_robin_strategy):
    # Setup
    task = {"task_id": "task1", "payload": "data"}
    service_registry = MagicMock(return_value=["service1", "service2"])

    # Execute
    round_robin_strategy.assign_task(task, service_registry)

    # Verify
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
    # Setup
    task = {"task_id": "task1", "payload": "data"}

    # Execute
    round_robin_strategy.add_task(task)

    # Verify
    assert not round_robin_strategy._task_queue.empty()
    queued_task = round_robin_strategy._task_queue.get()
    assert queued_task == task


def test_remove_task(round_robin_strategy):
    # Setup
    task_id = "task1"
    round_robin_strategy.task_assignments[task_id] = "service1"

    # Execute
    round_robin_strategy.remove_task(task_id)

    # Verify
    assert task_id not in round_robin_strategy.task_assignments


def test_remove_task_not_found(round_robin_strategy):
    # Setup
    task_id = "task1"

    # Execute & Verify
    with pytest.raises(ValueError) as exc_info:
        round_robin_strategy.remove_task(task_id)
    assert str(exc_info.value) == "Task 'task1' not found in assignments."


def test_get_task(round_robin_strategy):
    # Setup
    task_id = "task1"
    round_robin_strategy.task_assignments[task_id] = "service1"

    # Execute
    result = round_robin_strategy.get_task(task_id)

    # Verify
    expected_result = {"task_id": task_id, "assigned_service": "service1"}
    assert result == expected_result


def test_get_task_not_found(round_robin_strategy):
    # Setup
    task_id = "task1"

    # Execute & Verify
    with pytest.raises(ValueError) as exc_info:
        round_robin_strategy.get_task(task_id)
    assert str(exc_info.value) == "Task 'task1' not found in assignments."


def test_process_tasks(round_robin_strategy):
    # Setup
    service_registry = MagicMock(return_value=["service1", "service2"])
    transport = MagicMock()
    tasks = [
        {"task_id": "task1", "payload": "data1"},
        {"task_id": "task2", "payload": "data2"},
        {"task_id": "task3", "payload": "data3"},
    ]
    for task in tasks:
        round_robin_strategy.add_task(task)

    # Execute
    round_robin_strategy.process_tasks(service_registry, transport)

    # Verify assignments
    assert round_robin_strategy.task_assignments["task1"] == "service1"
    assert round_robin_strategy.task_assignments["task2"] == "service2"
    assert round_robin_strategy.task_assignments["task3"] == "service1"
    assert round_robin_strategy.current_index == 3

    # Verify that transport.send was called correctly
    transport.send.assert_any_call(tasks[0], "service1")
    transport.send.assert_any_call(tasks[1], "service2")
    transport.send.assert_any_call(tasks[2], "service1")
    assert transport.send.call_count == 3


def test_process_tasks_no_services(round_robin_strategy):
    # Setup
    service_registry = MagicMock(return_value=[])
    transport = MagicMock()
    task = {"task_id": "task1", "payload": "data"}
    round_robin_strategy.add_task(task)

    # Execute & Verify
    with pytest.raises(ValueError) as exc_info:
        round_robin_strategy.process_tasks(service_registry, transport)
    assert "No services available for task assignment." in str(exc_info.value)
