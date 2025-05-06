import inspect
from typing import get_type_hints, List, Any
from pydantic import Field

from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_base.ComponentBase import ComponentBase


def tool(func):
    """
    Decorator that creates a dynamic ToolBase subclass from the decorated function.

    The generated tool will:
    - Use the function name as the `name` and `type` of the tool.
    - Derive parameters from the function's signature and type hints.
    - Use the function's docstring as the tool's description.
    """
    # Capture function name and docstring
    func_name = func.__name__
    docstring = func.__doc__ or ""

    # Inspect the function signature for parameter names, defaults, etc.
    signature = inspect.signature(func)
    type_hints = get_type_hints(func)

    # Build the list of Parameter objects from the function signature
    parameters_list: List[Parameter] = []
    for param_name, param in signature.parameters.items():
        # If the parameter has a type annotation, grab it; otherwise use "string" as default
        annotated_type = type_hints.get(param_name, str)

        # Derive a required flag by checking if the parameter has a default
        required = param.default == inspect.Parameter.empty

        # Use the parameter’s name, the string version of the annotated type, etc.
        parameters_list.append(
            Parameter(
                name=param_name,
                type=annotated_type.__name__,
                description=f"Parameter for {param_name}",
                required=required,
            )
        )

    # Dynamically create the subclass of ToolBase
    @ComponentBase.register_type(ToolBase, func_name)
    class FunctionTool(ToolBase):
        version: str = "1.0.0"
        parameters: List[Parameter] = Field(default_factory=lambda: parameters_list)
        name: str = func_name
        description: str = docstring
        # The tool type is set to be the same as the function name
        type: str = func_name

        def __call__(self, *args, **kwargs) -> Any:
            """
            Invoke the underlying function with the provided arguments.
            """
            return func(*args, **kwargs)

    # Return an *instance* of this generated class (or the class itself)
    return FunctionTool()
