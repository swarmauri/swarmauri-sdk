from typing import Literal
from swarmauri_base.control_panels.ControlPanelBase import ControlPanelBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(ControlPanelBase, "ControlPanel")
class ControlPanel(ControlPanelBase):
    """
    Concrete implementation of the ControlPanelBase.
    """

    type: Literal["ControlPanel"] = "ControlPanel"
