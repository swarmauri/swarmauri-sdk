"""
JupyterDisplayTool.py

This module defines the JupyterDisplayTool, a component that leverages IPython display
functionality to render data with a variety of rich representations. It inherits from
ToolBase and integrates with the swarmauri framework's tool architecture.
"""

import logging
from typing import List, Dict, Literal
from pydantic import Field
import IPython.display as ipyd  # Updated import to use namespace

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "JupyterDisplayTool")
class JupyterDisplayTool(ToolBase):
    """
    JupyterDisplayTool is a tool that displays data in a Jupyter environment using IPython's
    rich display capabilities. It supports multiple data formats, including plain text, HTML,
    images, and LaTeX.

    Attributes:
        version (str): The version of the JupyterDisplayTool.
        parameters (List[Parameter]): A list of parameters defining the expected inputs.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterDisplayTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="data",
                input_type="string",
                description="The data to be displayed. Accepts text, HTML, image paths, or LaTeX content.",
                required=True,
            ),
            Parameter(
                name="data_format",
                input_type="string",
                description="The format of the data ('auto', 'text', 'html', 'image', or 'latex').",
                required=False,
                default="auto",
                enum=["auto", "text", "html", "image", "latex"],
            ),
        ]
    )
    name: str = "JupyterDisplayTool"
    description: str = "Displays data in a Jupyter environment using IPython's rich display capabilities."
    type: Literal["JupyterDisplayTool"] = "JupyterDisplayTool"

    def __call__(self, data: str, data_format: str = "auto") -> Dict[str, str]:
        """
        Renders the provided data in the Jupyter environment using IPython's display.

        Args:
            data (str): The data to be displayed. Could be text, HTML, a path to an image, or LaTeX.
            data_format (str, optional): The format of the data. Defaults to 'auto'. Supported
                                         values are 'text', 'html', 'image', and 'latex'.

        Returns:
            Dict[str, str]: A dictionary containing the status of the operation ("success" or "error")
                            and a corresponding message.

        Example:
            >>> display_tool = JupyterDisplayTool()
            >>> display_tool("<b>Hello, world!</b>", "html")
            {'status': 'success', 'message': 'Data displayed successfully.'}
        """
        logger = logging.getLogger(__name__)
        logger.debug("Attempting to display data with data_format=%s", data_format)

        try:
            if data_format == "html":
                ipyd.display(ipyd.HTML(data))
            elif data_format == "latex":
                ipyd.display(ipyd.Latex(data))
            elif data_format == "image":
                # If data is a path to an image, display it. Otherwise, it may fail.
                ipyd.display(ipyd.Image(data))
            elif data_format == "text":
                ipyd.display(ipyd.Markdown(data))
            else:
                # 'auto' or anything else defaults to treating the data as text
                ipyd.display(ipyd.Markdown(data))

            logger.debug("Data displayed successfully.")
            return {"status": "success", "message": "Data displayed successfully."}

        except Exception as e:
            error_message = f"Error displaying data: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "message": error_message}
