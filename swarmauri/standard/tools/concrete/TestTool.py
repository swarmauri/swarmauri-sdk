import json
import subprocess as sp

from dataclasses import field
from swarmauri.standard.tools.base.ToolBase import ToolBase 
from swarmauri.standard.tools.concrete.Parameter import Parameter 

class TestTool(ToolBase):
    version = "1.0.0"
        
    # Define the parameters required by the tool
    parameters: List[Parameter] = field(default_factory=lambda: [
        Parameter(
            name="program",
            type="string",
            description="The program that the user wants to open ('notepad' or 'calc' or 'mspaint')",
            required=True,
            enum=["notepad", "calc", "mspaint"]
        )
    ])
    
    description="This opens a program based on the user's request."


    def __call__(self, program) -> str:
        # sp.check_output(program)
        # Here you would implement the actual logic for fetching the weather information.
        # For demonstration, let's just return the parameters as a string.
        return f"Program Opened: {program}\n"
