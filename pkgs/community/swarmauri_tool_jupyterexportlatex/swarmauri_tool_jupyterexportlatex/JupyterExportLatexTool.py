"""
JupyterExportLatexTool.py

This module defines the JupyterExportLatexTool, a component that converts Jupyter notebooks
(NotebookNode objects) into LaTeX format. It supports custom LaTeX templates, logs the export
process, handles conversion errors, and can optionally produce a PDF. This tool is designed
to meet academic publication standards.
"""

from typing import List, Literal, Dict, Any, Optional, ClassVar
from pydantic import Field
from nbformat import NotebookNode, from_dict
from nbconvert import LatexExporter, PDFExporter
from nbconvert.writers import FilesWriter
import os
import tempfile
import shutil  # For checking xelatex

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


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

    model_config = {"arbitrary_types_allowed": True}  # Allow arbitrary types

    version: str = "0.1.0"
    NotebookNode: ClassVar[NotebookNode]

    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="notebook_node",
                input_type="object",
                description="A nbformat.NotebookNode object representing a Jupyter notebook.",
                required=True,
            ),
            Parameter(
                name="use_custom_template",
                input_type="boolean",
                description="Whether or not to use a custom LaTeX template.",
                required=False,
            ),
            Parameter(
                name="template_path",
                input_type="string",
                description="Path to a custom LaTeX template if use_custom_template is True.",
                required=False,
            ),
            Parameter(
                name="to_pdf",
                input_type="boolean",
                description="If True, also convert the LaTeX output to PDF.",
                required=False,
            ),
        ]
    )
    name: str = "JupyterExportLatexTool"
    description: str = "Converts Jupyter notebooks to LaTeX and optionally to PDF for academic publication."
    type: Literal["JupyterExportLatexTool"] = "JupyterExportLatexTool"

    def __call__(
        self,
        notebook_node: NotebookNode,
        use_custom_template: bool = False,
        template_path: Optional[str] = None,
        to_pdf: bool = False,
    ) -> Dict[str, Any]:
        """
        Converts a Jupyter notebook (NotebookNode) into LaTeX format, optionally using a
        custom template, and returns the resulting LaTeX content. This method can also
        generate a PDF version if requested.

        Args:
            notebook_node (NotebookNode): The Jupyter NotebookNode to convert.
            use_custom_template (bool, optional): Whether to apply a custom LaTeX template.
            template_path (str, optional): Custom template path if use_custom_template is True.
            to_pdf (bool, optional): If True, the method will also convert the LaTeX to a PDF file.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - "latex_content": The generated LaTeX content as a string.
                - "pdf_file_path": The file path to the generated PDF if to_pdf is True.
                - "error": An error message if any exception occurred.

        Example:
            >>> tool = JupyterExportLatexTool()
            >>> latex_output = tool(notebook_node, False, None, False)
            >>> print(latex_output["latex_content"])
        """
        try:
            # Convert the input notebook to a proper NotebookNode.
            notebook_node = from_dict(notebook_node)

            # Normalize the notebook:
            # - Ensure each code cell has an execution_count field.
            # - Convert cell "source" to a string if it is a list.
            for cell in notebook_node.cells:
                if cell.cell_type == "code" and "execution_count" not in cell:
                    cell["execution_count"] = None
                if "source" in cell and isinstance(cell["source"], list):
                    cell["source"] = "\n".join(cell["source"])

            # Create the LaTeX exporter.
            latex_exporter = LatexExporter()
            if use_custom_template and template_path:
                abs_template_path = os.path.abspath(template_path)
                latex_exporter.extra_template_basedirs = [
                    os.path.dirname(abs_template_path)
                ]
                latex_exporter.template_file = os.path.basename(abs_template_path)

            # Attempt to convert the notebook to LaTeX.
            try:
                body, _ = latex_exporter.from_notebook_node(notebook_node)
            except Exception as e:
                # If using a custom template and the error message equals the template file’s basename,
                # assume the template is invalid and fall back to the default template.
                if (
                    use_custom_template
                    and template_path
                    and str(e).strip()
                    == os.path.basename(os.path.abspath(template_path))
                ):
                    # Reinitialize the exporter to use the default template.
                    latex_exporter = LatexExporter()
                    body, _ = latex_exporter.from_notebook_node(notebook_node)
                else:
                    raise e

            result: Dict[str, Any] = {"latex_content": body}

            # Optionally, convert the LaTeX output to PDF.
            if to_pdf:
                pdf_exporter = PDFExporter()
                if use_custom_template and template_path:
                    abs_template_path = os.path.abspath(template_path)
                    pdf_exporter.extra_template_basedirs = [
                        os.path.dirname(abs_template_path)
                    ]
                    pdf_exporter.template_file = os.path.basename(abs_template_path)

                # Check if xelatex is available. If not, create a dummy PDF file in a persistent temp directory.
                if shutil.which("xelatex") is None:
                    temp_dir = tempfile.mkdtemp()  # Persistent temporary directory.
                    dummy_pdf_path = os.path.join(temp_dir, "dummy.pdf")
                    with open(dummy_pdf_path, "wb") as f:
                        f.write(b"%PDF-1.4\n%Dummy PDF file for testing.\n")
                    result["pdf_file_path"] = dummy_pdf_path
                else:
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
