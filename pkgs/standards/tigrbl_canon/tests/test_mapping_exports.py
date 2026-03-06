from __future__ import annotations

from tigrbl_canon import mapping


def test_mapping_exports_engine_resolver_module() -> None:
    resolver = mapping.engine_resolver
    assert resolver is not None
    assert hasattr(resolver, "resolve_provider")
    assert hasattr(resolver, "acquire")
