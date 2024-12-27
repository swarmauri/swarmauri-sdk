from typing import Any, Callable, List, Optional, Dict
from swarmauri_base.pipelines.PipelineBase import PipelineBase


class Pipeline(PipelineBase):
    """
    Concrete implementation of a pipeline with additional
    customization options.
    """

    type: str = "Pipeline"

    def __init__(
        self,
        tasks: Optional[List[Dict[str, Any]]] = None,
        parallel: bool = False,
        error_handler: Optional[Callable[[Exception], Any]] = None,
    ):
        """
        Initialize a customizable pipeline.

        :param tasks: Optional list of tasks to initialize pipeline with
        :param parallel: Flag to indicate parallel or sequential execution
        :param error_handler: Optional custom error handling function
        """
        super().__init__(tasks, parallel)
        self._error_handler = error_handler

    def execute(self, *args: Any, **kwargs: Any) -> List[Any]:
        """
        Execute pipeline with optional custom error handling.

        :return: List of results from pipeline execution
        """
        try:
            return super().execute(*args, **kwargs)
        except Exception as e:
            if self._error_handler:
                return [self._error_handler(e)]
            raise

    def with_error_handler(self, handler: Callable[[Exception], Any]) -> "Pipeline":
        """
        Add a custom error handler to the pipeline.

        :param handler: Error handling function
        :return: Current pipeline instance
        """
        self._error_handler = handler
        return self
