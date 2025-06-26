import tempfile
from pathlib import Path
import pytest


from peagen.core import keys_core


class DummyDriver:
    def __init__(self, key_dir: Path, passphrase: str | None = None) -> None:
        self.key_dir = key_dir
        self.passphrase = passphrase
        self.priv_path = key_dir / "private.asc"
        self.pub_path = key_dir / "public.asc"
        self.priv_path.write_text("priv")
        self.pub_path.write_text("pub")

    def _ensure_keys(self) -> None:
        pass

    def list_keys(self) -> dict[str, str]:
        return {"FP": str(self.pub_path)}

    def export_public_key(self, fingerprint: str, fmt: str = "armor") -> str:
        assert fingerprint == "FP"
        return "KEY"

    def add_key(
        self,
        public_key: Path,
        *,
        private_key: Path | None = None,
        name: str | None = None,
    ) -> dict:
        return {"fingerprint": "FP", "path": str(self.key_dir)}


class DummyPM:
    def __init__(self, _cfg: dict) -> None:
        self.called = False

    def get(self, group: str, name: str | None = None):
        assert group == "secrets_drivers"
        self.called = True
        return DummyDriver(Path(tempfile.mkdtemp()))


def test_create_keypair_uses_plugin_manager(monkeypatch):
    monkeypatch.setattr(keys_core, "load_peagen_toml", lambda *a, **k: {})
    pm = DummyPM({})
    monkeypatch.setattr(keys_core, "PluginManager", lambda cfg: pm)
    out = keys_core.create_keypair()
    assert pm.called
    assert out["private"].endswith("private.asc")
    assert out["public"].endswith("public.asc")


def test_export_public_key_delegates(monkeypatch, tmp_path):
    monkeypatch.setattr(keys_core, "load_peagen_toml", lambda *a, **k: {})

    class PM(DummyPM):
        def get(self, group: str, name: str | None = None):
            return DummyDriver(tmp_path)

    monkeypatch.setattr(keys_core, "PluginManager", PM)
    text = keys_core.export_public_key("FP", key_dir=tmp_path)
    assert text == "KEY"


@pytest.mark.unit
def test_upload_and_remove_key(monkeypatch, tmp_path):
    monkeypatch.setattr(keys_core, "_get_driver", lambda *a, **k: DummyDriver(tmp_path))
    posted = {}

    def fake_post(url, json, timeout):
        posted.update(json=json)

        class R:
            def json(self):
                return {}

        return R()

    monkeypatch.setattr(keys_core, "httpx", type("X", (), {"post": fake_post}))

    keys_core.upload_public_key(key_dir=tmp_path, tenant_id="t")
    assert posted["json"]["params"]["tenant_id"] == "t"
    keys_core.remove_public_key("FP", tenant_id="t")
    assert posted["json"]["method"] == "Keys.delete"
