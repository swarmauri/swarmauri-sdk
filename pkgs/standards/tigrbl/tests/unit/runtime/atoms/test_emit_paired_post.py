from types import SimpleNamespace

from tigrbl.runtime.atoms.emit import paired_post


def test_paired_post_emits_and_scrubs() -> None:
    temp = {
        "emit_aliases": {
            "pre": [
                {
                    "field": "token",
                    "alias": "t",
                    "source": ("paired_values", "token", "raw"),
                    "meta": {},
                }
            ],
            "post": [],
            "read": [],
        },
        "paired_values": {"token": {"raw": "abc"}},
        "response_extras": {},
    }
    ctx = SimpleNamespace(persist=True, temp=temp)
    paired_post.run(None, ctx)
    assert ctx.temp["response_extras"]["t"] == "abc"
    assert "raw" not in ctx.temp["paired_values"]["token"]
    assert ctx.temp["emit_aliases"]["pre"] == []
