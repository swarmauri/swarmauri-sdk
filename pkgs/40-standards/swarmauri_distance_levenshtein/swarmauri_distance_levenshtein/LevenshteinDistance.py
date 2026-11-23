import warnings

from swarmauri_standard.distances.LevenshteinDistance import (
    LevenshteinDistance as _StandardLevenshteinDistance,
)


class LevenshteinDistance(_StandardLevenshteinDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            (
                "LevenshteinDistance is deprecated and will be removed from "
                "the active workspace by v0.12.0."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
