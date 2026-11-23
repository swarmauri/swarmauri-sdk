import warnings

from swarmauri_standard.distances.CanberraDistance import (
    CanberraDistance as _StandardCanberraDistance,
)


class CanberraDistance(_StandardCanberraDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            (
                "CanberraDistance is deprecated and will be removed from the "
                "active workspace by v0.12.0."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
