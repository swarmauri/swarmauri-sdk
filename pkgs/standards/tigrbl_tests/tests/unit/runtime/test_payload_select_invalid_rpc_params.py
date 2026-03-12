from types import SimpleNamespace

from tigrbl_atoms.atoms.route import payload_select


def test_payload_select_invalid_jsonrpc_string_params_returns_invalid_rpc_error():
    ctx = SimpleNamespace(
        temp={
            "route": {
                "rpc_envelope": {
                    "jsonrpc": "2.0",
                    "method": "Widget.create",
                    "params": "not-a-mapping",
                    "id": 1,
                },
                "params": {},
            },
        }
    )

    payload_select.run(None, ctx)

    assert isinstance(ctx.temp["route"].get("payload"), dict)
    assert ctx.payload == {}
    assert ctx.temp.get("rpc_error", {}).get("code") == -32602
    assert ctx.temp["rpc_error"]["message"] == "Invalid params"
    assert ctx.temp["rpc_error"]["data"]["value_type"] == "str"
