from typing import List, Literal, Union
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParameterBase, "Parameter")
class Parameter(ParameterBase):
    input_type: Union[
        Literal["string", "number", "boolean", "array", "object"],
        str,
        List[str],
    ]
