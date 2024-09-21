from celery import Celery
from swarmauri.core.agent_apis.IAgentCommands import IAgentCommands
from typing import Callable, Any, Dict

class CeleryAgentCommands(IAgentCommands):
    def __init__(self, broker_url: str, backend_url: str):
        """
        Initializes the Celery application with the specified broker and backend URLs.
        """
        self.app = Celery('swarmauri_agent_tasks', broker=broker_url, backend=backend_url)

    def register_command(self, command_name: str, function: Callable[..., Any], *args, **kwargs) -> None:
        """
        Registers a new command as a Celery task.
        """
        self.app.task(name=command_name, bind=True)(function)

    def execute_command(self, command_name: str, *args, **kwargs) -> Any:
        """
        Executes a registered command by name asynchronously.
        """
        result = self.app.send_task(command_name, args=args, kwargs=kwargs)
        return result.get()

    def get_status(self, task_id: str) -> Dict[str, Any]:
        """
        Fetches the status of a command execution via its task ID.
        """
        async_result = self.app.AsyncResult(task_id)
        return {"status": async_result.status, "result": async_result.result if async_result.ready() else None}

    def revoke_command(self, task_id: str) -> None:
        """
        Revokes or terminates a command execution by its task ID.
        """
        self.app.control.revoke(task_id, terminate=True) 