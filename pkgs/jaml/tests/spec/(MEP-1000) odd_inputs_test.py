import pytest

from jaml import round_trip_loads

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
extras = [k = v for k, v in %{module.extras.items} if k != "secret"]
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
[file.auth.login.source]
name = "login.py"
path = "src/auth/login.py"
type = "python"
extras = {"owner": "teamA", "secret": "xyz"}
extras = { "testFramework" = "pytest", "tests" = ["test_v2_login", "test_v2_auth"] }

[file.auth.signup.source]
name = "signup.py"
path = "src/auth/signup.py"
type = "python"
extras = { "owner" = "teamB" }
extras = { "testFramework" = "pytest", "tests" = ["test_v2_login", "test_v2_auth"] }

"""


@pytest.mark.spec
@pytest.mark.xfail(reason="Pending proper implementation")
def test_assignment_in_list_compr():
    """
    Validate that updating the 'rootDir' in the AST leads to an updated path in the rendered output.
    """
    data = round_trip_loads(JML_INPUT)
    assert data["rootDir"] == "src"

    data["rootDir"].origin = '"new_src"'
    resolved_config = data.resolve()
    assert resolved_config["rootDir"] == '"new_src"'

    data.dumps()
    rendered_data = data.render(context=BASE_CONTEXT)
    final_out = data.dumps(rendered_data)

    assert rendered_data["rootDir"] == "new_src"
    assert "src/auth" in final_out
