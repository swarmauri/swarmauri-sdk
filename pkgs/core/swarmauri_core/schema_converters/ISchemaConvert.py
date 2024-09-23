from abc import ABC, abstractmethod
from typing import Any, Dict
from swarmauri_core.tools.ITool import ITool

class ISchemaConvert(ABC):

    @abstractmethod
    def convert(self, tool: ITool) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement the convert method.")
