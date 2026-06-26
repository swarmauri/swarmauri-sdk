import warnings

from swarmauri_standard.distances.SquaredEuclideanDistance import (
    SquaredEuclideanDistance as _StandardSquaredEuclideanDistance,
)


class SquaredEuclideanDistance(_StandardSquaredEuclideanDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "SquaredEuclideanDistance is deprecated and will be removed from the active workspace by v0.12.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
