from abc import ABC, abstractmethod
from typing import List
import json
import numpy as np
from swarmauri.core.vectors.IVector import IVector

class VectorBase(IVector, ABC):
    def __init__(self, data: List[float]):
        self._data = data

    @property
    def data(self) -> List[float]:
        """
        Returns the vector's data.
        """
        return self._data
    
    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self._data)
    
    def __repr__(self):
        return str(self.data)
    
    def __len__(self):
        return len(self.data)

    def to_dict(self) -> dict:
        """
        Converts the vector into a dictionary suitable for JSON serialization.
        This method needs to be called explicitly for conversion.
        """
        return {'data': self.data}

    def to_json(self):
        """
        Return state which can be used by both pickle and json.dumps.
        For json.dumps, this will enable automatic dictionary serialization.
        """
        def my_serializer(self):
          if isinstance(self, VectorBase):
              return self.to_dict()
          raise TypeError("Type not serializable")
          
        return json.dumps(self, default=my_serializer)