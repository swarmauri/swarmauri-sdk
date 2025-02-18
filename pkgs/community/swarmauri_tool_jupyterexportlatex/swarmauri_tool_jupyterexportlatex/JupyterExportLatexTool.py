"""
JupyterExportLatexTool.py

This module defines the JupyterExportLatexTool, a component that converts Jupyter notebooks
(NotebookNode objects) into LaTeX format. It supports custom LaTeX templates, logs the export
process, handles conversion errors, and can optionally produce a PDF. This tool is designed
to meet academic publication standards.
"""

from typing import List, Literal, Dict, Any, Optional
from pydantic import Field
from nbformat import NotebookNode, from_dict
from nbconvert import LatexExporter, PDFExporter
from nbconvert.writers import FilesWriter
import os
import tempfile

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase


@ComponentBase.register_type(ToolBase, "JupyterExportLatexTool")
class JupyterExportLatexTool(ToolBase):
    """
    JupyterExportLatexTool is responsible for converting a Jupyter Notebook (NotebookNode)
    into a LaTeX document. It supports using a custom LaTeX template, can log and handle
    conversion errors, and optionally convert the generated LaTeX to PDF.

    Attributes:
        version (str): The version of the JupyterExportLatexTool.
        parameters (List[Parameter]): A list of parameters required to perform the export.
        name (str): The name of the tool.
        description (str): A brief description of the tool's functionality.
        type (Literal["JupyterExportLatexTool"]): The type identifier for the tool.
    """

    version: str = "0.1.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_node",
                type="object",
                description="A nbformat.NotebookNode object representing a Jupyter notebook.",
                required=True,
            ),
            Parameter(
                name="use_custom_template",
                type="boolean",
                description="Whether or not to use a custom LaTeX template.",
                required=False,
            ),
            Parameter(
                name="template_path",
                type="string",
                description="Path to a custom LaTeX template if use_custom_template is True.",
                required=False,
            ),
            Parameter(
                name="to_pdf",
                type="boolean",
                description="If True, also convert the LaTeX output to PDF.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExportLatexTool"
    description: str = "Converts Jupyter notebooks to LaTeX and optionally to PDF for academic publication."
    type: Literal["JupyterExportLatexTool"] = "JupyterExportLatexTool"

    from nbformat import NotebookNode, from_dict  # make sure to import from_dict

    def __call__(
        self,
        notebook_node: NotebookNode,
        use_custom_template: bool = False,
        template_path: Optional[str] = None,
        to_pdf: bool = False,
    ) -> Dict[str, Any]:
        try:
            # Convert the input notebook to a proper NotebookNode.
            notebook_node = from_dict(notebook_node)

            # Normalize the notebook: ensure each code cell has an execution_count field.
            for cell in notebook_node.cells:
                if cell.cell_type == "code" and "execution_count" not in cell:
                    cell["execution_count"] = None

            # Create the LaTeX exporter.
            latex_exporter = LatexExporter()
            if use_custom_template and template_path:
                latex_exporter.template_file = template_path

            # Convert the notebook to LaTeX.
            body, _ = latex_exporter.from_notebook_node(notebook_node)
            result: Dict[str, Any] = {"latex_content": body}

            # Optionally, convert the LaTeX output to PDF.
            if to_pdf:
                pdf_exporter = PDFExporter()
                if use_custom_template and template_path:
                    pdf_exporter.template_file = template_path

                with tempfile.TemporaryDirectory() as temp_dir:
                    pdf_exporter.output_filename = "converted_notebook.pdf"
                    pdf_data, _ = pdf_exporter.from_notebook_node(notebook_node)

                    writer = FilesWriter(build_directory=temp_dir)
                    writer.write(pdf_data, pdf_exporter.output_filename)
                    pdf_path = os.path.join(temp_dir, pdf_exporter.output_filename)
                    result["pdf_file_path"] = pdf_path

            return result
        except Exception as e:
            return {"error": f"An error occurred during LaTeX export: {str(e)}"}
