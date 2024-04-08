import numpy as np
from typing import List

from swarmauri.core.vectors.IVector import IVector
from swarmauri.core.vectors.IVectorProduct import IVectorProduct
from swarmauri.standard.vectors.concrete.SimpleVector import SimpleVector

class VectorProduct(IVectorProduct):
    def dot_product(self, vector_a: IVector, vector_b: IVector) -> float:
        a = np.array(vector_a.data).flatten()
        b = np.array(vector_b.data).flatten()
        return np.dot(a, b)
    
    def cross_product(self, vector_a: IVector, vector_b: IVector) -> IVector:
        if len(vector_a.data) != 3 or len(vector_b.data) != 3:
            raise ValueError("Cross product is only defined for 3-dimensional vectors")
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        cross = np.cross(a, b)
        return SimpleVector(cross.tolist())
    
    def vector_triple_product(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> IVector:
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        c = np.array(vector_c.data)
        result = np.cross(a, np.cross(b, c))
        return SimpleVector(result.tolist())
    
    def scalar_triple_product(self, vector_a: IVector, vector_b: IVector, vector_c: IVector) -> float:
        a = np.array(vector_a.data)
        b = np.array(vector_b.data)
        c = np.array(vector_c.data)
        return np.dot(a, np.cross(b, c))