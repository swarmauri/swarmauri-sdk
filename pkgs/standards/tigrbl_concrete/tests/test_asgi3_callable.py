import ast
from pathlib import Path


APP_SOURCE_PATH = (
    Path(__file__).resolve().parents[1] / "tigrbl_concrete" / "_concrete" / "_app.py"
)


def _get_call_method_node() -> ast.AsyncFunctionDef:
    module = ast.parse(APP_SOURCE_PATH.read_text(encoding="utf-8"))

    for node in module.body:
        if isinstance(node, ast.ClassDef) and node.name == "App":
            for item in node.body:
                if isinstance(item, ast.AsyncFunctionDef) and item.name == "__call__":
                    return item

    msg = "App.__call__ async method not found"
    raise AssertionError(msg)


def test_app_call_signature_matches_asgi3() -> None:
    call_method = _get_call_method_node()
    arg_names = [arg.arg for arg in call_method.args.args]

    assert arg_names == ["self", "scope", "receive", "send"]


def test_app_call_wraps_envelope_with_asgi3_kind() -> None:
    call_method = _get_call_method_node()

    env_assignments = [
        node
        for node in call_method.body
        if isinstance(node, ast.Assign)
        and any(
            isinstance(target, ast.Name) and target.id == "env"
            for target in node.targets
        )
    ]
    assert env_assignments

    gw_envelope_call = env_assignments[0].value
    assert isinstance(gw_envelope_call, ast.Call)
    assert isinstance(gw_envelope_call.func, ast.Name)
    assert gw_envelope_call.func.id == "GwRawEnvelope"

    keywords = {
        kw.arg: kw.value for kw in gw_envelope_call.keywords if kw.arg is not None
    }
    kind_literal = keywords.get("kind")
    assert isinstance(kind_literal, ast.Constant)
    assert kind_literal.value == "asgi3"
