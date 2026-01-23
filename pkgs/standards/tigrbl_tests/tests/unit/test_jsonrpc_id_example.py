from tigrbl.transport.jsonrpc.models import RPCRequest


def test_rpc_request_id_example_changes():
    schema1 = RPCRequest.model_json_schema()
    schema2 = RPCRequest.model_json_schema()
    example1 = schema1["properties"]["id"]["examples"][0]
    example2 = schema2["properties"]["id"]["examples"][0]
    assert example1 != example2
