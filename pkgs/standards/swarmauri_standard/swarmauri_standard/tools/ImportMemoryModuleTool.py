from swarmauri_core.typing import SubclassUnion
import sys
import types
import importlib
from typing import List, Literal, Dict
from pydantic import Field
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


class ImportMemoryModuleTool(ToolBase):
    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="name",
                type="string",
                description="Name of the new module.",
                required=True,
            ),
            Parameter(
                name="code",
                type="string",
                description="Python code snippet to include in the module.",
                required=True,
            ),
            Parameter(
                name="package_path",
                type="string",
                description="Dot-separated package path where the new module should be inserted.",
                required=True,
            ),
        ]
    )

    name: str = "ImportMemoryModuleTool"
    description: str = (
        "Dynamically imports a module from memory into a specified package path."
    )
    type: Literal["ImportMemoryModuleTool"] = "ImportMemoryModuleTool"

    def __call__(self, name: str, code: str, package_path: str) -> Dict[str, str]:
        """
        Dynamically creates a module from a code snippet and inserts it into the specified package path.

        Args:
            name (str): Name of the new module.
            code (str): Python code snippet to include in the module.
            package_path (str): Dot-separated package path where the new module should be inserted.
        """
        # Implementation adapted from the provided snippet
        # Ensure the package structure exists
        current_package = self.ensure_module(package_path)

        # Create a new module
        module = types.ModuleType(name)

        # Execute code in the context of this new module
        exec(code, module.__dict__)

        # Insert the new module into the desired location
        setattr(current_package, name, module)
        sys.modules[package_path + "." + name] = module
        return {"message": f"{name} has been successfully imported into {package_path}"}

    @staticmethod
    def ensure_module(package_path: str):
        package_parts = package_path.split(".")
        module_path = ""
        current_module = None

        for part in package_parts:
            if module_path:
                module_path += "." + part
            else:
                module_path = part

            if module_path not in sys.modules:
                try:
                    # Try importing the module; if it exists, this will add it to sys.modules
                    imported_module = importlib.import_module(module_path)
                    sys.modules[module_path] = imported_module
                except ImportError:
                    # If the module doesn't exist, create a new placeholder module
                    new_module = types.ModuleType(part)
                    if current_module:
                        setattr(current_module, part, new_module)
                    sys.modules[module_path] = new_module
            current_module = sys.modules[module_path]

        return current_module


SubclassUnion.update(
    baseclass=ToolBase, type_name="ImportMemoryModuleTool", obj=ImportMemoryModuleTool
)
