from jaml import loads, load, dump, dumps

# Robust JML payload used in tests
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
"""

EXPECTED_DATA = {
    "users": {
        "name": "Alice",
        "age": 30,
        "is_active": True,
        "colors": ["red", "green", "blue"],
        # For our non round-trip API, inline tables may be parsed as simple dicts.
        "profile": {"email": "alice@example.com", "role": "admin"},
    },
    "settings": {
        "theme": "dark",
        "max_connections": 100,
        "pi_value": 3.14159,
        "nullable": None,
    },
}


def test_loads():
    """
    Test that loads() correctly converts a robust JML string into a plain Python dictionary.
    """
    data = loads(ROBUST_JML)
    # Check that all sections and values match expected results.
    assert data == EXPECTED_DATA


def test_load(tmp_path):
    """
    Test that load() correctly reads from a file and produces the expected plain Python dictionary.
    """
    # Create a temporary JML file with the robust payload.
    file_path = tmp_path / "config.jml"
    file_path.write_text(ROBUST_JML)

    # Load the file using our API.
    with open(file_path, "r") as fp:
        data = load(fp)

    assert data == EXPECTED_DATA


def test_dumps():
    """
    Test that dumps() serializes a plain Python dictionary to a JML-formatted string,
    and that the output can be re-parsed to yield the original dictionary.
    """
    jml_str = dumps(EXPECTED_DATA)
    # Re-parse the dumped string and compare to the original data.
    data = loads(jml_str)
    assert data == EXPECTED_DATA


def test_dump(tmp_path):
    """
    Test that dump() writes a plain Python dictionary to a file in JML format,
    and that reading the file returns the expected dictionary.
    """
    file_path = tmp_path / "output.jml"
    with open(file_path, "w") as fp:
        dump(EXPECTED_DATA, fp)

    with open(file_path, "r") as fp:
        data = load(fp)

    assert data == EXPECTED_DATA
