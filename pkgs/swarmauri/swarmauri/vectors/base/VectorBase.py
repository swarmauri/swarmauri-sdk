from abc import ABC
from typing import Union, Callable, List, Tuple, Dict, Any, Optional, Literal
import numpy as np
from pydantic import BaseModel, Field
from swarmauri_core.vectors.IVector import IVector
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes

VectorValue = Union[
    float,                          # Real numbers
    int,                            # Integers
    complex,                        # Complex numbers
    Callable[[float], float],       # Functions (e.g., continuous representations)
    np.ndarray,                     # NumPy arrays
    List[float],                    # Lists of floats
    List[int],                      # Lists of integers
    Tuple[float, ...],              # Tuples of floats
    Dict[Any, float],               # Sparse representations
    str,                            # Optional: for categorical vectors
]


class VectorBase(ComponentBase, BaseModel):
    value: VectorValue
    domain: Optional[Tuple[float, float]] = None
    num_samples: int = 100
    resource: Optional[str] = Field(default=ResourceTypes.VECTOR.value, frozen=True)
    type: Literal['VectorBase'] = 'VectorBase'

    def __init__(self, **kwargs):
        """
        Custom initialization to process `value` into the internal representation
        while leveraging Pydantic for validation and management of attributes.
        """
        # Extract `value` from kwargs for special processing
        value = kwargs.get('value')
        domain = kwargs.get('domain', None)
        num_samples = kwargs.get('num_samples', 100)

        # Process the value using `_process_value` to ensure a consistent format
        processed_value = self._process_value(value, domain, num_samples)
        kwargs['value'] = processed_value  # Update kwargs with processed value

        # Call the parent __init__ to handle validation and other attributes
        super().__init__(**kwargs)

    def _process_value(self, value: VectorValue, domain: Optional[Tuple[float, float]], num_samples: int) -> np.ndarray:
        """
        Processes the input value into a consistent internal NumPy array format.

        Args:
            value (VectorValue): The input value to process.
            domain (Optional[Tuple[float, float]]): Domain for callable values.
            num_samples (int): Number of samples for callable values.

        Returns:
            np.ndarray: The processed vector in NumPy array format.
        """
        # Handle numbers
        if isinstance(value, (int, float, complex)):
            return np.array([value], dtype=np.float64)

        # Handle lists, tuples, or NumPy arrays
        if isinstance(value, (list, tuple, np.ndarray)):
            return np.array(value, dtype=np.float64)

        # Handle functions
        if callable(value):
            if not domain:
                raise ValueError("A domain must be specified when the value is a function.")
            start, end = domain
            sample_points = np.linspace(start, end, num_samples)
            return np.array([value(x) for x in sample_points], dtype=np.float64)

        # Handle sparse representations
        if isinstance(value, dict):
            max_index = max(value.keys())
            sparse_array = np.zeros(max_index + 1, dtype=np.float64)
            for key, val in value.items():
                sparse_array[key] = val
            return sparse_array

        # Handle unsupported types
        raise TypeError(f"Unsupported value type: {type(value)}")

    def to_numpy(self) -> np.ndarray:
        """
        Converts the vector into a numpy array.

        Returns:
            np.ndarray: The numpy array representation of the vector.
        """
        return self.value

    @property
    def shape(self):
        return self.value.shape

    def __len__(self):
        return len(self.value)

    def __add__(self, other: "VectorBase") -> "VectorBase":
        if not isinstance(other, VectorBase):
            raise TypeError("Can only add another VectorBase instance.")
        if len(self) != len(other):
            raise ValueError("Vectors must have the same length.")
        return VectorBase(value=(self.value + other.value))

    def __neg__(self) -> "VectorBase":
        return VectorBase(value=(-self.value))

    def __sub__(self, other: "VectorBase") -> "VectorBase":
        return self + (-other)

    def __mul__(self, scalar: float) -> "VectorBase":
        return VectorBase(value=(self.value * scalar))

    def __rmul__(self, scalar: float) -> "VectorBase":
        return self * scalar

    def __eq__(self, other: "VectorBase") -> bool:
        if not isinstance(other, VectorBase):
            return False
        return np.array_equal(self.value, other.value)

    @property
    def zero(self) -> "VectorBase":
        return VectorBase(value=[0.0] * len(self))

    # Axiom checks (unchanged)

    def check_closure_addition(self, other: "VectorBase") -> bool:
        try:
            result = self + other
            return isinstance(result, VectorBase)
        except Exception:
            return False

    def check_closure_scalar_multiplication(self, scalar: float) -> bool:
        try:
            result = scalar * self
            return isinstance(result, VectorBase)
        except Exception:
            return False

    def check_additive_identity(self) -> bool:
        return self + self.zero == self

    def check_additive_inverse(self) -> bool:
        return self + (-self) == self.zero

    def check_commutativity_addition(self, other: "VectorBase") -> bool:
        return self + other == other + self

    def check_distributivity_scalar_vector(self, scalar: float, other: "VectorBase") -> bool:
        return scalar * (self + other) == scalar * self + scalar * other

    def check_distributivity_scalar_scalar(self, scalar1: float, scalar2: float) -> bool:
        return (scalar1 + scalar2) * self == scalar1 * self + scalar2 * self

    def check_compatibility_scalar_multiplication(self, scalar1: float, scalar2: float) -> bool:
        return (scalar1 * scalar2) * self == scalar1 * (scalar2 * self)

    def check_scalar_multiplication_identity(self) -> bool:
        return 1 * self == self

    def check_all_axioms(self, other: "VectorBase", scalar1: float, scalar2: float) -> bool:
        return (
            self.check_closure_addition(other) and
            self.check_closure_scalar_multiplication(scalar1) and
            self.check_additive_identity() and
            self.check_additive_inverse() and
            self.check_commutativity_addition(other) and
            self.check_distributivity_scalar_vector(scalar1, other) and
            self.check_distributivity_scalar_scalar(scalar1, scalar2) and
            self.check_compatibility_scalar_multiplication(scalar1, scalar2) and
            self.check_scalar_multiplication_identity()
        )