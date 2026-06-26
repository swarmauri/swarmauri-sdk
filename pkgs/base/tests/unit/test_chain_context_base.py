from swarmauri_base.chains.ChainContextBase import ChainContextBase


def test_resolve_fstring_uses_direct_context_lookup() -> None:
    context = ChainContextBase(context={"name": "Ada", "count": 3})

    assert (
        context._resolve_fstring("Hello { name }, count={count}")
        == "Hello Ada, count=3"
    )


def test_resolve_fstring_preserves_unknown_or_expression_placeholders() -> (
    None
):
    context = ChainContextBase(context={"name": "Ada"})

    assert (
        context._resolve_fstring("{missing} {name.upper()}")
        == "{missing} {name.upper()}"
    )
