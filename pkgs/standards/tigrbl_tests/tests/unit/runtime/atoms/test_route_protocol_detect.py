from types import SimpleNamespace

from tigrbl.runtime.atoms.route import protocol_detect


def test_protocol_detect_uses_raw_scope_when_route_envelope_missing() -> None:
    ctx = SimpleNamespace(
        raw=SimpleNamespace(scope={"type": "http", "scheme": "https"})
    )

    protocol_detect.run(None, ctx)

    assert ctx.proto == "https.rest"
    assert ctx.temp["route"]["protocol"] == "https.rest"
