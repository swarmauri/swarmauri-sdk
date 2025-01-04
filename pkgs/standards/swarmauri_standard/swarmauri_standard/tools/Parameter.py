from typing import List, Literal, Union
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_core.ComponentBase import ComponentBase

@ComponentBase.register_type(ParameterBase, 'Parameter')
class Parameter(ParameterBase):
    type: Union[
        Literal["string", "number", "boolean", "array", "object"],
        str,
        List[str],
    ]
