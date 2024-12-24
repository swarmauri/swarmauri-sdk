from swarmauri_core.typing import SubclassUnion
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class TestTool(ToolBase):
    version: str = "1.0.0"

    # Define the parameters required by the tool
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="program",
                type="string",
                description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
                required=True,
                enum=["notepad", "calc", "mspaint"],
            )
        ]
    )
    name: str = "TestTool"
    description: str = "This opens a program based on the user's request."
    type: Literal["TestTool"] = "TestTool"

    def __call__(self, program) -> Dict[str, str]:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return {"program": f"Program Opened: {program}"}


SubclassUnion.update(baseclass=ToolBase, type_name="TestTool", obj=TestTool)
