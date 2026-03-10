from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.out import REGISTRY
from tigrbl_atoms.atoms.out import masking
from tigrbl_atoms.types import Atom, EncodedCtx


def test_out_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {("out", "masking")}


def test_out_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("out", "masking")] == (masking.ANCHOR, masking.INSTANCE)


def test_out_instance_and_impl_use_atom_contract() -> None:
    assert isinstance(masking.INSTANCE, Atom)
    assert issubclass(masking.AtomImpl, Atom)
    assert masking.INSTANCE.anchor == masking.ANCHOR


def test_masking_masks_sensitive_fields_on_dict_payload() -> None:
    ctx = SimpleNamespace(
        temp={"response_payload": {"secret": "abcd1234", "public": "ok"}},
        opview=SimpleNamespace(
            schema_out=SimpleNamespace(
                fields=("secret", "public"),
                by_field={
                    "secret": {"sensitive": True, "mask_last": 2},
                    "public": {"sensitive": False},
                },
                expose=("secret", "public"),
            )
        ),
    )

    masking._run(None, ctx)

    assert ctx.temp["response_payload"]["secret"] == "••••••34"
    assert ctx.temp["response_payload"]["public"] == "ok"


def test_masking_skips_explicitly_emitted_aliases() -> None:
    ctx = SimpleNamespace(
        temp={
            "response_payload": {"token_alias": "abcd1234"},
            "emit_aliases": {
                "pre": [],
                "post": [{"alias": "token_alias"}],
                "read": [],
            },
        },
        opview=SimpleNamespace(
            schema_out=SimpleNamespace(
                fields=("token_alias",),
                by_field={"token_alias": {"sensitive": True, "mask_last": 2}},
                expose=("token_alias",),
            )
        ),
    )

    masking._run(None, ctx)

    assert ctx.temp["response_payload"]["token_alias"] == "abcd1234"


def test_masking_instance_promotes_encoded_ctx() -> None:
    ctx = EncodedCtx()
    ctx.opview = SimpleNamespace(
        schema_out=SimpleNamespace(
            fields=("secret",),
            by_field={"secret": {"sensitive": True, "mask_last": 1}},
            expose=("secret",),
        )
    )
    ctx.temp["response_payload"] = {"secret": "abc"}

    out = asyncio.run(masking.INSTANCE(None, ctx))

    assert isinstance(out, EncodedCtx)
    assert out.temp["response_payload"]["secret"] == "••c"
