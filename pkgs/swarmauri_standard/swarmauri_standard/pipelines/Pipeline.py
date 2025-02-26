import warnings

from typing import Any, Callable, List

from swarmauri_base.pipelines.PipelineBase import PipelineBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(PipelineBase, "Pipeline")
class Pipeline(PipelineBase):
    """
    Concrete implementation of a pipeline with additional
    customization options.
    """

    type: str = "Pipeline"

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
