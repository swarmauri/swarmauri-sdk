import pytest
from pprint import pprint

# Suppose we have a hypothetical loads function that:
# 1) Parses the TOML/markup file,
# 2) Merges tables by namespace (dotted keys),
# 3) Returns a nested dictionary reflecting the final merged state.
# In practice, you'd import such a function from your parser/merger module.
from jaml import loads

@pytest.mark.spec
# @pytest.mark.xfail(reason="Namespace merging not yet implemented")
def test_simple_namespace_merging():
    """
    Verifies that separate sections with a shared dotted prefix are merged under the same namespace.
    """
    source = """
    [app.settings]
    debug = true

    [app.paths]
    log = "/var/log/app.log"
    """
    result = loads(source)
    # Expect nested dictionary structure:
    # { "app": {
    #     "settings": { "debug": true },
    #     "paths": { "log": "/var/log/app.log" }
    # } }
    assert "app" in result
    assert "settings" in result["app"]
    assert result["app"]["settings"]["debug"] is True
    assert "paths" in result["app"]
    assert result["app"]["paths"]["log"] == "/var/log/app.log"

@pytest.mark.spec
# @pytest.mark.xfail(reason="Conflict resolution (last key wins) not yet implemented")
def test_conflicting_keys_last_key_wins():
    """
    Tests that when two tables in the same namespace define the same key, the last one overwrites the first.
    """
    source = """
    [server]
    host = "127.0.0.1"

    [server]
    host = "localhost"
    port = 8080
    """
    result = loads(source)
    # Expect "host" to be "localhost", as the last definition wins
    # and "port" = 8080.
    assert "server" in result
    assert result["server"]["host"] == "localhost"
    assert result["server"]["port"] == 8080

@pytest.mark.spec
# @pytest.mark.xfail(reason="Nested namespaces not yet implemented or tested")
def test_nested_namespace():
    """
    Ensures multiple dotted levels are merged into nested dictionaries.
    """
    source = """
    [project.metadata]
    name = "MyApp"
    version = "1.0.0"

    [project.author]
    name = "John Doe"
    email = "john@example.com"
    """
    result = loads(source)
    # Expect:
    # { "project": {
    #   "metadata": { "name": "MyApp", "version": "1.0.0" },
    #   "author": { "name": "John Doe", "email": "john@example.com" }
    # } }
    assert "project" in result
    assert "metadata" in result["project"]
    assert result["project"]["metadata"]["name"] == "MyApp"
    assert result["project"]["metadata"]["version"] == "1.0.0"
    assert "author" in result["project"]
    assert result["project"]["author"]["name"] == "John Doe"
    assert result["project"]["author"]["email"] == "john@example.com"

@pytest.mark.spec
@pytest.mark.xfail(reason="Loading multiple files simultaneously is not supported.")
def test_merge_across_multiple_sources():
    """
    If the parser merges multiple file sources, ensure that dotted namespaces combine them.
    """
    # For demonstration, assume loads can handle multiple inputs
    source1 = """
    [database.connection]
    host = "localhost"
    port = 5432
    """
    source2 = """
    [database.credentials]
    user = "admin"

    [database.connection]
    # This doesn't overwrite the existing host or port,
    # just merges in a new key if we had one, or overwrites if it conflicts.
    """
    result = loads(source1, source2)

    # Expect final structure to contain both connection & credentials keys
    # under "database" namespace.
    assert "database" in result
    assert "connection" in result["database"]
    assert "credentials" in result["database"]
    assert result["database"]["connection"]["host"] == "localhost"
    assert result["database"]["connection"]["port"] == 5432
    assert result["database"]["credentials"]["user"] == "admin"

@pytest.mark.spec
@pytest.mark.xfail(reason="Conflict warnings or detection not yet implemented")
def test_conflicting_key_warning():
    """
    MEP-005 suggests warning the user when a key is overwritten.
    This test ensures that if such a mechanism exists, it triggers properly.
    """
    source = """
    [logging]
    level = "info"

    [logging]
    level = "debug"
    """
    # We might expect either a warning or a log message that "level" was overwritten.
    # This test example is conceptual; adjust to your actual code or log checking method.
    # For instance, if loads returns a warnings list:
    result, warnings = loads(source, enable_conflict_warnings=True)
    # Check that at least one warning about overwritten "level" is present.
    conflict_warnings = [w for w in warnings if "overwritten" in w.lower() and "level" in w]
    assert len(conflict_warnings) > 0

def test_print_namespaces_for_debug():
    """
    Optional test with no xfail – used for manual debugging or inspection.
    """
    source = """
    [service.api]
    url = "http://example.com"
    token = "abc123"

    [service]
    name = "ExampleService"
    """
    # We'll parse and just print the result.
    result = loads(source)
    pprint(result)
