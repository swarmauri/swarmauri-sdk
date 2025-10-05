import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Named parameter support in git() not fully implemented")
def test_git_named_parameters_basic():
    # Test basic usage with named parameters
    jml = """
[config]
repo = git(url = "https://github.com/user/project", branch = "master")
release = git(url = "https://github.com/user/release", tag = "v1.0")
fixed = git(url = "https://github.com/user/fix", commit = "abc123")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate structured git references
    assert data["config"]["repo"]["url"] == "https://github.com/user/project"
    assert data["config"]["repo"]["branch"] == "master"
    assert data["config"]["release"]["tag"] == "v1.0"
    assert data["config"]["fixed"]["commit"] == "abc123"


@pytest.mark.unit
@pytest.mark.xfail(reason="Embedding content from git() not fully implemented")
def test_git_named_parameters_with_embed():
    # Test embedding raw content from a git repository
    jml = """
[script]
deploy = git(url = "https://github.com/user/scripts", branch = "master").embed("deploy.sh")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate embedded content
    assert data["script"]["deploy"].startswith("#!/bin/bash")


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Mixed named parameter git() references not fully implemented"
)
def test_git_mixed_named_parameters():
    # Test mixed usage of named parameters in git()
    jml = """
[build]
source = git(url = "https://github.com/user/build", branch = "dev")
stable = git(url = "https://github.com/user/build", tag = "v2.0").embed("config.toml")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate mixed references
    assert data["build"]["source"]["branch"] == "dev"
    assert data["build"]["stable"]["tag"] == "v2.0"
    assert "App Configuration" in data["build"]["stable"]["content"]
