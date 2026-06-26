import warnings

from swarmauri_standard.distances.ManhattanDistance import (
    ManhattanDistance as _StandardManhattanDistance,
)


class ManhattanDistance(_StandardManhattanDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "ManhattanDistance is deprecated and will be removed from the active workspace by v0.12.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
