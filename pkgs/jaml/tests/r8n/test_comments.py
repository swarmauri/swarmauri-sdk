import pytest
from jaml import round_trip_loads, round_trip_dumps, loads


@pytest.mark.unit
@pytest.mark.xfail(reason="Comment line support not fully implemented")
def test_comment_lines():
    # Test whole line comments
    jml = """
# This is a full line comment
[app]
# Comment before version
version = "1.0"
# Another comment
debug = true
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate content while ignoring comments
    assert data["app"]["version"] == "1.0"
    assert data["app"]["debug"] is True


@pytest.mark.unit
@pytest.mark.xfail(reason="Inline comment support not fully implemented")
def test_inline_comments():
    # Test inline comments after key-value pairs
    jml = """
[server]
host = "localhost"    # The server host
port = 8080           # Default port number

[database]
name = "main"         # Primary database
timeout = 30          # Timeout in seconds
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate data while ignoring comments
    assert data["server"]["host"] == "localhost"
    assert data["server"]["port"] == 8080
    assert data["database"]["name"] == "main"
    assert data["database"]["timeout"] == 30


@pytest.mark.unit
@pytest.mark.xfail(reason="Mixed inline comment support not fully implemented")
def test_mixed_inline_comments():
    # Test inline comments within multiline arrays and mixed with standalone comments
    jml = """
# List of file paths
files = [
    "config.toml",    # Configuration file
    "data.csv",       # Main data file
    # Backup files
    "backup.bak"      # Backup file
]

# Numeric values with comments
numbers = [
    42,        # The answer to life
    3.14,      # Approximate value of pi
    0          # Zero value
]
    """.strip()
    ast = round_trip_loads(jml)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)

    # Validate data ignoring comments
    assert data["files"] == ["config.toml", "data.csv", "backup.bak"]
    assert data["numbers"] == [42, 3.14, 0]
