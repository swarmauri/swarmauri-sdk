import pytest

try:
    from peagen.plugin_registry import discover_and_register_plugins, registry
    from peagen.core import Peagen
except Exception as exc:  # pragma: no cover - environment guard
    pytest.skip(
        f"peagen is required to locate template sets ({exc!s})",
        allow_module_level=True,
    )


@pytest.mark.unit
def test_template_set_vue_locatable(tmp_path):
    discover_and_register_plugins()
    assert "peagen_templset_vue" in registry.get("template_sets", {})

    peagen = Peagen(projects_payload_path=str(tmp_path / "dummy.yaml"))
    template_path = peagen.locate_template_set("peagen_templset_vue")
    assert template_path.is_dir()
    assert (template_path / "ptree.yaml.j2").is_file()
