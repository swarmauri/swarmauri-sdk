import warnings

from swarmauri_standard.distances.JaccardIndexDistance import (
    JaccardIndexDistance as _StandardJaccardIndexDistance,
)


class JaccardIndexDistance(_StandardJaccardIndexDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            (
                "JaccardIndexDistance is deprecated and will be removed from "
                "the active workspace by v0.12.0."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
