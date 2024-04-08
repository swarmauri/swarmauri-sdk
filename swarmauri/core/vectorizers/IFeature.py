from abc import ABC, abstractmethod
from typing import List, Any

class IFeature(ABC):

    @abstractmethod
    def extract_features(self) -> List[Any]:
        pass
    
