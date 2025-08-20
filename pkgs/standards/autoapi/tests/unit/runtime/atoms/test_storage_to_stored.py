from types import SimpleNamespace

from autoapi.v3.runtime.atoms.storage import to_stored


class Col:
    def derive_from_raw(
        self, raw: str, ctx: object
    ) -> str:  # pragma: no cover - simple
        return raw.upper()


def test_to_stored_derives_from_paired_raw() -> None:
    temp = {
        "paired_values": {"token": {"raw": "abc"}},
        "persist_from_paired": {"token": {"source": ("paired_values", "token", "raw")}},
        "assembled_values": {},
    }
    ctx = SimpleNamespace(persist=True, specs={"token": Col()}, temp=temp)
    to_stored.run(None, ctx)
    assert ctx.temp["assembled_values"]["token"] == "ABC"
    assert ctx.temp["storage_log"][0]["action"] == "derived_from_paired"
