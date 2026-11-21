"""Build candidate wheels and test each package in a separate environment."""

import json
from pathlib import Path
import subprocess
import sys

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

MEMBERS = (
    "transport_httpx",
    "execution_default",
    "taskmanager_default",
    "taskstore_sqlite",
    "permission_explicit",
    "delegation_attenuating",
    "grantstore_sqlite",
    "invoker_default",
    "workflow_documentassistant",
    "workflow_delegatedresearch",
)


def run(*args, **kwargs):
    subprocess.run([str(arg) for arg in args], check=True, **kwargs)


def main():
    root = Path(__file__).resolve().parents[1]
    output = (
        root / ".venv-compat" / f"{sys.version_info.major}.{sys.version_info.minor}"
    )
    wheels = output / "dist"
    wheels.mkdir(parents=True, exist_ok=True)
    constraints = output / "constraints.txt"
    constraints.write_text(
        "swarmauri_core==0.11.0.dev8\n"
        "swarmauri_base==0.11.0.dev13\n"
        "swarmauri_standard==0.11.0.dev13\n"
        "swarmauri_agent_runner==0.1.2\n"
        "swarmauri_workflow_statedriven==0.11.0.dev3\n"
        "swarmauri_tokens_jwt==0.11.0.dev3\n",
        encoding="utf-8",
    )
    for member in MEMBERS:
        path = root / "pkgs" / "standards" / f"swarmauri_{member}"
        run("uv", "build", "--directory", path, "--wheel", "--out-dir", wheels)
    for member in MEMBERS:
        name = f"swarmauri_{member}"
        path = root / "pkgs" / "standards" / name
        with (path / "pyproject.toml").open("rb") as stream:
            metadata = tomllib.load(stream)
        environment = output / name
        run("uv", "venv", environment, "--python", sys.executable)
        binaries = environment / ("Scripts" if sys.platform == "win32" else "bin")
        python = binaries / ("python.exe" if sys.platform == "win32" else "python")
        run(
            "uv",
            "pip",
            "install",
            "--python",
            python,
            "--prerelease",
            "allow",
            "--find-links",
            wheels,
            "--constraint",
            constraints,
            f"{name}=={metadata['project']['version']}",
            *metadata.get("dependency-groups", {}).get("dev", []),
        )
        run("uv", "pip", "check", "--python", python)
        run(
            python,
            "-I",
            "-c",
            f"import {name},sys; from pathlib import Path; "
            f"assert Path({name}.__file__).is_relative_to(Path(sys.prefix))",
        )
        run(
            python,
            "-I",
            "-m",
            "pytest",
            "--import-mode=importlib",
            "-c",
            path / "pyproject.toml",
            "-q",
            path / "tests",
            cwd=output,
        )
        if member.startswith("workflow_"):
            command = "swarmauri-" + member.replace("_", "-")
            if sys.platform == "win32":
                command += ".exe"
            result = subprocess.check_output([str(binaries / command)], text=True)
            result = json.loads(result)
            assert result["execution"]["status"] == "completed"
            if member == "workflow_delegatedresearch":
                assert [entry["remaining_depth"] for entry in result["trace"]] == [
                    2,
                    1,
                    0,
                ]


if __name__ == "__main__":
    main()
