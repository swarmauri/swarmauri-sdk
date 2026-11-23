import warnings

from swarmauri_standard.distances.ChebyshevDistance import (
    ChebyshevDistance as _StandardChebyshevDistance,
)


class ChebyshevDistance(_StandardChebyshevDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            (
                "ChebyshevDistance is deprecated and will be removed from the "
                "active workspace by v0.12.0."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
