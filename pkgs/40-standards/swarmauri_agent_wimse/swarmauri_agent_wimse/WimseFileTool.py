"""Read one delegated file through the WIMSE file service."""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from pydantic import Field, PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tools.ParameterBase import ParameterBase
from swarmauri_base.tools.ToolBase import ToolBase

from .proof import Rejected, produce_wpt


@ComponentBase.register_type(ToolBase, "WimseFileTool")
class WimseFileTool(ToolBase):
    """Read the resource bound to the host's delegated transaction."""

    type: Literal["WimseFileTool"] = "WimseFileTool"
    name: str = "read_file"
    description: str = "Read the file granted for this research request."
    parameters: list[ParameterBase] = Field(
        default_factory=lambda: [
            ParameterBase(
                name="file",
                description="Name granted for this read",
                input_type="string",
                required=True,
            ),
        ]
    )
    _file: str | None = PrivateAttr(default=None)
    _read: Callable[[], str] | None = PrivateAttr(default=None)
    _content: str | None = PrivateAttr(default=None)

    @classmethod
    def for_transaction(
        cls,
        *,
        file: str,
        transaction_id: str,
        wit: str,
        token: str,
        audience: str,
        signer: object,
        key_reference: str,
        url: str,
        post_json: Callable[..., dict],
    ) -> WimseFileTool:
        """Bind host-owned proof material and transport for one request."""

        def read() -> str:
            proof = produce_wpt(
                wit,
                token,
                audience=audience,
                signer=signer,
                key_reference=key_reference,
            )
            response = post_json(url, {"file": file}, proof)
            content = response.get("content")
            if (
                response.get("file") != file
                or response.get("txn") != transaction_id
                or not isinstance(content, str)
            ):
                raise Rejected(502, "file-response-invalid")
            return content

        tool = cls()
        tool._file = file
        tool._read = read
        return tool

    @property
    def has_read(self) -> bool:
        """Report whether the delegated read succeeded."""
        return self._content is not None

    def __call__(self, file: str) -> str:
        if self._read is None:
            raise Rejected(403, "file-tool-unbound")
        if file != self._file:
            raise Rejected(403, "file-not-authorized")
        if self._content is None:
            self._content = self._read()
        return self._content
