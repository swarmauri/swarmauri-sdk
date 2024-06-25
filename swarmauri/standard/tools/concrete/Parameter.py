from typing import Literal
from swarmauri.standard.tools.base.ParameterBase import ParameterBase


class Parameter(ParameterBase):
    type: Literal['Parameter'] = 'Parameter'