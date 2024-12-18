from typing import Callable, Dict, Any, List, Literal
from swarmauri.task_mgt_strategies.base.TaskMgtStrategyBase import TaskMgtStrategyBase
from queue import Queue
import logging


class RoundRobinStrategy(TaskMgtStrategyBase):
    """Round-robin task assignment strategy."""

    task_assignments: Dict[str, str] = {}  # Tracks task assignments
    current_index: int = 0
    type: Literal["RoundRobinStrategy"] = "RoundRobinStrategy"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._task_queue = Queue()  # Private instance attribute

    def assign_task(self, task: Dict[str, Any], services: List[Callable]) -> Callable:
        """
        Assign a task to a service using the round-robin strategy.
        :param task: Task metadata and payload.
        :param service: Callable that returns available services.
        """
        if not services:
            raise ValueError("No services available for task assignment.")

        # Select the service based on the round-robin index
        service = services[self.current_index % len(services)]
        self.task_assignments[task["task_id"]] = service
        self.current_index += 1
        return service

    def add_task(self, task: Dict[str, Any]) -> None:
        """
        Add a task to the task queue.
        :param task: Task metadata and payload.
        """
        self._task_queue.put(task)

    def remove_task(self, task_id: str) -> None:
        """
        Remove a task from the task registry.
        :param task_id: Unique identifier of the task to remove.
        """
        if task_id in self.task_assignments:
            del self.task_assignments[task_id]
            logging.info(f"Task '{task_id}' removed from assignments.")
        else:
            raise ValueError(f"Task '{task_id}' not found in assignments.")

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """
        Get a task's assigned service.
        :param task_id: Unique identifier of the task.
        :return: Task assignment details.
        """
        if task_id in self.task_assignments:
            service = self.task_assignments[task_id]
            return {"task_id": task_id, "assigned_service": service}
        else:
            raise ValueError(f"Task '{task_id}' not found in assignments.")

    def process_tasks(self, service_registry: Callable, transport: Callable) -> None:
        """
        Process tasks from the task queue and assign them to services.
        :param service_registry: Callable that returns available services.
        :param transport: Callable used to send tasks to assigned services.
        """
        while not self._task_queue.empty():
            task = self._task_queue.get()
            try:
                assigned_service = self.assign_task(task, service_registry)
                transport.send(recipient=assigned_service, message=task)
            except ValueError as e:
                raise ValueError(f"Error assigning task: {e}")

    def get_tasks(self):
        """
        Get all tasks from the task queue.
        :return: List of tasks.
        """
        return list(self._task_queue.queue)
