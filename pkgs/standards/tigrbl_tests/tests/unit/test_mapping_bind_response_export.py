from pathlib import Path


def test_mapping_bind_response_uses_responses_resolver() -> None:
    mapping_init = (
        Path(__file__).resolve().parents[3]
        / "tigrbl"
        / "tigrbl"
        / "mapping"
        / "__init__.py"
    )
    source = mapping_init.read_text(encoding="utf-8")

    assert '"bind_response"' in source
    assert (
        'import_module(".responses_resolver", __name__).resolve_response_spec' in source
    )
    assert 'import_module("..responses.bind", __name__).bind' not in source
