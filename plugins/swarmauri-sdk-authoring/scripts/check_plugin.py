"""Validate the Swarmauri SDK authoring Codex plugin structure."""

from __future__ import annotations

import json
import re
from pathlib import Path


PLUGIN_NAME = "swarmauri-sdk-authoring"
SKILLS = {
    "swarmauri-add-core-interface",
    "swarmauri-add-base-class",
    "swarmauri-add-base-mixin",
    "swarmauri-add-swarmauri-standard-concrete",
    "swarmauri-add-standards-standalone",
    "swarmauri-add-community-standalone",
    "swarmauri-add-experimental-standalone",
    "swarmauri-add-plugin-package",
}
REFERENCES = {
    "repo-patterns.md",
    "registry-rules.md",
    "package-readme.md",
    "inheritance-entrypoints.md",
    "home-install.md",
}
ABSOLUTE_PATH_RE = re.compile(
    r"(?i)([a-z]:\\|" + "/" + "users" + "/" + "|" + "/" + "home" + "/" + ")"
)


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    plugin_root = Path(__file__).resolve().parents[1]
    repo_root = plugin_root.parents[1]

    manifest = _load_json(plugin_root / ".codex-plugin" / "plugin.json")
    _assert(manifest["name"] == PLUGIN_NAME, "plugin manifest name mismatch")
    _assert(manifest.get("skills") == "./skills/", "plugin skills path mismatch")
    _assert("TODO" not in json.dumps(manifest), "plugin manifest contains TODO text")

    marketplace = _load_json(repo_root / ".agents" / "plugins" / "marketplace.json")
    entries = {
        entry["name"]: entry for entry in marketplace.get("plugins", [])
    }
    _assert(PLUGIN_NAME in entries, "marketplace entry is missing")
    _assert(
        entries[PLUGIN_NAME]["source"]["path"] == f"./plugins/{PLUGIN_NAME}",
        "marketplace source path mismatch",
    )

    skill_root = plugin_root / "skills"
    for skill_name in SKILLS:
        skill_dir = skill_root / skill_name
        skill_md = skill_dir / "SKILL.md"
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        _assert(skill_md.is_file(), f"{skill_name} missing SKILL.md")
        _assert(openai_yaml.is_file(), f"{skill_name} missing agents/openai.yaml")
        skill_text = skill_md.read_text(encoding="utf-8")
        _assert(f"name: {skill_name}" in skill_text, f"{skill_name} frontmatter mismatch")
        _assert("TODO" not in skill_text, f"{skill_name} contains TODO text")

    reference_root = plugin_root / "references"
    for reference_name in REFERENCES:
        _assert((reference_root / reference_name).is_file(), f"{reference_name} missing")

    for path in plugin_root.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="ignore")
            _assert(
                ABSOLUTE_PATH_RE.search(text) is None,
                f"{path.relative_to(plugin_root)} contains an absolute local path",
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
