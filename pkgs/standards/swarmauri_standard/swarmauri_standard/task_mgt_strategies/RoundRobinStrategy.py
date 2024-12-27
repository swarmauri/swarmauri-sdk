from typing import Callable, Dict, Any, List
from swarmauri_base.task_mgt_strategies.TaskMgtStrategyBase import TaskMgtStrategyBase
from queue import Queue
import logging


class RoundRobinStrategy(TaskMgtStrategyBase):
    """Round-robin task assignment strategy."""

    task_queue: Queue = Queue()  # Synchronous task queue for incoming tasks
    task_assignments: Dict[str, str] = {}  # Tracks task assignments
    current_index: int = 0  # Tracks the next service to assign tasks to

    def assign_task(self, task: Dict[str, Any], service_registry: Callable[[], List[str]]) -> None:
        """
        Assign a task to a service using the round-robin strategy.
        :param task: Task metadata and payload.
        :param service_registry: Callable that returns available services.
        """
        available_services = service_registry()
        if not available_services:
            raise ValueError("No services available for task assignment.")

        # Select the service based on the round-robin index
        service = available_services[self.current_index % len(available_services)]
        self.task_assignments[task["task_id"]] = service
        self.current_index += 1
        logging.info(f"Task '{task['task_id']}' assigned to service '{service}'.")

    def add_task(self, task: Dict[str, Any]) -> None:
        """
        Add a task to the task queue.
        :param task: Task metadata and payload.
        """
        self.task_queue.put(task)

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

    def process_tasks(self, service_registry: Callable[[], List[str]], transport: Callable) -> None:
        """
        Process tasks from the task queue and assign them to services.
        :param service_registry: Callable that returns available services.
        :param transport: Callable used to send tasks to assigned services.
        """
        while not self.task_queue.empty():
            task = self.task_queue.get()
            try:
                self.assign_task(task, service_registry)
                assigned_service = self.task_assignments[task["task_id"]]
                transport.send(task, assigned_service)
            except ValueError as e:
                raise ValueError(f"Error assigning task: {e}")
