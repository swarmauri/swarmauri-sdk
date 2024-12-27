from typing import List, Literal, Union
from swarmauri_base.tools.ParameterBase import ParameterBase


class Parameter(ParameterBase):
    type: Union[
        Literal["string", "number", "boolean", "array", "object"],
        str,
        List[str],
    ]
