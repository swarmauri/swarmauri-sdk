import warnings

from swarmauri_standard.distances.SorensenDiceDistance import (
    SorensenDiceDistance as _StandardSorensenDiceDistance,
)


class SorensenDiceDistance(_StandardSorensenDiceDistance):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            (
                "SorensenDiceDistance is deprecated and will be removed from "
                "the active workspace by v0.12.0."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(*args, **kwargs)
