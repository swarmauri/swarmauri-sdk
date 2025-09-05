from jaml import (
    round_trip_loads,
    round_trip_load,
    round_trip_dumps,
    round_trip_dump,
    loads,
)

# Robust JML payload.
ROBUST_JML = """
[users]
name: str = "Alice"
age: int = 30
is_active: bool = true
colors: list = ["red", "green", "blue"]
profile: table = { email = "alice@example.com", role = "admin" }

[settings]
theme: str = "dark"
max_connections: int = 100
pi_value: float = 3.14159
nullable: null = null
""".strip()

# Expected plain dictionary (non round-trip) after parsing.
EXPECTED_DATA = {
    "users": {
        "name": "Alice",
        "age": 30,
        "is_active": True,
        "colors": ["red", "green", "blue"],
        "profile": {"email": "alice@example.com", "role": "admin"},
    },
    "settings": {
        "theme": "dark",
        "max_connections": 100,
        "pi_value": 3.14159,
        "nullable": None,
    },
}


def test_round_trip_loads():
    """
    Test that round_trip_loads() correctly parses a robust JML string into an AST,
    and that re-dumping the AST produces a JML string which can be reloaded into the expected data.
    """
    ast = round_trip_loads(ROBUST_JML)
    dumped_str = round_trip_dumps(ast)
    # Re-parse dumped string using our plain loader.
    data = loads(dumped_str)
    assert data == EXPECTED_DATA


def test_round_trip_load(tmp_path):
    """
    Test that round_trip_load() correctly reads a robust JML file into an AST,
    and that its round-trip dump produces a JML string that re-parses to the expected data.
    """
    file_path = tmp_path / "config.jml"
    file_path.write_text(ROBUST_JML)
    with open(file_path, "r") as fp:
        ast = round_trip_load(fp)
    dumped_str = round_trip_dumps(ast)
    data = loads(dumped_str)
    assert data == EXPECTED_DATA


def test_round_trip_dumps():
    """
    Test that round_trip_dumps() serializes a DocumentNode AST into a JML string,
    and that this string re-parsed produces the expected plain dictionary.
    """
    ast = round_trip_loads(ROBUST_JML)
    dumped_str = round_trip_dumps(ast)
    assert isinstance(dumped_str, str)
    data = loads(dumped_str)
    assert data == EXPECTED_DATA


def test_round_trip_dump(tmp_path):
    """
    Test that round_trip_dump() writes the DocumentNode AST to a file in JML format,
    and that reading this file returns data equivalent to the expected plain dictionary.
    """
    file_path = tmp_path / "output.jml"
    ast = round_trip_loads(ROBUST_JML)
    with open(file_path, "w") as fp:
        round_trip_dump(ast, fp)
    with open(file_path, "r") as fp:
        dumped_str = fp.read()
    data = loads(dumped_str)
    assert data == EXPECTED_DATA
