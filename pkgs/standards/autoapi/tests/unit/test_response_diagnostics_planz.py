from __future__ import annotations
from types import SimpleNamespace
import pytest

from autoapi.v3.ops.types import OpSpec
from autoapi.v3.response.types import ResponseSpec
from autoapi.v3.runtime import plan as runtime_plan
from autoapi.v3.system.diagnostics import _build_planz_endpoint

from .response_utils import RESPONSE_KINDS


def handler(ctx):  # pragma: no cover - simple handler
    return None


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", RESPONSE_KINDS)
async def test_response_atom_in_diagnostics_planz(kind) -> None:
    class Model:  # pragma: no cover - simple model
        __name__ = "Model"

    Model.opspecs = SimpleNamespace(
        all=(
            OpSpec(
                alias="read",
                target="read",
                table=Model,
                persist="default",
                handler=handler,
                response=ResponseSpec(kind=kind),
            ),
        )
    )
    runtime_plan.attach_atoms_for_model(Model, {})

    class API:  # pragma: no cover - simple container
        pass

    api = API()
    api.models = {"Model": Model}

    planz = _build_planz_endpoint(api)
    data = await planz()
    assert "atom:response:template@out:dump" in data["Model"]["read"]
    assert "atom:response:negotiate@out:dump" in data["Model"]["read"]
    assert "atom:response:render@out:dump" in data["Model"]["read"]
