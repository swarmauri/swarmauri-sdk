from typing import List
from swarmauri.standard.vectors.base.VectorBase import VectorBase

class SimpleVector(VectorBase):
    def __init__(self, data: List[float]):
        super().__init__(data)
        