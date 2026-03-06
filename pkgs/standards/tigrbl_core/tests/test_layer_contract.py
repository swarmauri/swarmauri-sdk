from __future__ import annotations

from tigrbl_core._spec.response_spec import ResponseSpec, TemplateSpec
from tigrbl_core._spec.response_types import Response, Template
from tigrbl_core._spec.session_spec import SessionSpec, wrap_sessionmaker


def test_response_types_use_spec_aliases() -> None:
    assert Response is ResponseSpec
    assert Template is TemplateSpec


def test_wrap_sessionmaker_supports_wrapper_without_concrete_imports() -> None:
    class Underlying:
        pass

    class Wrapped:
        def __init__(self, inner: Underlying, spec: SessionSpec) -> None:
            self.inner = inner
            self.spec = None
            self.apply_spec(spec)

        def apply_spec(self, spec: SessionSpec) -> None:
            self.spec = spec

    spec = SessionSpec(read_only=True)

    def maker() -> Underlying:
        return Underlying()

    factory = wrap_sessionmaker(maker, spec, wrapper=Wrapped)
    wrapped = factory()
    assert isinstance(wrapped, Wrapped)
    assert isinstance(wrapped.inner, Underlying)
    assert wrapped.spec == spec
