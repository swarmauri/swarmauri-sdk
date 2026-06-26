import warnings

from swarmauri_standard.distances.HaversineDistance import (
    HaversineDistance as _StandardHaversineDistance,
)


class HaversineDistance(_StandardHaversineDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "HaversineDistance is deprecated and will be removed from the active workspace by v0.12.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
