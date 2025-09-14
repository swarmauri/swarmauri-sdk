from __future__ import annotations
from types import SimpleNamespace
import pytest

from tigrbl.op.types import OpSpec
from tigrbl.response.types import ResponseSpec, TemplateSpec
from tigrbl.system.diagnostics import _build_kernelz_endpoint

from .response_utils import RESPONSE_KINDS


def handler(ctx):  # pragma: no cover - simple handler
    return None


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", RESPONSE_KINDS)
async def test_response_atom_in_diagnostics_kernelz(kind) -> None:
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

    class API:  # pragma: no cover - simple container
        pass

    api = API()
    api.models = {"Model": Model}

    kernelz = _build_kernelz_endpoint(api)
    data = await kernelz()
    assert "POST_RESPONSE:atom:response:template@out:dump" in data["Model"]["read"]
    assert "POST_RESPONSE:atom:response:negotiate@out:dump" in data["Model"]["read"]
    assert "POST_RESPONSE:atom:response:render@out:dump" in data["Model"]["read"]


@pytest.mark.asyncio
async def test_response_atom_in_diagnostics_kernelz_template(tmp_path) -> None:
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
                response=ResponseSpec(
                    kind="html",
                    template=TemplateSpec(
                        name="hello.html", search_paths=[str(tmp_path)]
                    ),
                ),
            ),
        )
    )

    class API:  # pragma: no cover - simple container
        pass

    api = API()
    api.models = {"Model": Model}

    kernelz = _build_kernelz_endpoint(api)
    data = await kernelz()
    assert "POST_RESPONSE:atom:response:template@out:dump" in data["Model"]["read"]
    assert "POST_RESPONSE:atom:response:negotiate@out:dump" in data["Model"]["read"]
    assert "POST_RESPONSE:atom:response:render@out:dump" in data["Model"]["read"]
