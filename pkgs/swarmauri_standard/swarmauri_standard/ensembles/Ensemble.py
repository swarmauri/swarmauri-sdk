from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.ensembles.EnsembleBase import EnsembleBase


@ComponentBase.register_type(EnsembleBase, "Ensemble")
class Ensemble(EnsembleBase):
    """Generic ensemble for routing prompts across providers."""

    type: Literal["Ensemble"] = "Ensemble"
