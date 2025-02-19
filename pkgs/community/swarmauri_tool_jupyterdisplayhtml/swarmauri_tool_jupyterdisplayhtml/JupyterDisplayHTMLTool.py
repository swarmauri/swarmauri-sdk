from typing import List, Dict, Literal
from pydantic import Field
import logging

from IPython.display import HTML, display
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

logger = logging.getLogger(__name__)


"""
JupyterDisplayHTMLTool.py

This module defines the JupyterDisplayHTMLTool, a tool that displays HTML content within
a Jupyter Notebook cell. It inherits from the ToolBase class and supports dynamic HTML
content updates, integrates with other visualization tools, handles malformed HTML gracefully,
and returns a confirmation of the displayed output.
"""


@ComponentBase.register_type(ToolBase, "JupyterDisplayHTMLTool")
class JupyterDisplayHTMLTool(ToolBase):
    """
    JupyterDisplayHTMLTool is responsible for rendering HTML within a Jupyter Notebook cell.
    It supports dynamic updates by allowing multiple calls with new HTML content, integrates
    easily with other visualization tools, and logs the display actions and any errors
    encountered.

    Attributes:
        version (str): The version of the JupyterDisplayHTMLTool.
        parameters (List[Parameter]): A list of parameters required to render HTML content.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterDisplayHTMLTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="html_content",
                type="string",
                description="The HTML content to display within the Jupyter Notebook cell.",
                required=True,
            ),
        ]
    )
    name: str = "JupyterDisplayHTMLTool"
    description: str = "Renders HTML content within a Jupyter environment."
    type: Literal["JupyterDisplayHTMLTool"] = "JupyterDisplayHTMLTool"

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
            >>> tool = JupyterDisplayHTMLTool()
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
