from jaml import round_trip_loads, round_trip_dumps, loads

MULTILINE_ARRAY_JML = """
[groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24.0",
    "pytest-xdist>=3.6.1",
    "pytest-json-report>=1.5.0",
    "python-dotenv",
    "requests>=2.32.3",
    "flake8>=7.0",
    "pytest-timeout>=2.3.1",
    "ruff>=0.9.9",
    "pytest-benchmark>=4.0.0",
]
""".strip()


def test_round_trip_multiline_array_preserves_format():
    """
    Test that round_trip_loads and round_trip_dumps correctly preserve the formatting
    of a multi-line array, including newlines between items.
    """
    # Parse the JML into an AST preserving formatting, comments, etc.
    ast = round_trip_loads(MULTILINE_ARRAY_JML)
    # Unparse the AST back into a JML-formatted string
    unparsed_text = round_trip_dumps(ast)

    # Check that the unparsed output still has a multiline array.
    # We search for the section of the output containing the 'dev' key.
    dev_start = unparsed_text.find("dev = [")
    assert dev_start != -1, "Could not find 'dev = [' in unparsed text"

    # Extract the content of the array between the opening '[' and the closing ']'
    array_start = dev_start + len("dev = [")
    array_end = unparsed_text.find("]", array_start)
    assert array_end != -1, (
        "Could not find the closing ']' for the dev array in unparsed text"
    )

    array_content = unparsed_text[array_start:array_end]
    # Assert that there is at least one newline inside the array content.
    assert "\n" in array_content, (
        "Multiline array formatting (newlines) was not preserved in unparsed text"
    )


def test_plain_loads_multiline_array():
    """
    Test that loads() converts a multi-line array into the expected plain Python dict.
    """
    plain_data = loads(MULTILINE_ARRAY_JML)

    expected = {
        "groups": {
            "dev": [
                "pytest>=8.0",
                "pytest-asyncio>=0.24.0",
                "pytest-xdist>=3.6.1",
                "pytest-json-report>=1.5.0",
                "python-dotenv",
                "requests>=2.32.3",
                "flake8>=7.0",
                "pytest-timeout>=2.3.1",
                "ruff>=0.9.9",
                "pytest-benchmark>=4.0.0",
            ]
        }
    }
    assert plain_data == expected, (
        f"Expected plain data {expected}, but got {plain_data}"
    )
