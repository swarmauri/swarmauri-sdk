from typing import Optional, List, Any, Literal
from pydantic import Field
from swarmauri.tools.base.ParameterBase import ParameterBase


class Parameter(ParameterBase):
    type: Literal["string", "number", "boolean", "array", "object"]

    class Config:
        use_enum_values = True
