from typing import Literal
import numpy as np
from swarmauri.vectors.concrete.Vector import Vector
from swarmauri.innerproducts.base.InnerProductBase import InnerProductBase

class FourierSpaceInnerProduct(InnerProductBase):
    """
    A class representing the Fourier space inner product of two vectors.

    The Fourier space inner product computes a scalar value based on
    the Fourier coefficients of the input vectors.
    """

    type: Literal['FourierSpaceInnerProduct'] = 'FourierSpaceInnerProduct'

    def compute(self, u: Vector, v: Vector) -> float:
        """
        Compute the Fourier space inner product of two vectors.

        Args:
            u: The first vector (in real or Fourier space).
            v: The second vector (in real or Fourier space).

        Returns:
            A float representing the Fourier space inner product.

        Raises:
            ValueError: If the vectors have different dimensions.

        --

        This implementation works for 1D vectors only.
        """
        if len(u.value) != len(v.value):
            raise ValueError("Vectors must have the same dimension to compute the Fourier space inner product.")

        # Perform Fourier transform on both vectors to obtain their Fourier coefficients
        u_fft = np.fft.fft(u.value)
        v_fft = np.fft.fft(v.value)

        # Compute the inner product as the sum of the product of conjugate(u_fft) and v_fft
        inner_product = np.sum(np.conj(u_fft) * v_fft).real  # Real part of the product sum

        return inner_product
