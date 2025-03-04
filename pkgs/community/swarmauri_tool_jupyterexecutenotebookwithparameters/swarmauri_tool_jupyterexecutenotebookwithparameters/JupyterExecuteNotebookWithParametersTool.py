from typing import List, Literal, Dict, Any, Optional
import logging
import papermill as pm
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)

"""
JupyterExecuteNotebookWithParametersTool.py

This module defines the JupyterExecuteNotebookWithParametersTool, a component that executes Jupyter
notebooks using papermill, injecting custom parameters, capturing execution logs, and returning
the path to the executed notebook output. It inherits from ToolBase and integrates seamlessly
with the Swarmauri framework.
"""


@ComponentBase.register_type(ToolBase, "JupyterExecuteNotebookWithParametersTool")
class JupyterExecuteNotebookWithParametersTool(ToolBase):
    """
    JupyterExecuteNotebookWithParametersTool is a tool that executes Jupyter notebooks with custom
    parameter injection using papermill. This tool captures execution logs, errors, and returns
    the path to the resulting executed notebook. It can be utilized within CI/CD pipelines when
    batch processing multiple notebooks.

    Attributes:
        version (str): The version of the JupyterExecuteNotebookWithParametersTool.
        parameters (List[Parameter]): A list of parameters the tool expects, including notebook_path,
                                      output_notebook_path, and params.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExecuteNotebookWithParametersTool"]): The type identifier.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_path",
                input_type="string",
                description="The path to the Jupyter Notebook file to execute.",
                required=True,
            ),
            Parameter(
                name="output_notebook_path",
                input_type="string",
                description="The path where the output notebook will be saved.",
                required=True,
            ),
            Parameter(
                name="params",
                input_type="object",
                description="A dictionary of parameters to inject into the notebook.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExecuteNotebookWithParametersTool"
    description: str = "Executes Jupyter notebooks with papermill, injecting parameters and capturing outputs."
    type: Literal["JupyterExecuteNotebookWithParametersTool"] = (
        "JupyterExecuteNotebookWithParametersTool"
    )

    def __call__(
        self,
        notebook_path: str,
        output_notebook_path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Executes the specified Jupyter notebook using papermill, injecting the provided parameters
        and saving the executed notebook to the specified output path.

        Args:
            notebook_path (str): The path to the Jupyter Notebook file to be executed.
            output_notebook_path (str): The path where the executed notebook will be saved.
            params (Optional[Dict[str, Any]]): A dictionary of parameters to inject into the notebook.

        Returns:
            Dict[str, str]: A dictionary containing information about the execution result. If
                            successful, it includes the key 'executed_notebook' pointing to the
                            output notebook path. If an error occurs, the dictionary contains an
                            'error' key with a descriptive message.

        Raises:
            ValueError: If the notebook_path is not a .ipynb file.
        """
        logger.info(
            "Starting notebook execution with JupyterExecuteNotebookWithParametersTool."
        )
        logger.debug(
            "notebook_path: %s, output_notebook_path: %s, params: %s",
            notebook_path,
            output_notebook_path,
            params,
        )

        if not notebook_path.endswith(".ipynb"):
            error_message = "The specified notebook_path is not a .ipynb file."
            logger.error(error_message)
            return {"error": error_message}

        if not output_notebook_path.endswith(".ipynb"):
            error_message = "The specified output_notebook_path is not a .ipynb file."
            logger.error(error_message)
            return {"error": error_message}

        try:
            pm.execute_notebook(
                input_path=notebook_path,
                output_path=output_notebook_path,
                parameters=params or {},
            )
            logger.info("Notebook execution completed successfully.")
            return {"executed_notebook": output_notebook_path}
        except Exception as e:
            error_message = f"An error occurred during notebook execution: {str(e)}"
            logger.error(error_message)
            return {"error": error_message}
