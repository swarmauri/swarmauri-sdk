from swarmauri_core.typing import SubclassUnion
import sys
import io
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class CodeInterpreterTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="user_code",
                type="string",
                description=(
                    "Executes the provided Python code snippet in a secure sandbox environment. "
                    "This tool is designed to interpret the execution of the python code snippet."
                    "Returns the output"
                ),
                required=True,
            )
        ]
    )
    name: str = "CodeInterpreterTool"
    description: str = "Executes provided Python code and captures its output."
    type: Literal["CodeInterpreterTool"] = "CodeInterpreterTool"

    def __call__(self, user_code: str) -> Dict[str, str]:
        """
        Executes the provided user code and captures its stdout output.

        Parameters:
            user_code (str): Python code to be executed.

        Returns:
            str: Captured output or error message from the executed code.
        """
        return {"code_output": self.execute_code(user_code)}

    def execute_code(self, user_code: str) -> str:
        """
        Executes the provided user code and captures its stdout output.

        Args:
            user_code (str): Python code to be executed.

        Returns:
            str: Captured output or error message from the executed code.
        """
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        try:
            # Note: Consider security implications of using 'exec'
            builtins = globals().copy()
            exec(user_code, builtins)
            sys.stdout = old_stdout
            captured_output = redirected_output.getvalue()
            return str(captured_output)
        except Exception as e:
            sys.stdout = old_stdout
            return f"An error occurred: {str(e)}"


SubclassUnion.update(
    baseclass=ToolBase, type_name="CodeInterpreterTool", obj=CodeInterpreterTool
)
