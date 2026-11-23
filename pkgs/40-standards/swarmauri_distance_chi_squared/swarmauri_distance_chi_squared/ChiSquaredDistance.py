import warnings

from swarmauri_standard.distances.ChiSquaredDistance import (
    ChiSquaredDistance as _StandardChiSquaredDistance,
)


class ChiSquaredDistance(_StandardChiSquaredDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            (
                "ChiSquaredDistance is deprecated and will be removed from "
                "the active workspace by v0.12.0."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
