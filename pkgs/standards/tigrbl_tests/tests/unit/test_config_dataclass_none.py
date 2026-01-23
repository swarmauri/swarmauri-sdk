from dataclasses import dataclass

from tigrbl.config import resolve_cfg


def test_dataclass_none_fields_do_not_override_defaults() -> None:
    @dataclass
    class AppSpec:
        trace: dict | None = None

    cfg = resolve_cfg(appspec=AppSpec())
    assert cfg.trace == {"enabled": True}
