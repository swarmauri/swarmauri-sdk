import warnings

from swarmauri_standard.distances.EuclideanDistance import EuclideanDistance as _StandardEuclideanDistance


class EuclideanDistance(_StandardEuclideanDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "EuclideanDistance is deprecated and will be removed from the active workspace by v0.12.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
