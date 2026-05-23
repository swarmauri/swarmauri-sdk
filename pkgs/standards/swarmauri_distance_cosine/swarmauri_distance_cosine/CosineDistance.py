import warnings

from swarmauri_standard.distances.CosineDistance import CosineDistance as _StandardCosineDistance


class CosineDistance(_StandardCosineDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            "CosineDistance is deprecated and will be removed from the active workspace by v0.12.0.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
