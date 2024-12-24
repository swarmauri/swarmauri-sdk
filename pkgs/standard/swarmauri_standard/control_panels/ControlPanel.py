from typing import Literal
from swarmauri_base.control_panels.ControlPanelBase import ControlPanelBase


class ControlPanel(ControlPanelBase):
    """
    Concrete implementation of the ControlPanelBase.
    """

    type: Literal["ControlPanel"] = "ControlPanel"
