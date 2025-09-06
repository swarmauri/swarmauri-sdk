from pydantic import BaseModel

from autoapi.v3.config import resolve_cfg


class AppSpec(BaseModel):
    trace: dict | None = None


def test_pydantic_none_fields_do_not_override_defaults() -> None:
    cfg = resolve_cfg(appspec=AppSpec())
    assert cfg.trace == {"enabled": True}
