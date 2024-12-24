from typing import (
    List,
    Any,
    Union,
    Optional,
    Callable,
    get_type_hints,
    get_args,
    get_origin,
)
import inspect
from functools import wraps
from pydantic import BaseModel
from swarmauri_standard.tools.Parameter import Parameter


class MethodSignatureExtractor(BaseModel):
    parameters: List[Parameter] = []
    method: Callable
    _type_mapping: dict = {
        int: "integer",
        float: "number",
        str: "string",
        bool: "boolean",
        list: "array",
        dict: "object",
        Any: "any",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.parameters = self.extract_signature_details()

    def _python_type_to_json_schema_type(self, py_type):
        if get_origin(py_type) is not None:
            origin = get_origin(py_type)
            args = get_args(py_type)

            if origin is list:
                items_type = self._python_type_to_json_schema_type(args[0])
                return {"type": "array", "items": items_type}
            elif origin is dict:
                return {"type": "object"}
            elif origin in (Union, Optional):
                if len(args) == 2 and type(None) in args:
                    non_none_type = args[0] if args[1] is type(None) else args[1]
                    return self._python_type_to_json_schema_type(non_none_type)
                return {
                    "oneOf": [
                        self._python_type_to_json_schema_type(arg) for arg in args
                    ]
                }
            return {"type": self._type_mapping.get(origin, "string")}
        else:
            return {"type": self._type_mapping.get(py_type, "string")}

    def extract_signature_details(self):
        sig = inspect.signature(self.method)
        type_hints = get_type_hints(self.method)
        parameters = sig.parameters
        details_list = []
        for param_name, param in parameters.items():
            if param_name == "self":
                continue

            param_type = type_hints.get(param_name, Any)
            param_default = (
                param.default if param.default is not inspect.Parameter.empty else None
            )
            required = param.default is inspect.Parameter.empty
            enum = None
            param_type_json_schema = self._python_type_to_json_schema_type(param_type)
            print(param_type_json_schema)

            if "oneOf" in param_type_json_schema:
                param_type_json_schema["type"] = [
                    type_["type"] for type_ in param_type_json_schema["oneOf"]
                ]

            description = f"Parameter {param_name} of type {param_type_json_schema}"

            detail = Parameter(
                name=param_name,
                type=param_type_json_schema["type"],
                description=description,
                required=required,
                enum=enum,
            )
            details_list.append(detail)

        return details_list


def extract_method_signature(func: Callable):
    """
    A decorator that extracts method signature details and attaches them to the function.

    Args:
        func (Callable): The function to extract signature details for.

    Returns:
        Callable: The original function with added signature_details attribute.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    extractor = MethodSignatureExtractor(method=func)

    wrapper.signature_details = extractor.parameters

    return wrapper
