import pytest

from jaml import loads, round_trip_loads

# The input JML content (as a multi-line string)
JML_INPUT = r"""
rootDir = "src"
packages = ${packages}

[f"file.{package.name}.{module.name}.source" 
  for package as %{package} in @{packages} if package.active
  for module as %{module} in @{package.modules} if module.enabled]
name = %{module.name} + ".py"
path = @{rootDir} + "/" + %{package.name} + "/" + %{name}
type = "python"
test_conf = { testFramework = "pytest", tests = %{module.tests} }

"""

# The base external context used during rendering.
BASE_CONTEXT = {
    "env": "prod",
    "packages": [
        {
            "name": "auth",
            "active": True,
            "modules": [
                {
                    "name": "login",
                    "enabled": True,
                    "isTest": True,
                    "extras": {"owner": "teamA", "secret": "xyz"},
                    "tests": ["test_v2_login", "test_v2_auth"],
                },
                {
                    "name": "signup",
                    "enabled": True,
                    "isTest": False,
                    "extras": {"owner": "teamB"},
                },
            ],
        }
    ],
}

expected_result = r"""
rootDir = "src"
packages = {
    "name": "auth",
    "active": True,
    "modules": [
        {
            "name": "login",
            "enabled": True,
            "isTest": True,
            "extras": {"owner": "teamA", "secret": "xyz"},
            "tests": ["test_v2_login", "test_v2_auth"],
        },
        {
            "name": "signup",
            "enabled": True,
            "isTest": False,
            "extras": {"owner": "teamB"},
        },
    ],
}
"""


# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0011a
def test_v2_round_trip_loads_valid():
    """
    Validate that the round_trip_loads API correctly parses the JML content into an AST.
    """
    ast = loads(JML_INPUT)
    # Assuming that the AST is a dict-like structure and should contain a 'rootDir' key.
    assert isinstance(ast, dict), "The AST should be a dictionary."
    assert "rootDir" in ast, "AST should contain 'rootDir' key."


# @pytest.mark.xfail(reason="Pending proper implementation")
@pytest.mark.spec
@pytest.mark.mep0011a
def test_context_scoped_var_resolve():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    print("\n\n[TEST DEBUG]:")
    print(data, "\n\n")
    assert data["rootDir"] == '"src"'

    resolved_config = data.resolve()
    assert resolved_config["rootDir"] == "src"

    # out = data.dumps()
    # rendered_data = data.render(out, context=BASE_CONTEXT)
    rendered_data = data.render(context=BASE_CONTEXT)
    data.dumps()

    print("\n\n\n\n[FINAL_OUT]:")
    print(rendered_data)
    assert rendered_data["rootDir"] == "src"
    assert isinstance(rendered_data["packages"], list)
