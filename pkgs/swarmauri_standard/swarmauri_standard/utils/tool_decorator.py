import inspect
from typing import Annotated, Any, List, get_origin, get_type_hints
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
    type_hints = get_type_hints(func, include_extras=True)

    # Build the list of Parameter objects from the function signature
    parameters_list: List[Parameter] = []
    for param_name, param in signature.parameters.items():
        # If the parameter has a type annotation, grab it; otherwise use "string" as default
        annotated_type = type_hints.get(param_name, str)
        origin = get_origin(annotated_type)
        if origin is Annotated:
            input_type = "Annotated"
        else:
            input_type = getattr(annotated_type, "__name__", str(annotated_type))

        # Derive a required flag by checking if the parameter has a default
        required = param.default == inspect.Parameter.empty

        # Use the parameter's name, the string version of the annotated type, etc.
        parameters_list.append(
            Parameter(
                name=param_name,
                input_type=input_type,
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
        type: str = func_name

        def __call__(self, *args, **kwargs) -> Any:
            """
            Invoke the underlying function with the provided arguments.
            """
            return func(*args, **kwargs)

    tool_instance = FunctionTool()

    # Explicitly set the type attribute to ensure it matches the function name
    tool_instance.type = func_name

    return tool_instance
