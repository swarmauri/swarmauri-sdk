from __future__ import annotations

from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient

from tigrbl.types import App
from tigrbl.bindings import rpc_call
from tigrbl.system.diagnostics import _build_kernelz_endpoint
from tigrbl.runtime.kernel import _default_kernel as K
from tigrbl.response import render_template

from .response_utils import build_model_for_response, build_model_for_jinja_response


# 1. REST call on an alias decorated table using HtmlResponse


def test_html_response_rest_alias_table(tmp_path):
    Widget, _ = build_model_for_response("html", tmp_path)
    app = App()
    app.include_router(Widget.rest.router)
    client = TestClient(app)
    r = client.post("/widget/download", json={})
    assert r.status_code == 200
    assert r.text == "<h1>pong</h1>"


# 1b. REST call on an alias decorated table using JinjaResponse


def test_jinja_response_rest_alias_table(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    app = App()
    app.include_router(Widget.rest.router)
    client = TestClient(app)
    r = client.post("/widget/download", json={})
    assert r.status_code == 200
    assert r.text == "<h1>World</h1>"


# 2. RPC call on an alias decorated table using HtmlResponse


@pytest.mark.asyncio
async def test_html_response_rpc_alias_table(tmp_path):
    Widget, _ = build_model_for_response("html", tmp_path)
    api = SimpleNamespace(models={"Widget": Widget})
    result = await rpc_call(api, Widget, "download", {}, db=SimpleNamespace())
    assert result["status_code"] == 200
    assert result["body"] == b"<h1>pong</h1>"


# 2b. RPC call on an alias decorated table using JinjaResponse


@pytest.mark.asyncio
async def test_jinja_response_rpc_alias_table(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    api = SimpleNamespace(models={"Widget": Widget})
    result = await rpc_call(api, Widget, "download", {}, db=SimpleNamespace())
    assert result["status_code"] == 200
    assert result["body"] == b"<h1>World</h1>"


# 4. Diagnostics kernelz state when active


@pytest.mark.asyncio
async def test_diagnostics_kernelz_active_for_jinja_response(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    api = SimpleNamespace(models={"Widget": Widget})
    kernelz = _build_kernelz_endpoint(api)
    data = await kernelz()
    assert "atom:response:template@out:dump" in data["Widget"]["download"]
    assert "atom:response:negotiate@out:dump" in data["Widget"]["download"]
    assert "atom:response:render@out:dump" in data["Widget"]["download"]


# 5. Kernel state


def test_kernel_state_for_jinja_response(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    api = SimpleNamespace(models={"Widget": Widget})
    K.ensure_primed(api)
    labels = [
        lbl.split(":", 1)[1] for lbl in K.kernelz_payload(api)["Widget"]["download"]
    ]
    assert "atom:response:template@out:dump" in labels
    assert "atom:response:negotiate@out:dump" in labels
    assert "atom:response:render@out:dump" in labels


# 6. j2 search path behavior, precedence


@pytest.mark.asyncio
async def test_jinja_search_path_precedence(tmp_path):
    pytest.importorskip("jinja2")
    dir1 = tmp_path / "a"
    dir2 = tmp_path / "b"
    dir1.mkdir()
    dir2.mkdir()
    (dir1 / "hello.html").write_text("<h1>A</h1>")
    (dir2 / "hello.html").write_text("<h1>B</h1>")
    html = await render_template(
        name="hello.html",
        context={},
        search_paths=[str(dir2), str(dir1)],
    )
    assert html == "<h1>B</h1>"
