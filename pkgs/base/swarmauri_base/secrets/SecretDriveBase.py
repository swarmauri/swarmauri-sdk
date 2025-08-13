"""Base class for secrets storage drivers."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import Field

from swarmauri_core.secrets.ISecretDrive import ISecretDrive
from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class SecretDriveBase(ISecretDrive, ComponentBase):
    resource: Optional[str] = Field(
        default=ResourceTypes.SECRET_DRIVE.value, frozen=True
    )
    type: Literal["SecretDriveBase"] = "SecretDriveBase"
