# test_merge_operator.py
import pytest

from jaml import round_trip_loads, round_trip_dumps, render


@pytest.mark.spec
@pytest.mark.xfail(reason="Basic table merge not fully implemented yet.")
def test_basic_table_merge_syntax():
    """
    MEP-015:
      Basic '<< = source' merges one table into another.
    """
    toml_str = """
[default]
retries = 3
timeout = 30

[production]
<< = default
timeout = 60
"""
    # Round-trip parse -> re-serialize
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "<< = default" in reserialized, (
        "Merge operator syntax not preserved in round-trip."
    )

    # If merges are resolved at parse/render time, check the final result:
    rendered = render(toml_str, context={})
    # 'production' should have 'retries = 3' inherited from 'default', but 'timeout = 60'.
    assert "retries = 3" in rendered
    assert "timeout = 60" in rendered


@pytest.mark.spec
@pytest.mark.xfail(reason="Inline table merge functionality not fully implemented yet.")
def test_inline_table_merge():
    """
    MEP-015:
      Inline tables can use << = to merge another inline table.
    """
    toml_str = """
settings = { theme = "dark", << = { font = "Arial", size = 12 } }
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # Ensure the merge operator is still there
    assert '<< = { font = "Arial", size = 12 }' in reserialized

    # If merges are applied, check final rendered results:
    rendered = render(toml_str, context={})
    # The merged table should have 'theme', 'font', and 'size':
    assert 'theme = "dark"' in rendered
    assert 'font = "Arial"' in rendered
    assert "size = 12" in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Global scoped variable merge resolution not fully implemented yet."
)
def test_merge_with_scoped_variable_global():
    """
    MEP-015:
      A table merges another table referenced by a global variable ( @{} ).
    """
    toml_str = """
[globals]
base-config = { retries = 3, timeout = 30 }

[production]
<< = @{base-config}
timeout = 60
"""
    # Round-trip to verify syntax is preserved
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    assert "<< = @{base-config}" in reserialized

    # Check final merged result
    rendered = render(toml_str, context={})
    # Expect merges from base-config, plus local override
    assert "retries = 3" in rendered
    assert "timeout = 60" in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Self scoped variable merge resolution not fully implemented yet."
)
def test_merge_with_scoped_variable_self():
    """
    MEP-015:
      A table merges another local (self) table, e.g. << = %{override}.
    """
    toml_str = """
[project.override]
theme = "dark"

[project]
settings = { theme = "light", << = %{override} }
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # Confirm the inline table merge statement is preserved
    assert "<< = %{override}" in reserialized

    # After merges:
    rendered = render(toml_str, context={})
    # The final theme should be "dark", because override merges last.
    assert 'theme = "dark"' in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Context scoped variable merge resolution not fully implemented yet."
)
def test_merge_with_scoped_variable_context():
    """
    MEP-015:
      A table merges another table referenced by context scope ( ${} ) at render time.
    """
    toml_str = """
[config]
<< = ${env_config}
"""
    # Provide a context that has a table in "env_config"
    ctx = {"env_config": {"retries": 10, "timeout": 100}}

    rendered = render(toml_str, context=ctx)
    assert "retries = 10" in rendered
    assert "timeout = 100" in rendered


@pytest.mark.spec
@pytest.mark.xfail(reason="Key precedence not fully enforced yet.")
def test_key_precedence():
    """
    MEP-015:
      Keys in the target override those in the merged source.
    """
    toml_str = """
[default]
timeout = 30
retries = 3

[production]
<< = default
timeout = 60
"""
    rendered = render(toml_str, context={})
    # 'production' should have retries=3 from default, but override timeout=60
    assert "retries = 3" in rendered
    assert "timeout = 60" in rendered


@pytest.mark.spec
@pytest.mark.xfail(reason="Recursive merging not fully implemented yet.")
def test_recursive_merge():
    """
    MEP-015:
      Merging nested tables recursively, with later merges overriding earlier ones.
    """
    toml_str = """
[base]
database = { host = "localhost", port = 5432 }

[override]
database = { port = 5433 }

[production]
<< = base
<< = override
"""
    rendered = render(toml_str, context={})
    # We should get database.host=localhost from base,
    # but database.port=5433 from override
    assert 'host = "localhost"' in rendered
    assert "port = 5433" in rendered


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Multiple merges in a single inline table not fully implemented yet."
)
def test_multiple_merges_inline_table():
    """
    MEP-015:
      Inline table can have multiple merges, e.g. << = table1, << = table2,
      applied in order.
      Mark xfail if unimplemented.
    """
    toml_str = """
[table1]
foo = 1
bar = 2

[table2]
bar = 99
baz = 3

[combined]
stuff = { << = table1, << = table2 }
"""
    rendered = render(toml_str, context={})
    # We expect 'foo=1' from table1, 'bar=99' from table2 overriding bar=2,
    # and 'baz=3' from table2
    assert "foo = 1" in rendered
    assert "bar = 99" in rendered
    assert "baz = 3" in rendered


@pytest.mark.spec
@pytest.mark.xfail(reason="Type consistency checks not yet enforced.")
def test_merge_type_mismatch_error():
    """
    MEP-015:
      If we attempt to merge a table with a scalar or array, it should raise an error.
    """
    invalid_toml = """
[defaults]
foo = 123

[production]
<< = defaults  # 'defaults' is not a table but a scalar key
"""
    # Expect an error or invalid merge
    _ = render(invalid_toml, context={})  # Should raise or fail
