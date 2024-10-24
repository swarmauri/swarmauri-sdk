from typing import Literal, Union
from pydantic import Field
from swarmauri.tools.base.ParameterBase import ParameterBase


class Parameter(ParameterBase):
    type: Union[Literal["string", "number", "boolean", "array", "object"], str]
