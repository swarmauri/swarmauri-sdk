# test_conditional_table_sections.py
import pytest

from jaml import round_trip_loads, round_trip_dumps, render


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Conditional table inclusion might not be fully implemented yet."
)
def test_table_included_if_expression_is_string():
    """
    MEP-0028:
      A conditional table [~(expr)] is included if expr -> "some_table_name".
    """
    toml_str = """
[settings]
env = "production"

[~("prod_config" if ${settings.env} == "production" else None)]
db_host = "prod.database.example.com"
"""

    # 1) Load or parse the document (retaining the conditional header)
    ast = round_trip_loads(toml_str)
    # 2) Round-trip to ensure the syntax is preserved
    reserialized = round_trip_dumps(ast)
    assert (
        '[~("prod_config" if ${settings.env} == "production" else None)]'
        in reserialized
    )

    # 3) Render with a context matching the 'production' environment
    context = {"settings.env": "production"}
    rendered_str = render(reserialized, context=context)

    # We expect the table to appear under "prod_config"
    assert "prod_config" in rendered_str
    assert 'db_host = "prod.database.example.com"' in rendered_str


@pytest.mark.spec
@pytest.mark.xfail(reason="Excluding conditional tables not fully validated yet.")
def test_table_excluded_if_expression_is_none():
    """
    MEP-0028:
      A conditional table is excluded if expr -> null/None or false.
    """
    toml_str = """
[settings]
env = "development"

[~("prod_config" if ${settings.env} == "production" else None)]
db_host = "prod.database.example.com"
"""

    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # The header is still there in the text
    assert (
        '[~("prod_config" if ${settings.env} == "production" else None)]'
        in reserialized
    )

    context = {"settings.env": "development"}
    rendered_str = render(reserialized, context=context)

    # Because env != "production", the expression yields None => exclude
    assert "prod_config" not in rendered_str
    assert 'db_host = "prod.database.example.com"' not in rendered_str


@pytest.mark.spec
@pytest.mark.xfail(
    reason="Direct boolean expressions may not fully resolve to a table name."
)
def test_direct_boolean_inclusion():
    """
    MEP-0028:
      A conditional table can be declared with a direct boolean expression [~(${expr})].
      If it's true => table name is retained, if false => excluded.
    """
    toml_str = """
[env]
is_prod = true

[~(${env.is_prod})]
db_url = "https://prod-db.example.com"
"""

    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)
    # We'll see something like [~(${env.is_prod})] in the text
    assert "[~(${env.is_prod})]" in reserialized

    context = {"env.is_prod": True}
    rendered_str = render(reserialized, context=context)
    # If the expression is True, the table name is presumably the same as the original
    # or we might define a default name. The spec says "the expression must evaluate
    # to string or null/false." So if true => ???

    # We'll assume your parser names it "true".
    assert "[true]" in rendered_str
    assert 'db_url = "https://prod-db.example.com"' in rendered_str


@pytest.mark.spec
@pytest.mark.xfail(reason="Merging multiple conditionals might not be implemented.")
def test_multiple_conditionals_merging_same_name():
    """
    MEP-0028:
      If multiple conditional sections result in the same table name,
      they should be merged. Last-declared keys override earlier ones.
    """
    toml_str = """
[settings]
env = "production"

[~("config" if ${settings.env} == "production" else None)]
timeout = 30

[~("config" if ${settings.env} == "production" else None)]
timeout = 60
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)

    context = {"settings.env": "production"}
    rendered_str = render(reserialized, context=context)
    # Both conditional sections evaluate to "config", so they merge.
    # The second one sets timeout=60, overriding 30.
    assert "config" in rendered_str
    assert "timeout = 60" in rendered_str
    assert "timeout = 30" not in rendered_str


@pytest.mark.spec
@pytest.mark.xfail(reason="Ternary expressions in header might be incomplete.")
def test_ternary_style_expression():
    """
    MEP-0028:
      A user can use standard ternary syntax: "table_name" if condition else None
    """
    toml_str = """
[settings]
env = "development"

[~("dev_config" if ${settings.env} == "development" else None)]
db_host = "localhost"
"""
    ast = round_trip_loads(toml_str)
    reserialized = round_trip_dumps(ast)

    context = {"settings.env": "development"}
    rendered_str = render(reserialized, context=context)
    assert "dev_config" in rendered_str
    assert 'db_host = "localhost"' in rendered_str


@pytest.mark.xfail(
    reason="Not implemented: error if expression not a valid name or null/false"
)
@pytest.mark.spec
def test_error_if_result_not_string_or_boolean():
    """
    MEP-0028:
      If the conditional expression returns a numeric or other type
      that isn't a valid table name, null, or false => error.
    """
    invalid_toml = """
[~(123)]
key = "value"
"""
    # Expect an error at render time because 123 is not a string, null, or false
    ast = round_trip_loads(invalid_toml)
    with pytest.raises(
        Exception, match="Expression must yield a string, null, or false"
    ):
        render(round_trip_dumps(ast), context={})


@pytest.mark.xfail(
    reason="No syntax check for environment usage or disallowed load-time variables yet"
)
@pytest.mark.spec
def test_disallow_load_time_variables_in_conditional_header():
    """
    MEP-0028:
      The expression in [~(expr)] must be purely render-time (context).
      If we use a load-time variable like @{some_var}, that should be an error.
    """
    invalid_toml = """
[globals]
env = "test"

[~(@{env})]
key = "value"
"""
    # Expect an error because the spec forbids load-time references in conditional headers
    ast = round_trip_loads(invalid_toml)
    render(round_trip_dumps(ast), context={})  # Should raise an error


@pytest.mark.xfail(
    reason="Detailed syntax checks for the expression not fully implemented"
)
@pytest.mark.spec
def test_syntax_error_in_conditional_header():
    """
    MEP-0028:
      If there's a syntax error in the expression, we should get an error at render time.
    """
    invalid_toml = """
[~("config" if ${env} = "prod" else None)]
key = "value"
"""
    # Single '=' instead of '==' is a syntax error
    ast = round_trip_loads(invalid_toml)
    with pytest.raises(Exception, match="Syntax error in conditional expression"):
        render(round_trip_dumps(ast), context={"env": "prod"})
