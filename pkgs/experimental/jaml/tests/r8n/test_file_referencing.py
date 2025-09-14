import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Basic file inclusion not fully implemented")
def test_basic_file_reference():
    # Test including an entire TOML file
    jml = """
[config]
common = file("common.toml")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate the inclusion of the entire file content
    assert data["config"]["common"]["app_name"] == "AzzyApp"
    assert data["config"]["common"]["version"] == "1.2.3"


@pytest.mark.unit
@pytest.mark.xfail(reason="Key-specific file inclusion not fully implemented")
def test_key_specific_file_reference():
    # Test including a specific key from a TOML file
    jml = """
[database]
url = file("db.toml").url
port = file("db.toml").port
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate key-specific inclusion
    assert data["database"]["url"] == "http://localhost:5432"
    assert data["database"]["port"] == 5432


@pytest.mark.unit
@pytest.mark.xfail(reason="JSON file embedding not fully implemented")
def test_json_file_reference():
    # Test including data from a JSON file
    jml = """
[user]
profile = file("user.json", "json")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate JSON file inclusion
    assert data["user"]["profile"]["name"] == "Azzy"
    assert data["user"]["profile"]["age"] == 9


@pytest.mark.unit
@pytest.mark.xfail(reason="YAML file embedding not fully implemented")
def test_yaml_file_reference():
    # Test including data from a YAML file
    jml = """
[settings]
config = file("config.yaml", "yaml")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate YAML file inclusion
    assert data["settings"]["config"]["env"] == "production"
    assert data["settings"]["config"]["debug"] is False


@pytest.mark.unit
@pytest.mark.xfail(reason="Plain text file embedding not fully implemented")
def test_text_file_reference():
    # Test embedding plain text file content
    jml = """
[docs]
readme = file("README.md", "text")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate plain text file embedding
    assert "Welcome to AzzyApp" in data["docs"]["readme"]


@pytest.mark.unit
@pytest.mark.xfail(reason="Script file embedding not fully implemented")
def test_raw_file_embedding():
    # Test embedding a raw script file
    jml = """
[scripts]
deploy = file("deploy.sh", "embed")
    """.strip()

    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate script file embedding
    assert data["scripts"]["deploy"].startswith("#!/bin/bash")


@pytest.mark.unit
@pytest.mark.xfail(reason="Missing file error not fully implemented")
def test_missing_file():
    # Test referencing a non-existent file
    jml = """
[config]
file_path = file("nonexistent.toml")
    """.strip()

    with pytest.raises(FileNotFoundError):
        round_trip_loads(jml)


@pytest.mark.unit
@pytest.mark.xfail(reason="Circular reference detection not fully implemented")
def test_circular_file_reference():
    # Test circular file referencing
    jml = """
[config]
a = file("b.toml").b
    """.strip()

    with pytest.raises(ValueError, match="Circular reference detected"):
        round_trip_loads(jml)


@pytest.mark.unit
@pytest.mark.xfail(reason="Unsupported file format handling not fully implemented")
def test_unsupported_file_format():
    # Test embedding an unsupported file format
    jml = """
[data]
binary = file("image.png", "binary")
    """.strip()

    with pytest.raises(ValueError, match="Unsupported file format: binary"):
        round_trip_loads(jml)
