from typing import List, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase


@ComponentBase.register_type(ParameterBase, "Parameter")
class Parameter(ParameterBase):
    input_type: (
        Literal["string", "number", "boolean", "array", "object"]
        | str
        | List[str]
    )
