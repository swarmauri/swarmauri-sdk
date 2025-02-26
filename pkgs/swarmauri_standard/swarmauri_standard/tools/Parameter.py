import warnings

from typing import List, Literal, Union
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.ComponentBase import ComponentBase


warnings.warn(
    "Importing ComponentBase from swarmauri_core is deprecated and will be "
    "removed in a future version. Please use 'from swarmauri_base import "
    "ComponentBase'",
    DeprecationWarning,
    stacklevel=2,
)



@ComponentBase.register_type(ParameterBase, "Parameter")
class Parameter(ParameterBase):
    input_type: Union[
        Literal["string", "number", "boolean", "array", "object"],
        str,
        List[str],
    ]
