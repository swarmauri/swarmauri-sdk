from typing import Any, Callable, List, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.pipelines.IPipeline import IPipeline, PipelineStatus
import uuid


class PipelineBase(IPipeline, ComponentBase):
    """
    Base class providing default behavior for task orchestration,
    error handling, and result aggregation.
    """

    resource: Optional[str] = Field(default=ResourceTypes.PIPELINE.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: str = "PipelineBase"

    # Pydantic model fields
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    parallel: bool = Field(default=False)

    def __init__(
        self, tasks: Optional[List[Dict[str, Any]]] = None, parallel: bool = False
    ):
        """
        Initialize the pipeline.

        :param tasks: Optional list of tasks to initialize pipeline with
        :param parallel: Flag to indicate parallel or sequential execution
        """
        super().__init__()
        self.tasks = tasks or []
        self._results: List[Any] = []
        self._status: PipelineStatus = PipelineStatus.PENDING
        self.parallel = parallel

    def add_task(self, task: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Add a task to the pipeline.

        :param task: Callable task to be executed
        :param args: Positional arguments for the task
        :param kwargs: Keyword arguments for the task
        """
        task_entry = {"callable": task, "args": args, "kwargs": kwargs}
        self.tasks.append(task_entry)

    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Execute pipeline tasks.

        :return: List of results from pipeline execution
        """
        try:
            self._status = PipelineStatus.RUNNING
            self._results = []

            if self.parallel:
                # Implement parallel execution logic
                from concurrent.futures import ThreadPoolExecutor

                with ThreadPoolExecutor() as executor:
                    futures = [
                        executor.submit(
                            task["callable"], *task["args"], **task["kwargs"]
                        )
                        for task in self.tasks
                    ]
                    self._results = [future.result() for future in futures]
            else:
                # Sequential execution
                for task in self.tasks:
                    result = task["callable"](*task["args"], **task["kwargs"])
                    self._results.append(result)

            self._status = PipelineStatus.COMPLETED
            return self._results

        except Exception as e:
            self._status = PipelineStatus.FAILED
            raise RuntimeError(f"Pipeline execution failed: {e}")

    def get_status(self) -> PipelineStatus:
        """
        Get the current status of the pipeline.

        :return: Current pipeline status
        """
        return self._status

    def reset(self) -> None:
        """
        Reset the pipeline to its initial state.
        """
        self._results = []
        self._status = PipelineStatus.PENDING

    def get_results(self) -> List[Any]:
        """
        Get the results of the pipeline execution.

        :return: List of results
        """
        return self._results
