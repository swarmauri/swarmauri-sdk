from pathlib import Path


def test_jsonrpc_transport_dispatcher_module_removed():
    dispatcher = (
        Path(__file__).resolve().parents[3]
        / "tigrbl"
        / "tigrbl"
        / "transport"
        / "jsonrpc"
        / "dispatcher.py"
    )
    assert not dispatcher.exists()
