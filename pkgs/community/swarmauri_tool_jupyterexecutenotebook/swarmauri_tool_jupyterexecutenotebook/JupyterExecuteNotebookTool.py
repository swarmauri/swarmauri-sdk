"""
JupyterExecuteNotebookTool.py

This module defines the JupyterExecuteNotebookTool, which executes all cells
in a Jupyter notebook sequentially, capturing outputs and errors, and returns
the executed notebook object. It leverages the ToolBase and ComponentBase
classes from the swarmauri framework to integrate seamlessly with the system's
tool architecture.

The JupyterExecuteNotebookTool supports configurable execution timeouts and
handles cell execution failures gracefully. The executed NotebookNode is
updated with outputs produced during execution.
"""

import logging
from typing import List, Literal, ClassVar, Type
from pydantic import Field

from nbclient.exceptions import CellExecutionError, CellTimeoutError
from nbclient import NotebookClient

import nbformat
from nbformat.notebooknode import NotebookNode

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


@ComponentBase.register_type(ToolBase, "JupyterExecuteNotebookTool")
class JupyterExecuteNotebookTool(ToolBase):
    """
    JupyterExecuteNotebookTool is a tool that executes a Jupyter notebook by running
    all cells sequentially. It captures and logs the outputs or errors produced
    during the execution and returns the executed notebook object.

    Attributes:
        version (str): The version of the JupyterExecuteNotebookTool.
        parameters (List[Parameter]): A list of parameters required to execute the notebook.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExecuteNotebookTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_path",
                input_type="string",
                description="The path to the Jupyter notebook to be executed.",
                required=True,
            ),
            Parameter(
                name="timeout",
                input_type="number",
                description="Maximum time (in seconds) for each cell to execute. Defaults to 30.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExecuteNotebookTool"
    description: str = "Executes a Jupyter notebook and captures outputs."
    type: Literal["JupyterExecuteNotebookTool"] = "JupyterExecuteNotebookTool"

    # Expose NotebookClient as a class attribute for easier patching.
    NotebookClient: ClassVar[Type[NotebookClient]] = NotebookClient

    def __call__(self, notebook_path: str, timeout: int = 30) -> NotebookNode:
        """
        Executes the given Jupyter notebook by running all cells sequentially. Captures
        all outputs and errors, updating the NotebookNode object with the results.

        Args:
            notebook_path (str): The file path to the Jupyter notebook to execute.
            timeout (int, optional): The maximum time (in seconds) allowed for each
                                     cell to execute. Defaults to 30.

        Returns:
            NotebookNode: The notebook object after execution, containing updated
                          outputs. If cell execution fails, the error is recorded
                          in the notebook outputs.

        Example:
            >>> tool = JupyterExecuteNotebookTool()
            >>> executed_notebook = tool("example_notebook.ipynb", 60)
            >>> # The returned NotebookNode now contains the executed cells and outputs.
        """
        return self.execute_notebook(notebook_path, timeout)

    def execute_notebook(self, notebook_path: str, timeout: int = 30) -> NotebookNode:
        """
        Executes the given Jupyter notebook by running all cells sequentially. Captures
        all outputs and errors, updating the NotebookNode object with the results.

        Args:
            notebook_path (str): The file path to the Jupyter notebook to execute.
            timeout (int, optional): The maximum time (in seconds) allowed for each
                                     cell to execute. Defaults to 30.

        Returns:
            NotebookNode: The notebook object after execution, containing updated
                          outputs. If cell execution fails, the error is recorded
                          in the notebook outputs.
        """
        logger.info("Starting notebook execution with JupyterExecuteNotebookTool.")
        logger.debug(f"Notebook path: {notebook_path}")
        logger.debug(f"Execution timeout: {timeout} seconds")

        try:
            with open(notebook_path, "r", encoding="utf-8") as f:
                notebook: NotebookNode = nbformat.read(f, nbformat.NO_CONVERT)

            # Create a client to execute the notebook
            client = NotebookClient(
                notebook,
                timeout=timeout,
                kernel_name="python3",
                allow_errors=True,  # Continue execution even if a cell fails
            )

            logger.info("Executing notebook cells...")
            client.execute()
            logger.info("Notebook execution completed successfully.")
            return notebook

        except (CellExecutionError, CellTimeoutError) as e:
            logger.error("A cell execution error occurred.")
            logger.exception(e)
            # The executed notebook still contains partial output and the error details.
            return notebook

        except Exception as e:
            logger.error("An unexpected error occurred during notebook execution.")
            logger.exception(e)
            # Return the partially executed or unmodified notebook in case of failure.
            return notebook
