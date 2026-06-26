from __future__ import annotations

import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Literal, Sequence

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, SubclassUnion
from swarmauri_base.skills.SkillBase import SkillBase
from swarmauri_base.tools.ToolBase import ToolBase
from swarmauri_standard.tools.Parameter import Parameter


@ComponentBase.register_type(ToolBase, "SkillExecutionTool")
class SkillExecutionTool(ToolBase):
    version: str = "0.1.0"
    name: str = "SkillExecutionTool"
    description: str = (
        "Runs argv command arrays relative to a selected skill root and returns "
        "structured subprocess results."
    )
    parameters: List[Parameter] = Field(
        default_factory=lambda: [
            Parameter(
                name="skill_name",
                input_type="string",
                description="Name of the selected skill whose root should be used.",
                required=True,
            ),
            Parameter(
                name="commands",
                input_type="array",
                description="One or more commands, each represented as an argv array.",
                required=True,
            ),
            Parameter(
                name="input_text",
                input_type="string",
                description="Optional stdin text passed to each command.",
                required=False,
            ),
            Parameter(
                name="timeout",
                input_type="number",
                description="Optional per-command timeout in seconds.",
                required=False,
            ),
            Parameter(
                name="mode",
                input_type="string",
                description="Run command arrays sequentially or concurrently.",
                enum=["sequential", "concurrent"],
                required=False,
            ),
        ]
    )
    skills: List[SubclassUnion[SkillBase]] = Field(default_factory=list)
    default_timeout: float = 60.0
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["SkillExecutionTool"] = "SkillExecutionTool"

    def model_post_init(self, __context: Any) -> None:
        self.skills = [self._hydrate_skill(item) for item in self.skills]

    @staticmethod
    def _hydrate_skill(value: Any) -> Any:
        if isinstance(value, SkillBase) or not isinstance(value, dict):
            return value
        type_name = value.get("type")
        skill_registry = SkillBase._registry.get("SkillBase", {})
        skill_cls = skill_registry.get("subtypes", {}).get(type_name)
        if skill_cls is None and type_name == "SkillBase":
            skill_cls = skill_registry.get("model_cls", SkillBase)
        return skill_cls.model_validate(value) if skill_cls else value

    def __call__(
        self,
        skill_name: str,
        commands: Sequence[Sequence[str]] | Sequence[str],
        input_text: str | None = None,
        timeout: float | None = None,
        mode: Literal["sequential", "concurrent"] = "sequential",
    ) -> Dict[str, Any]:
        skill = self._get_skill(skill_name)
        root = self._skill_root(skill)
        normalized_commands = self._normalize_commands(commands)
        effective_timeout = (
            timeout if timeout is not None else self.default_timeout
        )

        if mode == "concurrent":
            with ThreadPoolExecutor(
                max_workers=len(normalized_commands) or 1
            ) as pool:
                results = list(
                    pool.map(
                        lambda argv: self._run_command(
                            argv, root, input_text, effective_timeout
                        ),
                        normalized_commands,
                    )
                )
        else:
            results = [
                self._run_command(argv, root, input_text, effective_timeout)
                for argv in normalized_commands
            ]

        return {
            "skill_name": skill.name,
            "root_path": str(root),
            "mode": mode,
            "results": results,
        }

    def _get_skill(self, skill_name: str) -> SkillBase:
        for skill in self.skills:
            if skill.name == skill_name:
                return skill
        raise ValueError(f"Unknown skill name: {skill_name}")

    @staticmethod
    def _skill_root(skill: SkillBase) -> Path:
        root_path = getattr(skill, "root_path", None)
        if not root_path:
            raise ValueError(f"Skill '{skill.name}' does not define root_path")
        root = Path(root_path).expanduser().resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"Skill root does not exist: {root}")
        return root

    @staticmethod
    def _normalize_commands(
        commands: Sequence[Sequence[str]] | Sequence[str],
    ) -> List[List[str]]:
        if isinstance(commands, str):
            raise ValueError(
                "Commands must be argv arrays, not a shell string"
            )
        if not commands:
            raise ValueError("At least one command argv array is required")
        if isinstance(commands[0], str):
            normalized = [list(commands)]  # type: ignore[list-item]
        else:
            normalized = [list(command) for command in commands]  # type: ignore[arg-type]
        for command in normalized:
            if not command or not all(
                isinstance(part, str) and part for part in command
            ):
                raise ValueError("Each command must be a non-empty argv array")
        return normalized

    @staticmethod
    def _run_command(
        argv: List[str],
        root: Path,
        input_text: str | None,
        timeout: float,
    ) -> Dict[str, Any]:
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                argv,
                cwd=root,
                input=input_text,
                capture_output=True,
                text=True,
                shell=False,
                timeout=timeout,
            )
            exit_code: int | str = completed.returncode
            stdout = completed.stdout
            stderr = completed.stderr
        except subprocess.TimeoutExpired as exc:
            exit_code = "timeout"
            stdout = exc.stdout or ""
            stderr = exc.stderr or "Process timed out"
        except Exception as exc:  # pragma: no cover - defensive fallback
            exit_code = "error"
            stdout = ""
            stderr = str(exc)
        duration_ms = int((time.perf_counter() - started) * 1000)
        return {
            "argv": argv,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration_ms": duration_ms,
        }
