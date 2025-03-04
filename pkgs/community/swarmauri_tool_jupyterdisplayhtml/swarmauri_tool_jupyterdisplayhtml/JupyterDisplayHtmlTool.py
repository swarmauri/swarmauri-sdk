from typing import List, Dict, Literal
from pydantic import Field
import logging

from IPython.display import HTML, display
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)

"""
JupyterDisplayHtmlTool.py

This module defines the JupyterDisplayHtmlTool, a tool that displays HTML content within
a Jupyter Notebook cell. It inherits from the ToolBase class and supports dynamic HTML
content updates, integrates with other visualization tools, handles malformed HTML gracefully,
and returns a confirmation of the displayed output.
"""


@ComponentBase.register_type(ToolBase, "JupyterDisplayHtmlTool")
class JupyterDisplayHtmlTool(ToolBase):
    """
    JupyterDisplayHtmlTool is responsible for rendering HTML within a Jupyter Notebook cell.
    It supports dynamic updates by allowing multiple calls with new HTML content, integrates
    easily with other visualization tools, and logs the display actions and any errors
    encountered.

    Attributes:
        version (str): The version of the JupyterDisplayHtmlTool.
        parameters (List[Parameter]): A list of parameters required to render HTML content.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterDisplayHtmlTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="html_content",
                input_type="string",
                description="The HTML content to display within the Jupyter Notebook cell.",
                required=True,
            ),
        ]
    )
    name: str = "JupyterDisplayHtmlTool"
    description: str = "Renders HTML content within a Jupyter environment."
    type: Literal["JupyterDisplayHtmlTool"] = "JupyterDisplayHtmlTool"

    def __call__(self, html_content: str) -> Dict[str, str]:
        """
        Renders the provided HTML content in a Jupyter Notebook cell and returns a
        status message indicating whether the operation succeeded.

        Args:
            html_content (str): The HTML content to be rendered.

        Returns:
            Dict[str, str]: A dictionary containing 'status' and 'message' keys.
                            If successful, 'status' will be 'success' and 'message'
                            will confirm the rendered HTML. In the event of an error,
                            'status' will be 'error' and 'message' will contain
                            the error description.

        Example:
            >>> tool = JupyterDisplayHtmlTool()
            >>> result = tool("<h1>Hello, world!</h1>")
            >>> print(result)
            {'status': 'success', 'message': 'HTML displayed successfully.'}
        """
        try:
            logger.info("Attempting to display HTML content in Jupyter...")
            # Display the HTML content in the notebook cell.
            display(HTML(html_content))

            logger.info("HTML content displayed successfully.")
            return {"status": "success", "message": "HTML displayed successfully."}
        except Exception as e:
            error_msg = f"An error occurred while displaying HTML: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
