from abc import ABC, abstractmethod
from typing import List, Optional, Literal
import json
import numpy as np
from pydantic import Field
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

class VectorBase(IVector, ComponentBase):
    value: List[float]
    resource: Optional[str] =  Field(default=ResourceTypes.VECTOR.value, frozen=True)
    type: Literal['VectorBase'] = 'VectorBase'

    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return np.array(self.value)

    @property
    def shape(self):
        return self.to_numpy().shape
        
    def __len__(self):
        return len(self.value)