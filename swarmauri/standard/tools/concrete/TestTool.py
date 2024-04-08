import json
import subprocess as sp
from ..base.ToolBase import ToolBase
from .Parameter import Parameter

class TestTool(ToolBase):
    def __init__(self):
        parameters = [
            Parameter(
                name="program",
                type="string",
                description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
                required=True,
                enum=["notepad", "calc", "mspaint"]
            )
        ]
        
        super().__init__(name="TestTool", 
                         description="This opens a program based on the user's request.", 
                         parameters=parameters)

    def __call__(self, program) -> str:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Program Opened: {program}\n"
