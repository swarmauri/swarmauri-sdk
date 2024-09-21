import numpy as np
import pacmap  # Ensure pacmap is installed
from swarmauri.standard.tools.base.ToolBase import ToolBase
from swarmauri.standard.tools.concrete.Parameter import Parameter
from typing import List, Literal, Dict, Union

from pydantic import Field


class PaCMAPTool(ToolBase):
    """
    A tool for applying the PaCMAP method for dimensionality reduction.
    """

    version: str = "1.0.0"
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="X",
                type="object",
                description="X (np.ndarray): The high-dimensional data points to reduce.",
                required=True,
            ),
            Parameter(
                name="n_neighbors",
                type="integer",
                description="The size of local neighborhood (in terms of number of neighboring data points) used for manifold approximation.",
                required=False,
            ),
            Parameter(
                name="n_components",
                type="integer",
                description="The dimension of the space into which to embed the data.",
                required=True,
            ),
            Parameter(
                name="n_iterations",
                type="integer",
                description="The number of iterations used for optimization.",
                required=False,
            ),
        ]
    )

    name: str = "PaCMAPTool"
    description: str = "Applies PaCMAP for dimensionality reduction."
    type: Literal["PaCMAPTool"] = "PaCMAPTool"

    def __call__(self, **kwargs) -> Dict[str, Union[np.ndarray, None]]:
        """
        Applies the PaCMAP algorithm on the provided dataset.

        Parameters:
        - kwargs: Additional keyword arguments for the PaCMAP algorithm.

        Returns:
        - Dict[str, Union[np.ndarray, None]]: A dictionary containing the reduced data points.
        """
        # Set default values for any unspecified parameters
        X = kwargs.get("X")

        if X is None:
            return {"X_reduced": None}

        n_neighbors = kwargs.get("n_neighbors", 30)
        n_components = kwargs.get("n_components", 2)
        n_iterations = kwargs.get("n_iterations", 500)

        # Instantiate the PaCMAP instance with specified parameters
        embedder = pacmap.PaCMAP(
            n_neighbors=n_neighbors, n_components=n_components, num_iters=n_iterations
        )
        # Fit the model and transform the data
        X_reduced = embedder.fit_transform(X)

        return {"X_reduced": X_reduced}
