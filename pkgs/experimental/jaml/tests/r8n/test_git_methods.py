import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Git .embed() method not fully implemented")
def test_git_embed_method():
    # Test using the .embed() method to include raw content
    jml = """
[scripts]
deploy = git(url = "https://github.com/user/scripts", branch = "master").embed("deploy.sh")
readme = git(url = "https://github.com/user/docs", tag = "v1.0").embed("README.md")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate embedded raw content
    assert data["scripts"]["deploy"].startswith("#!/bin/bash")
    assert "Project Documentation" in data["scripts"]["readme"]


@pytest.mark.unit
@pytest.mark.xfail(reason="Git .file() method not fully implemented")
def test_git_file_method():
    # Test using the .file() method to include structured data
    jml = """
[data]
config = git(url = "https://github.com/user/config", tag = "v1.0").file("settings.toml")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate structured file inclusion
    assert data["data"]["config"]["app_name"] == "AzzyApp"
    assert data["data"]["config"]["version"] == "1.2.3"


@pytest.mark.unit
@pytest.mark.xfail(
    reason="Git mixed .embed() and .file() methods not fully implemented"
)
def test_git_mixed_methods():
    # Test using both .embed() and .file() in the same configuration
    jml = """
[deployment]
script = git(url = "https://github.com/user/deploy", branch = "release").embed("start.sh")
config = git(url = "https://github.com/user/deploy", tag = "v2.0").file("env.toml")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate embedded script content
    assert data["deployment"]["script"].startswith("#!/bin/bash")
    assert data["deployment"]["config"]["environment"] == "production"
    assert data["deployment"]["config"]["version"] == "2.0"
