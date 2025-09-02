from __future__ import annotations
import pytest

from autoapi.v3.system.diagnostics import _build_planz_endpoint

from .response_utils import build_alias_model


@pytest.mark.asyncio
async def test_response_atoms_in_diagnostics_planz(tmp_path):
    Widget = build_alias_model(tmp_path)

    class API:  # pragma: no cover - simple container
        pass

    api = API()
    api.models = {"Widget": Widget}

    planz = _build_planz_endpoint(api)
    data = await planz()
    for op in ("json", "html", "text", "file", "stream", "redirect"):
        assert "atom:response:template@out:dump" in data["Widget"][op]
        assert "atom:response:negotiate@out:dump" in data["Widget"][op]
        assert "atom:response:render@out:dump" in data["Widget"][op]
