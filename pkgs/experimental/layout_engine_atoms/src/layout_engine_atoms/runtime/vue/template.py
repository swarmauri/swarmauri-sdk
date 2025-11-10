from __future__ import annotations

import json
from importlib.resources import files
from typing import Iterable

TEMPLATE_NAME = "mpa_shell.html"


def _load_template() -> str:
    template_path = files("layout_engine_atoms.runtime.vue.templates") / TEMPLATE_NAME
    return template_path.read_text(encoding="utf-8")


def _indent(content: str, spaces: int) -> str:
    prefix = " " * spaces
    return "\n".join(f"{prefix}{line}" if line else "" for line in content.splitlines())


def _build_extra_styles(extra_styles: Iterable[str] | None) -> str:
    if not extra_styles:
        return ""

    tags: list[str] = []
    for entry in extra_styles:
        stripped = entry.strip()
        if not stripped:
            continue
        if stripped.startswith("<"):
            tags.append(stripped)
        else:
            tags.append(f'<link rel="stylesheet" href="{stripped}">')
    if not tags:
        return ""
    return "\n" + _indent("\n".join(tags), 4)


def _build_pre_boot_scripts(scripts: Iterable[str] | None) -> str:
    if not scripts:
        return ""
    rendered = "\n".join(scripts)
    if not rendered:
        return ""
    return _indent(rendered, 4) + "\n"


def _build_css_variables(palette: dict[str, str]) -> str:
    if not palette:
        return "        --le-accent: rgba(56, 189, 248, 0.75);"
    lines = [
        f"--le-{key.replace('_', '-')}: {value};" for key, value in palette.items()
    ]
    return _indent("\n".join(lines), 8)


_TEMPLATE_CACHE: str | None = None


def render_shell(
    *,
    title: str,
    import_map: dict[str, str],
    config_payload: dict,
    palette: dict[str, str],
    bootstrap_module: str,
    extra_styles: Iterable[str] | None = None,
    pre_boot_scripts: Iterable[str] | None = None,
) -> str:
    global _TEMPLATE_CACHE
    if _TEMPLATE_CACHE is None:
        _TEMPLATE_CACHE = _load_template()

    import_map_json = json.dumps({"imports": import_map}, indent=8)
    config_json = json.dumps(config_payload, indent=2)

    rendered = _TEMPLATE_CACHE.format(
        title=title,
        extra_style_tags=_build_extra_styles(extra_styles),
        css_variables=_build_css_variables(palette),
        import_map_json=import_map_json,
        pre_boot_scripts=_build_pre_boot_scripts(pre_boot_scripts),
        config_json=_indent(config_json, 4),
        bootstrap_module=bootstrap_module,
    )
    return rendered
