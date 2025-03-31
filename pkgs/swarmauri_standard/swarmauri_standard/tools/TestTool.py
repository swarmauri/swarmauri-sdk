import platform
import subprocess as sp
from typing import Dict, List, Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ToolBase import ToolBase

from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "TestTool")
class TestTool(ToolBase):
    version: str = "1.0.0"

    # Define the parameters required by the tool
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="program",
                input_type="string",
                description="The program that the user wants to open",
                required=True,
                enum=["notepad", "calc", "mspaint"],
            )
        ]
    )
    name: str = "TestTool"
    description: str = "This opens a program based on the user's request."
    type: Literal["TestTool"] = "TestTool"

    def __call__(self, program) -> Dict[str, str]:
        # Map Windows program names to macOS equivalents

        system = platform.system().lower()
        if system == "darwin":  # macOS
            if program == "notepad":
                sp.Popen(["open", "-a", "TextEdit"])
            elif program == "calc":
                sp.Popen(["open", "-a", "Calculator"])
            elif program == "mspaint":
                sp.Popen(["open", "-a", "Preview"])
        elif system == "linux":
            if program == "notepad":
                sp.Popen(["gedit"])
            elif program == "calc":
                sp.Popen(["gnome-calculator"])
            elif program == "mspaint":
                sp.Popen(["gimp"])
        else:  # Windows or other
            sp.Popen([program])

        return {"program": f"Program Opened: {program}"}
