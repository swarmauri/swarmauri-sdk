from types import SimpleNamespace

from tigrbl.runtime.kernel.opview_compiler import compile_opview_from_specs


def test_compile_opview_from_specs_builds_sorted_io_fields() -> None:
    specs = {
        "zeta": SimpleNamespace(
            io=SimpleNamespace(in_verbs=("create",), out_verbs=("read",)),
            field=SimpleNamespace(py_type=str, required_in=("create",), constraints={}),
            storage=SimpleNamespace(nullable=False),
            default_factory=None,
        ),
        "alpha": SimpleNamespace(
            io=SimpleNamespace(in_verbs=("create",), out_verbs=()),
            field=SimpleNamespace(py_type=int, required_in=(), constraints={}),
            storage=None,
            default_factory=lambda: 1,
        ),
    }

    opview = compile_opview_from_specs(specs, SimpleNamespace(alias="create"))

    assert opview.schema_in.fields == ("alpha", "zeta")
    assert opview.schema_in.by_field["alpha"]["virtual"] is True
    assert opview.schema_in.by_field["zeta"]["required"] is True
