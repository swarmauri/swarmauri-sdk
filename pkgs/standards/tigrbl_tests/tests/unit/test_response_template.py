from __future__ import annotations
import pytest

from tigrbl.response import render_template

pytest.importorskip("jinja2")


@pytest.mark.asyncio
async def test_render_template_j2_html(tmp_path):
    tpl = tmp_path / "hello.j2.html"
    tpl.write_text("<h1>{{ name }}</h1>")
    html = await render_template(
        name="hello.j2.html",
        context={"name": "World"},
        search_paths=[str(tmp_path)],
    )
    assert "<h1>World</h1>" in html


@pytest.mark.asyncio
async def test_render_template_html(tmp_path):
    tpl = tmp_path / "plain.html"
    tpl.write_text("<h1>{{ name }}</h1>")
    html = await render_template(
        name="plain.html",
        context={"name": "World"},
        search_paths=[str(tmp_path)],
    )
    assert "<h1>World</h1>" in html
