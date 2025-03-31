import subprocess as sp
import platform
from typing import List, Literal, Dict, Union
from pydantic import Field
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase

@ComponentBase.register_type(ToolBase, "TestTool")
class TestTool(ToolBase):
    version: str = "1.0.0"

    # Define the parameters required by the tool
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="program",
                input_type="string",
                description="The program to open ('notepad', 'calc', or 'paint')",
                required=True,
                enum=["notepad", "calc", "paint"],
            )
        ]
    )
    name: str = "TestTool"
    description: str = "This opens a program based on the user's request."
    type: Literal["TestTool"] = "TestTool"

    def __call__(self, program: str) -> Dict[str, str]:
        os_name = platform.system()
        # Define mappings for each OS
        commands: Dict[str, Union[str, List[str]]] = {}
        if os_name == "Windows":
            # On Windows, the commands are used directly.
            commands = {
                "notepad": "notepad",
                "calc": "calc",
                "paint": "mspaint",
            }
        elif os_name == "Darwin":
            # On macOS, we use the 'open' command with the -a flag to open applications.
            commands = {
                "notepad": ["open", "-a", "TextEdit"],
                "calc": ["open", "-a", "Calculator"],
                # macOS doesn't have an exact equivalent of MS Paint.
                # 'Preview' is used here as a placeholder.
                "paint": ["open", "-a", "Preview"],
            }
        elif os_name == "Linux":
            # For Linux, we assume some common applications.
            commands = {
                "notepad": ["gedit"],
                "calc": ["gnome-calculator"],
                # 'pinta' is often used as a simple image editor similar to MSPaint.
                "paint": ["pinta"],
            }
        else:
            return {"error": f"Unsupported OS: {os_name}"}

        # Retrieve the command based on the program parameter
        cmd = commands.get(program)
        if cmd is None:
            return {"error": f"Unsupported program: {program}"}

        try:
            # If cmd is a list (for Darwin/Linux) we pass it directly.
            # If it’s a string (as for Windows) we pass it as is.
            sp.Popen(cmd) if isinstance(cmd, list) else sp.Popen([cmd])
            return {"program": f"Program Opened: {program} on {os_name}"}
        except Exception as e:
            return {"error": f"Failed to open program: {str(e)}"}
