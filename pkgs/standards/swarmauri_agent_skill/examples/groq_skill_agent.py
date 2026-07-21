"""End-to-end proof that Groq can drive a Swarmauri SkillAgent.

Run with ``GROQ_API_KEY`` set. The script intentionally keeps the credential
out of source, output, and the evidence file.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

from swarmauri_agent_skill import SkillAgent
from swarmauri_llm_groq import GroqToolModel
from swarmauri_skill_local import LocalSkill


def main() -> int:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SystemExit("GROQ_API_KEY is required")

    with tempfile.TemporaryDirectory(prefix="swarmauri-groq-skill-") as raw:
        root = Path(raw) / "groq-proof"
        script = root / "scripts" / "record.py"
        script.parent.mkdir(parents=True)
        (root / "SKILL.md").write_text(
            "---\n"
            "name: groq-proof\n"
            "description: Proves that Groq can execute a loaded local skill.\n"
            "metadata:\n"
            "  triggers: [groq proof]\n"
            "---\n"
            "Use SkillExecutionTool exactly once with skill_name `groq-proof` "
            "and command argv [[the current Python executable, "
            "scripts/record.py]].\n",
            encoding="utf-8",
        )
        script.write_text(
            "from pathlib import Path\n"
            "Path('skill-proof.marker').write_text(\n"
            "    'skill-executed', encoding='utf-8')\n"
            "print('skill-executed')\n",
            encoding="utf-8",
        )

        skill = LocalSkill.from_path(root)
        assert skill.name == "groq-proof"
        assert skill.root_path == str(root.resolve())
        assert "scripts/record.py" in skill.scripts

        llm = GroqToolModel(api_key=api_key)
        llm.name = "openai/gpt-oss-20b"
        agent = SkillAgent(
            llm=llm,
            skills=[skill],
            turn_mode="multi",
            require_skill=True,
        )

        prompt = (
            "Run the groq proof skill now. Use skill_name groq-proof and run "
            f"the argv command [{sys.executable!r}, 'scripts/record.py']. "
            "Return a short confirmation after the tool result."
        )
        response = agent.exec(prompt, skill_names=["groq-proof"])
        marker = root / "skill-proof.marker"
        evidence = {
            "skill_loaded": True,
            "skill_name": skill.name,
            "skill_root": str(root.resolve()),
            "skill_script_discovered": "scripts/record.py" in skill.scripts,
            "skill_context_in_agent": "# Skill: groq-proof"
            in agent.conversation.system_context.content,
            "groq_model": agent.llm.name,
            "skill_command_executed": marker.is_file()
            and marker.read_text(encoding="utf-8") == "skill-executed",
            "groq_response_nonempty": bool(response and response.strip()),
            "response": response,
        }
        if not all(
            evidence[key]
            for key in (
                "skill_loaded",
                "skill_script_discovered",
                "skill_context_in_agent",
                "skill_command_executed",
                "groq_response_nonempty",
            )
        ):
            raise AssertionError(json.dumps(evidence, indent=2))
        print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
