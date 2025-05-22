import logging
from typing import List, Literal, Optional, Union

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.matrices.IMatrix import IMatrix
from swarmauri_core.metrics.IMetric import IMetric, MetricInput, MetricInputCollection
from swarmauri_core.vectors.IVector import IVector

# Logger configuration
logger = logging.getLogger(__name__)


@ComponentBase.register_model()
class MetricBase(IMetric, ComponentBase):
    """
    Base class for implementing metric spaces.

    This class provides the foundation for implementing metric spaces that comply
    with the metric axioms:
    - Non-negativity: d(x,y) ≥ 0
    - Identity of indiscernibles (point separation): d(x,y) = 0 if and only if x = y
    - Symmetry: d(x,y) = d(y,x)
    - Triangle inequality: d(x,z) ≤ d(x,y) + d(y,z)

    Child classes must implement the abstract methods to define specific distance calculations.
    """

    resource: Optional[str] = ResourceTypes.METRIC.value
    type: Literal["MetricBase"] = "MetricBase"

    def distance(self, x: MetricInput, y: MetricInput) -> float:
        """
        Calculate the distance between two points.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        float
            The distance between x and y

        Raises
        ------
        ValueError
            If inputs are incompatible with the metric
        TypeError
            If input types are not supported
        NotImplementedError
            If the method is not implemented by a child class
        """
        logger.debug(f"Calculating distance between {x} and {y}")
        raise NotImplementedError(
            "The distance method must be implemented by child classes"
        )

    def distances(
        self,
        x: Union[MetricInput, MetricInputCollection],
        y: Union[MetricInput, MetricInputCollection],
    ) -> Union[List[float], IVector, IMatrix]:
        """
        Calculate distances between collections of points.

        Parameters
        ----------
        x : Union[MetricInput, MetricInputCollection]
            First collection of points
        y : Union[MetricInput, MetricInputCollection]
            Second collection of points

        Returns
        -------
        Union[List[float], IVector, IMatrix]
            Matrix or vector of distances between points in x and y

        Raises
        ------
        ValueError
            If inputs are incompatible with the metric
        TypeError
            If input types are not supported
        NotImplementedError
            If the method is not implemented by a child class
        """
        logger.debug("Calculating distances between collections")
        raise NotImplementedError(
            "The distances method must be implemented by child classes"
        )

    def check_non_negativity(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the non-negativity axiom: d(x,y) ≥ 0.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a child class
        """
        logger.debug(f"Checking non-negativity axiom for {x} and {y}")
        raise NotImplementedError(
            "The check_non_negativity method must be implemented by child classes"
        )

    def check_identity_of_indiscernibles(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the identity of indiscernibles axiom:
        d(x,y) = 0 if and only if x = y.

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a child class
        """
        logger.debug(f"Checking identity of indiscernibles axiom for {x} and {y}")
        raise NotImplementedError(
            "The check_identity_of_indiscernibles method must be implemented by child classes"
        )

    def check_symmetry(self, x: MetricInput, y: MetricInput) -> bool:
        """
        Check if the metric satisfies the symmetry axiom: d(x,y) = d(y,x).

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a child class
        """
        logger.debug(f"Checking symmetry axiom for {x} and {y}")
        raise NotImplementedError(
            "The check_symmetry method must be implemented by child classes"
        )

    def check_triangle_inequality(
        self, x: MetricInput, y: MetricInput, z: MetricInput
    ) -> bool:
        """
        Check if the metric satisfies the triangle inequality axiom:
        d(x,z) ≤ d(x,y) + d(y,z).

        Parameters
        ----------
        x : MetricInput
            First point
        y : MetricInput
            Second point
        z : MetricInput
            Third point

        Returns
        -------
        bool
            True if the axiom is satisfied, False otherwise

        Raises
        ------
        NotImplementedError
            If the method is not implemented by a child class
        """
        logger.debug(f"Checking triangle inequality axiom for {x}, {y}, and {z}")
        raise NotImplementedError(
            "The check_triangle_inequality method must be implemented by child classes"
        )
