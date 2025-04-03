import pytest
from jaml import round_trip_loads, round_trip_dumps, loads, TableNode, ArrayNode, ScalarNode

PAYLOAD = '''
[project]
name = "jaml"
version = "0.1.0.dev8"
description = "Swarmauri's Canon Jaml Handler"
authors = [{ name = "Jacob Stewart", email = "jacob@swarmauri.com" }]
'''.strip()

def test_round_trip_lists_of_tables():
    """
    Test that round_trip_loads and round_trip_dumps correctly preserve
    lists of tables, including their internal structure and multi-line formatting.
    """
    # Parse into an AST while preserving formatting, comments, etc.
    ast = round_trip_loads(PAYLOAD)
    
    # Locate the [project] section.
    project_section = next((sec for sec in ast.sections if sec.name == "project"), None)
    assert project_section is not None, "Section 'project' not found in AST."
    
    # Locate the 'authors' key.
    authors_kv = next((kv for kv in project_section.keyvalues if kv.key == "authors"), None)
    assert authors_kv is not None, "Key 'authors' not found in section 'project'."
    
    # Verify that the authors key is typed as a list.
    assert authors_kv.type_annotation == "list", "The type of 'authors' should be 'list'."
    assert isinstance(authors_kv.value, ArrayNode), "The value of 'authors' should be an ArrayNode."
    
    # There should be one table in the list.
    assert len(authors_kv.value.items) == 1, "Expected one table in the 'authors' list."
    author_table = authors_kv.value.items[0]
    assert isinstance(author_table, TableNode), "Expected each item in 'authors' to be a TableNode."
    
    # Check that the table contains the expected keys and values.
    name_kv = next((kv for kv in author_table.keyvalues if kv.key == "name"), None)
    email_kv = next((kv for kv in author_table.keyvalues if kv.key == "email"), None)
    assert name_kv is not None, "Key 'name' not found in the author table."
    assert email_kv is not None, "Key 'email' not found in the author table."
    assert name_kv.value.value == "Jacob Stewart", f"Expected author name 'Jacob Stewart', got {name_kv.value.value}."
    assert email_kv.value.value == "jacob@swarmauri.com", f"Expected author email 'jacob@swarmauri.com', got {email_kv.value.value}."

    # Additionally, verify that the unparsed text preserves the multi-line formatting.
    unparsed_text = round_trip_dumps(ast)
    authors_section_start = unparsed_text.find("authors = [")
    assert authors_section_start != -1, "Could not find 'authors = [' in unparsed text."
    # Check that there is at least one newline within the authors array portion.
    authors_array_text = unparsed_text[authors_section_start:authors_section_start+200]
    assert "\n" in authors_array_text, "The multi-line formatting of the authors list was not preserved."

def test_plain_loads_lists_of_tables():
    """
    Test that loads() correctly converts a JML payload with lists of tables
    into the expected plain Python dictionary.
    """
    plain_data = loads(PAYLOAD)
    
    # Verify that the 'project' section exists.
    assert "project" in plain_data, "Section 'project' not found in plain data."
    project_data = plain_data["project"]
    
    expected = {
        "name": "jaml",
        "version": "0.1.0.dev8",
        "description": "Swarmauri's Canon Jaml Handler",
        "authors": [
            {
                "name": "Jacob Stewart",
                "email": "jacob@swarmauri.com"
            }
        ]
    }
    assert project_data == expected, f"Expected plain data {expected}, but got {project_data}"
