"""Parse all maintained shell examples without executing their workflows."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest
from readme_standards.config import discover, load_package

ROOT = Path(__file__).resolve().parents[2]


def shell_sources():
    sources = set()
    for folder in discover(ROOT, all_packages=True):
        package = load_package(folder)
        for example in package.settings["examples"].values():
            if example.get("language") in {"bash", "sh", "shell"}:
                sources.add(package.local(example["source"]))
    return sorted(sources)


@pytest.mark.unit
@pytest.mark.parametrize(
    "source", shell_sources(), ids=lambda p: p.relative_to(ROOT).as_posix()
)
def test_maintained_shell_example_parses(source):
    git_bash = Path("C:/Program Files/Git/bin/bash.exe")
    bash = (
        str(git_bash)
        if os.name == "nt" and git_bash.is_file()
        else shutil.which("bash")
    )
    assert bash, "Bash is required to validate maintained shell examples"
    result = subprocess.run(
        [bash, "-n", source.as_posix()],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )
    assert result.returncode == 0, result.stderr
