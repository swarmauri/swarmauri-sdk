"""
JupyterExportHtmlTool.py

This module defines the JupyterExportHtmlTool, a component responsible for converting Jupyter
Notebook content into HTML format. The tool leverages nbconvert to generate HTML output and
optionally allows applying a custom HTML template, as well as embedding additional CSS or JS.
Logging is used to record export operations and errors.
"""

import logging
from typing import List, Literal, Dict, Optional

import nbformat
from nbconvert import HTMLExporter
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "JupyterExportHtmlTool")
class JupyterExportHtmlTool(ToolBase):
    """
    JupyterExportHtmlTool is a tool that converts a Jupyter Notebook (provided as a JSON string)
    into an HTML document. It supports using a custom template file, as well as optionally
    embedding CSS and JS directly into the generated HTML output.

    Attributes:
        version (str): The version of the JupyterExportHtmlTool.
        parameters (List[Parameter]): A list of parameters that specify the tool's expected inputs
                                      for the conversion process.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExportHtmlTool"]): The type identifier for the tool.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_json",
                input_type="string",
                description="A JSON string representation of the Jupyter Notebook to be exported.",
                required=True,
            ),
            Parameter(
                name="template_file",
                input_type="string",
                description="Path to an optional nbconvert-compatible template file for custom HTML formatting.",
                required=False,
            ),
            Parameter(
                name="extra_css",
                input_type="string",
                description="Inline CSS to embed into the generated HTML. Inserted within <style> tags in the document head.",
                required=False,
            ),
            Parameter(
                name="extra_js",
                input_type="string",
                description="Inline JavaScript to embed into the generated HTML. Inserted within <script> tags in the document head.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExportHtmlTool"
    description: str = "Converts Jupyter Notebooks into HTML format with optional custom template, CSS, and JS."
    type: Literal["JupyterExportHtmlTool"] = "JupyterExportHtmlTool"

    def __call__(
        self,
        notebook_json: str,
        template_file: Optional[str] = None,
        extra_css: Optional[str] = None,
        extra_js: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Converts a Jupyter Notebook (provided as a JSON string) into HTML format.

        Args:
            notebook_json (str): The JSON string representation of the Jupyter Notebook.
            template_file (Optional[str]): An optional nbconvert-compatible template file path.
            extra_css (Optional[str]): Inline CSS to be embedded in the generated HTML.
            extra_js (Optional[str]): Inline JavaScript to be embedded in the generated HTML.

        Returns:
            Dict[str, str]: A dictionary containing either:
                - "exported_html": The generated HTML as a string, if successful.
                - "error": An error message describing any issues encountered during export.

        Example:
            >>> exporter = JupyterExportHtmlTool()
            >>> result = exporter(notebook_json='{"cells":[],"metadata":{}}', template_file=None)
            >>> html_output = result.get("exported_html", "")
        """
        try:
            # Parse the notebook JSON into a NotebookNode
            nb_node = nbformat.reads(notebook_json, as_version=4)

            # Create an HTMLExporter instance
            html_exporter = HTMLExporter()

            # If a template file is provided, set it for the exporter
            if template_file:
                html_exporter.template_file = template_file

            # Convert the notebook to HTML
            body, _ = html_exporter.from_notebook_node(nb_node)

            # If extra CSS is provided, embed it in the <head> section
            if extra_css:
                css_tag = f"<style>\n{extra_css}\n</style>\n</head>"
                body = body.replace("</head>", css_tag, 1)

            # If extra JS is provided, embed it before the closing </body> tag
            if extra_js:
                js_tag = f"<script>\n{extra_js}\n</script>\n</body>"
                body = body.replace("</body>", js_tag, 1)

            logging.info("Notebook successfully exported to HTML.")
            return {"exported_html": body}

        except Exception as e:
            logging.error("Error exporting notebook to HTML: %s", e)
            return {"error": f"An error occurred: {str(e)}"}
