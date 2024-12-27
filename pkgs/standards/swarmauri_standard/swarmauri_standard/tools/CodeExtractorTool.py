from swarmauri_core.typing import SubclassUnion
import ast
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class CodeExtractorTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="file_name",
                type="string",
                description="The name of the Python file to extract code from.",
                required=True,
            ),
            Parameter(
                name="extract_documentation",
                type="bool",
                description="Whether to start extracting code from the documentation string.",
                required=False,
                default=True,
            ),
            Parameter(
                name="to_be_ignored",
                type="list",
                description="A list of function or variable names to be ignored during code extraction.",
                required=False,
                default=[],
            ),
        ]
    )
    name: str = "CodeExtractorTool"
    description: str = "Extracts code from a Python file."
    type: Literal["CodeExtractorTool"] = "CodeExtractorTool"

    def __call__(
        self,
        file_name: str,
        extract_documentation: bool = True,
        to_be_ignored: List[str] = [],
    ) -> Dict[str, str]:
        """
        Extracts code from a Python file.

        Parameters:
            file_name (str): The name of the Python file to extract code from.
            extract_documentation (bool): Whether to start extracting code from the documentation string.
            to_be_ignored (List[str]): A list of function or variable names to be ignored during code extraction.

        Returns:
            str: Extracted code.
        """
        return {
            "code": self.extract_code(file_name, extract_documentation, to_be_ignored)
        }

    def extract_code(
        self,
        file_name: str,
        extract_documentation: bool = True,
        to_be_ignored: List[str] = [],
    ) -> str:
        """
        Extracts code from a Python file.

        Args:
            file_name (str): The name of the Python file to extract code from.
            extract_documentation (bool): Whether to start extracting code from the documentation string.
            to_be_ignored (List[str]): A list of function or variable names to be ignored during code extraction.

        Returns:
            str: Extracted code.
        """
        response_lines = []

        # Read the current file and collect relevant lines
        with open(file_name, "r", encoding="utf-8") as f:
            documentation_start = False
            first = not extract_documentation

            for line in f:
                stripped_line = line.strip()

                # Check if the line starts or ends the documentation string
                if first and '"""' in stripped_line:
                    documentation_start = not documentation_start
                    first = False
                    continue

                if documentation_start and '"""' in stripped_line:
                    documentation_start = not documentation_start
                    continue

                if documentation_start and not extract_documentation:
                    continue

                # Stop collecting lines when reaching the specified comment
                if "#" in stripped_line and "non-essentials" in stripped_line:
                    break

                # Collect the line
                response_lines.append(line)

        response = "".join(response_lines)

        # Parse the response with AST
        tree = ast.parse(response)

        # Filter out nodes based on the `to_be_ignored` set
        class CodeCleaner(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if any(pattern in node.name for pattern in to_be_ignored):
                    return None
                return node

            def visit_Assign(self, node):
                if any(
                    isinstance(target, ast.Name)
                    and any(pattern in target.id for pattern in to_be_ignored)
                    for target in node.targets
                ):
                    return None
                return node

        # Transform the AST to remove ignored nodes
        cleaned_tree = CodeCleaner().visit(tree)

        # Convert the cleaned AST back to source code
        cleaned_code = ast.unparse(cleaned_tree)

        # Return the cleaned code
        return cleaned_code


SubclassUnion.update(
    baseclass=ToolBase, type_name="CodeExtractorTool", obj=CodeExtractorTool
)
