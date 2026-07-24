from typing import List, Literal
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ParameterBase, "Parameter")
class Parameter(ParameterBase):
    input_type: (
        Literal["string", "number", "boolean", "array", "object"]
        | str
        | List[str]
    )
