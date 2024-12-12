from typing import List, Literal, Union
from swarmauri.tools.base.ParameterBase import ParameterBase


class Parameter(ParameterBase):
    type: Union[
        Literal["string", "number", "boolean", "array", "object"],
        str,
        List[str],
    ]
