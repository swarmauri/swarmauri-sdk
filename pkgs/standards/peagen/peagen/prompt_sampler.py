from __future__ import annotations

from importlib.resources import files
from typing import List

from jinja2 import Environment, FileSystemLoader, StrictUndefined


class PromptSampler:
    _env = Environment(
        loader=FileSystemLoader(str(files("peagen") / "templates")),
        undefined=StrictUndefined,
        autoescape=False,
    )

    @classmethod
    def build_mutate_prompt(
        cls,
        parent_src: str,
        inspirations: List[str],
        entry_sig: str,
        rules: str = "",
    ) -> str:
        tmpl = cls._env.get_template("agent_evolve.j2")
        blocks = []
        for i, src in enumerate(inspirations, 1):
            blocks.append(f"# inspiration {i}\n```python\n{src}\n```")
        return tmpl.render(
            parent_src=parent_src,
            inspirations="\n\n".join(blocks),
            entry_sig=entry_sig,
            rules=rules,
        )
